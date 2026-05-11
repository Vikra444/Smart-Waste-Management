import os
import time
import logging
import numpy as np
from PIL import Image

# Suppress TensorFlow logging for a cleaner console
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

# Dynamic path to model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "waste_model.h5")

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AI-ENGINE - %(levelname)s - %(message)s')
logger = logging.getLogger("Classifier")

class WasteClassifier:
    """
    Production-grade AI Classifier for CleanCity AI.
    Handles inference, confidence thresholds, and disposal guidance.
    """
    
    def __init__(self):
        self.classes = ['Hazardous', 'Non-Recyclable', 'Organic', 'Recyclable']
        self.guidance = {
            'Organic': 'Composting (Green Bin)',
            'Recyclable': 'Recycling Facility (Blue Bin)',
            'Hazardous': 'Specialized Disposal (Contact Local Unit)',
            'Non-Recyclable': 'Landfill Processing (Red Bin)',
            'Uncertain': 'Manual Verification Required'
        }
        self.model = self._load_and_warmup()

    def _load_and_warmup(self):
        """Loads the model and performs a dummy prediction for faster real-time inference."""
        try:
            if not os.path.exists(MODEL_PATH):
                logger.error(f"AI Model not found at: {MODEL_PATH}")
                return None
            
            logger.info("Loading Neural Weights...")
            model = tf.keras.models.load_model(MODEL_PATH)
            
            # Hardware Detection
            device = "GPU" if tf.config.list_physical_devices('GPU') else "CPU"
            logger.info(f"AI Engine successfully deployed on {device}")
            
            # Warmup: Run a dummy prediction
            logger.info("Initializing AI Engine Warmup...")
            dummy_data = np.zeros((1, 224, 224, 3))
            model.predict(dummy_data, verbose=0)
            logger.info("Warmup Complete. Ready for real-time inference.")
            
            return model
        except Exception as e:
            logger.error(f"Critical AI Initialization Failure: {e}")
            return None

    def predict(self, img_input):
        """
        Performs inference on a PIL image or numpy array.
        Returns: label, confidence, guidance, and inference_time_ms.
        """
        if self.model is None:
            return "Engine Offline", 0.0, "N/A", 0
        
        start_time = time.time()
        
        try:
            # 1. Input Validation & Preprocessing
            if isinstance(img_input, Image.Image):
                img = img_input.resize((224, 224))
            else:
                img = Image.fromarray(img_input).resize((224, 224))
                
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # 2. Inference
            preds = self.model.predict(img_array, verbose=0)
            class_idx = np.argmax(preds)
            confidence = float(np.max(preds))
            
            # 3. Confidence Thresholding
            if confidence < 0.60:
                label = "Uncertain"
            else:
                label = self.classes[class_idx]
                
            end_time = time.time()
            inference_time_ms = int((end_time - start_time) * 1000)
            
            logger.info(f"Prediction: {label} ({confidence*100:.1f}%) in {inference_time_ms}ms")
            
            return label, confidence, self.guidance.get(label), inference_time_ms

        except Exception as e:
            logger.error(f"Inference Failure: {e}")
            return "Detection Error", 0.0, "Check Image Format", 0

# Singleton Instance
classifier = WasteClassifier()
