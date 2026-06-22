"""
Waste image classifier for CleanCity AI.
Uses a Keras model (.h5) to classify waste images into four categories.
Designed for concurrent use in a FastAPI environment with thread-safety, 
input validation, batch prediction, and graceful TensorFlow degradation.
"""
import os
import time
import logging
import threading
from typing import List, Optional, Tuple, Union

import numpy as np
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - AI-ENGINE - %(levelname)s - %(message)s")
logger = logging.getLogger("Classifier")

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
try:
    import tensorflow as tf
except ImportError as e:
    tf = None  # type: ignore[misc, assignment]
    logger.warning(
        "TensorFlow failed to import (%s). Place `waste_model.h5` under ai_engine/models/ "
        "and install MSVC++ x64 redistributable for GPU/CPU inference.",
        e,
    )

# Configurable model path via environment variable (Requirement 3)
_DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "waste_model.h5")
MODEL_PATH = os.environ.get("WASTE_MODEL_PATH", _DEFAULT_MODEL_PATH)

# Maximum allowed image dimension to prevent memory exhaustion (Requirement 7)
_MAX_IMAGE_DIM = 4000


class WasteClassifier:
    """
    Thread-safe waste-type classifier using a trained Keras model (.h5 file).

    Classifies waste images into one of four categories:
      - Hazardous, Non-Recyclable, Organic, Recyclable

    Gracefully degrades to an 'Engine Offline' mode when TensorFlow is not
    installed or the model file is absent. Supports single and batch prediction,
    hot-reload without server restart, and input validation.

    Usage:
        classifier = WasteClassifier()
        label, confidence, guidance, latency_ms = classifier.predict(pil_image)
    """

    def __init__(self) -> None:
        self.classes = ["Hazardous", "Non-Recyclable", "Organic", "Recyclable"]
        self.guidance = {
            "Organic": "Composting (Green Bin)",
            "Recyclable": "Recycling Facility (Blue Bin)",
            "Hazardous": "Specialized Disposal (Contact Local Unit)",
            "Non-Recyclable": "Landfill Processing (Red Bin)",
            "Uncertain": "Manual Verification Required",
        }
        self._backend = "none"
        self.model = None
        # Thread lock for model loading and inference (Requirement 1)
        self._lock = threading.Lock()
        self._init_model()

    @property
    def active_backend(self) -> str:
        """Returns the currently active inference backend ('keras' or 'none')."""
        return self._backend

    def _init_model(self) -> None:
        """
        Internal method: loads the Keras model from MODEL_PATH.
        Silently skips loading if TensorFlow is unavailable or the file is missing.
        Must be called while holding self._lock, or during __init__ before the
        lock is needed (single-threaded context).
        """
        if tf is None or not os.path.exists(MODEL_PATH):
            self.model = None
            self._backend = "none"
            if not os.path.exists(MODEL_PATH):
                logger.warning(
                    "No model at %s — vision API returns offline until you add weights.",
                    MODEL_PATH,
                )
            return
        try:
            logger.info("Loading Keras model from %s", MODEL_PATH)

            class LegacyBatchNormalization(tf.keras.layers.BatchNormalization):
                def __init__(self, **kwargs):
                    kwargs.pop("renorm", None)
                    kwargs.pop("renorm_clipping", None)
                    kwargs.pop("renorm_momentum", None)
                    super().__init__(**kwargs)

            model = tf.keras.models.load_model(
                MODEL_PATH,
                custom_objects={"BatchNormalization": LegacyBatchNormalization},
                compile=False,
            )
            device = "GPU" if tf.config.list_physical_devices("GPU") else "CPU"
            logger.info("AI engine on %s", device)
            # Warm-up inference to initialise graph
            model.predict(np.zeros((1, 224, 224, 3)), verbose=0)
            self.model = model
            self._backend = "keras"
        except Exception as e:
            logger.error("Keras load failed: %s", e)
            self.model = None
            self._backend = "none"

    def reload_model(self) -> str:
        """
        Re-loads the model from disk without restarting the server.

        Thread-safe: acquires the inference lock before reloading so no
        concurrent predictions are disrupted.

        Returns:
            str: The active backend after reload ('keras' or 'none').
        """
        logger.info("Reloading model (hot-swap requested)...")
        with self._lock:
            self._init_model()
        logger.info("Model reload complete. Backend: %s", self._backend)
        return self._backend

    def _validate_and_convert(
        self, img_input: Union[Image.Image, np.ndarray]
    ) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        Validates and converts an input image to a PIL Image ready for inference.

        Args:
            img_input: A PIL Image or numpy ndarray.

        Returns:
            Tuple of (PIL Image or None, error message or None).
            If validation fails, PIL Image is None and error message is set.
        """
        # Reject None (Requirement 2)
        if img_input is None:
            return None, "Input image is None"

        # Reject unsupported types (Requirement 2)
        if not isinstance(img_input, (Image.Image, np.ndarray)):
            return None, f"Unsupported input type: {type(img_input).__name__}. Expected PIL Image or numpy array."

        # Convert numpy → PIL
        try:
            if isinstance(img_input, np.ndarray):
                pil_img = Image.fromarray(img_input).convert("RGB")
            else:
                pil_img = img_input.convert("RGB")
        except Exception as e:
            return None, f"Corrupt or invalid image data: {e}"

        # Reject oversized images to prevent memory exhaustion (Requirement 7)
        w, h = pil_img.size
        if w > _MAX_IMAGE_DIM or h > _MAX_IMAGE_DIM:
            return None, (
                f"Image dimensions ({w}x{h}) exceed maximum allowed "
                f"{_MAX_IMAGE_DIM}x{_MAX_IMAGE_DIM}px"
            )

        return pil_img, None

    def predict(
        self, img_input: Union[Image.Image, np.ndarray]
    ) -> Tuple[str, float, str, int]:
        """
        Classifies a single waste image.

        Args:
            img_input: A PIL Image or numpy ndarray in RGB format.

        Returns:
            Tuple of (label, confidence, guidance, latency_ms):
                - label (str): Predicted waste category or error/status string.
                - confidence (float): Prediction confidence in [0.0, 1.0].
                - guidance (str): Disposal guidance for the predicted label.
                - latency_ms (int): Total inference time in milliseconds.
        """
        # Input validation before acquiring the lock (Requirement 2)
        pil_img, err = self._validate_and_convert(img_input)
        if err:
            logger.warning("predict() input validation failed: %s", err)
            return "Invalid Input", 0.0, err, 0

        if self._backend != "keras" or self.model is None:
            return (
                "Engine Offline",
                0.0,
                "Add ai_engine/models/waste_model.h5 and working TensorFlow",
                0,
            )

        start = time.time()
        try:
            # Thread-safe inference (Requirement 1)
            with self._lock:
                img = pil_img.resize((224, 224))
                img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
                preds = self.model.predict(img_array, verbose=0)

            class_idx = int(np.argmax(preds))
            confidence = float(np.max(preds))
            label = "Uncertain" if confidence < 0.60 else self.classes[class_idx]
            ms = int((time.time() - start) * 1000)

            # Structured success log (Requirement 4)
            logger.info(
                "Prediction: label=%s confidence=%.2f latency=%dms",
                label,
                confidence,
                ms,
            )
            return label, confidence, self.guidance.get(label, "Manual Verification Required"), ms

        except Exception as e:
            logger.error("Inference error: %s", e)
            return "Detection Error", 0.0, "Check image format", 0

    def predict_batch(
        self, img_list: List[Union[Image.Image, np.ndarray]]
    ) -> List[Tuple[str, float, str, int]]:
        """
        Classifies a batch of waste images in a single model.predict() call.

        More efficient than calling predict() in a loop since the GPU/CPU
        processes all images in one forward pass.

        Args:
            img_list: List of PIL Images or numpy ndarrays.

        Returns:
            List of (label, confidence, guidance, latency_ms) tuples,
            one per input image. Validation failures are included as
            error tuples at the corresponding index without aborting the batch.
        """
        if not img_list:
            return []

        start = time.time()

        if self._backend != "keras" or self.model is None:
            offline_tuple = (
                "Engine Offline",
                0.0,
                "Add ai_engine/models/waste_model.h5 and working TensorFlow",
                0,
            )
            return [offline_tuple] * len(img_list)

        # Validate all inputs first, collecting valid images and their indices
        validated: List[Optional[Image.Image]] = []
        errors: List[Optional[str]] = []
        for img_input in img_list:
            pil_img, err = self._validate_and_convert(img_input)
            validated.append(pil_img)
            errors.append(err)

        # Build batch array from valid images only (skip errored ones)
        valid_indices = [i for i, e in enumerate(errors) if e is None]
        results: List[Optional[Tuple[str, float, str, int]]] = [None] * len(img_list)

        # Fill in error results immediately
        for i, err in enumerate(errors):
            if err is not None:
                logger.warning("predict_batch() input[%d] validation failed: %s", i, err)
                results[i] = ("Invalid Input", 0.0, err, 0)

        if valid_indices:
            try:
                batch_array = np.stack(
                    [
                        np.array(validated[i].resize((224, 224))) / 255.0  # type: ignore[union-attr]
                        for i in valid_indices
                    ],
                    axis=0,
                )
                with self._lock:
                    batch_preds = self.model.predict(batch_array, verbose=0)

                elapsed_ms = int((time.time() - start) * 1000)
                per_image_ms = elapsed_ms // max(len(valid_indices), 1)

                for rank, orig_idx in enumerate(valid_indices):
                    preds = batch_preds[rank]
                    class_idx = int(np.argmax(preds))
                    confidence = float(np.max(preds))
                    label = "Uncertain" if confidence < 0.60 else self.classes[class_idx]
                    guidance = self.guidance.get(label, "Manual Verification Required")
                    results[orig_idx] = (label, confidence, guidance, per_image_ms)

                logger.info(
                    "Batch prediction: %d images, total latency=%dms",
                    len(valid_indices),
                    elapsed_ms,
                )

            except Exception as e:
                logger.error("Batch inference error: %s", e)
                for i in valid_indices:
                    results[i] = ("Detection Error", 0.0, "Check image format", 0)

        return results  # type: ignore[return-value]


classifier = WasteClassifier()
