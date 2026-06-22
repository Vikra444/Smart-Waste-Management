import os
import argparse
import logging
import random
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - TRAIN - %(levelname)s - %(message)s")
logger = logging.getLogger("Trainer")

# Suppress TF warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

try:
    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
    from tensorflow.keras.models import Model
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
except ImportError:
    logger.error("TensorFlow is not installed. Run: pip install tensorflow")
    exit(1)

# Configuration
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
CLASSES = ["Hazardous", "Non-Recyclable", "Organic", "Recyclable"]
NUM_CLASSES = len(CLASSES)

def build_model() -> Model:
    """
    Builds a MobileNetV2 based model for Transfer Learning.
    
    Returns:
        Model: Compiled Keras model with a frozen MobileNetV2 base and custom head.
    """
    logger.info("Building MobileNetV2 Base Model...")
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(*IMAGE_SIZE, 3))
    
    # Freeze the base model
    base_model.trainable = False

    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def unfreeze_last_layers(model: Model, num_layers_to_unfreeze: int = 25):
    """
    Unfreezes the last N layers of the MobileNetV2 base model in the functional network.
    
    Args:
        model (Model): Keras Model instance.
        num_layers_to_unfreeze (int): Number of base layers from the end to unfreeze.
    """
    base_model = None
    for layer in model.layers:
        if layer.__class__.__name__ in ['Functional', 'Model', 'Sequential'] or (hasattr(layer, 'layers') and not layer.name.startswith('input')):
            base_model = layer
            break
            
    if base_model is not None:
        logger.info(f"Unfreezing the last {num_layers_to_unfreeze} layers of base model: {base_model.name}")
        base_model.trainable = True
        num_layers = len(base_model.layers)
        freeze_until = max(0, num_layers - num_layers_to_unfreeze)
        for i, layer in enumerate(base_model.layers):
            if i < freeze_until:
                layer.trainable = False
            else:
                layer.trainable = True
    else:
        logger.warning("Base model sub-network not found. Applying unfreezing on top-level layers.")
        model.trainable = True
        num_layers = len(model.layers)
        freeze_until = max(0, num_layers - num_layers_to_unfreeze)
        for i, layer in enumerate(model.layers):
            if i < freeze_until:
                layer.trainable = False
            else:
                layer.trainable = True

def compute_class_weights(classes) -> dict:
    """
    Computes class weights from training labels to handle class imbalance.
    Attempts to use scikit-learn but falls back to manual numpy calculation.
    
    Args:
        classes (np.ndarray): Target class labels of the dataset.
        
    Returns:
        dict: Mapping of class index to computed sample weights.
    """
    import numpy as np
    unique_classes = np.unique(classes)
    try:
        from sklearn.utils.class_weight import compute_class_weight
        weights = compute_class_weight(
            class_weight='balanced',
            classes=unique_classes,
            y=classes
        )
        class_weights = dict(zip(unique_classes, weights))
        logger.info(f"Computed class weights (sklearn): {class_weights}")
        return class_weights
    except ImportError:
        logger.warning("scikit-learn not available. Calculating class weights manually using numpy.")
        total_samples = len(classes)
        num_classes_found = len(unique_classes)
        class_counts = np.bincount(classes)
        class_weights = {}
        for c in unique_classes:
            count = class_counts[c]
            class_weights[c] = total_samples / (num_classes_found * count) if count > 0 else 1.0
        logger.info(f"Computed class weights (manual): {class_weights}")
        return class_weights

def plot_history(history, history_fine, model_save_path: str):
    """
    Plots training loss and accuracy history across both phases.
    Requires matplotlib, skips gracefully if not installed.
    
    Args:
        history: Keras history object from Phase 1.
        history_fine: Keras history object from Phase 2 (optional).
        model_save_path (str): The output model file path.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib is not installed. Skipping training curves plotting.")
        return

    try:
        acc = list(history.history['accuracy'])
        val_acc = list(history.history['val_accuracy'])
        loss = list(history.history['loss'])
        val_loss = list(history.history['val_loss'])

        if history_fine is not None:
            acc.extend(history_fine.history['accuracy'])
            val_acc.extend(history_fine.history['val_accuracy'])
            loss.extend(history_fine.history['loss'])
            val_loss.extend(history_fine.history['val_loss'])

        epochs_range = range(1, len(acc) + 1)
        plt.figure(figsize=(12, 5))

        # Accuracy Curve
        plt.subplot(1, 2, 1)
        plt.plot(epochs_range, acc, label='Training Accuracy')
        plt.plot(epochs_range, val_acc, label='Validation Accuracy')
        if history_fine is not None:
            phase1_epochs = len(history.history['accuracy'])
            plt.axvline(x=phase1_epochs, color='grey', linestyle='--', label='Start Fine-Tuning')
        plt.legend(loc='lower right')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')

        # Loss Curve
        plt.subplot(1, 2, 2)
        plt.plot(epochs_range, loss, label='Training Loss')
        plt.plot(epochs_range, val_loss, label='Validation Loss')
        if history_fine is not None:
            phase1_epochs = len(history.history['accuracy'])
            plt.axvline(x=phase1_epochs, color='grey', linestyle='--', label='Start Fine-Tuning')
        plt.legend(loc='upper right')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')

        plot_path = os.path.splitext(model_save_path)[0] + "_history.png"
        plt.savefig(plot_path)
        plt.close()
        logger.info(f"Training history plot saved to: {plot_path}")
    except Exception as e:
        logger.warning(f"Failed to generate training curves plot: {e}")

def evaluate_test_set(model_save_path: str, test_dataset_path: str):
    """
    Evaluates the final best checkpoint model on a held-out test dataset.
    Requires scikit-learn for metric analysis, falls back to basic numpy accuracy.
    
    Args:
        model_save_path (str): Path to the saved Keras model file.
        test_dataset_path (str): Path to the test dataset folder.
    """
    import numpy as np
    logger.info(f"Loading final best model from {model_save_path} for test set evaluation...")
    try:
        model = tf.keras.models.load_model(model_save_path)
    except Exception as e:
        logger.error(f"Failed to load model from {model_save_path} for testing: {e}")
        return

    logger.info(f"Loading test dataset from: {test_dataset_path}")
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        test_dataset_path,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    expected_indices = {class_name: idx for idx, class_name in enumerate(CLASSES)}
    if test_generator.class_indices != expected_indices:
        logger.warning(
            f"Test set class indices {test_generator.class_indices} "
            f"do not align with expectation {expected_indices}."
        )

    logger.info("Evaluating predictions on test dataset...")
    predictions = model.predict(test_generator)
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_generator.classes

    try:
        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
        acc = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, target_names=CLASSES, labels=range(len(CLASSES)), zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=range(len(CLASSES)))

        logger.info("=== Test Dataset Performance ===")
        logger.info(f"Test Accuracy: {acc:.4f}")
        logger.info("Classification Report:\n" + report)
        logger.info("Confusion Matrix:\n" + str(cm))
    except ImportError:
        logger.warning("scikit-learn is not installed. Computing basic metrics using numpy.")
        correct = np.sum(y_pred == y_true)
        acc = correct / len(y_true) if len(y_true) > 0 else 0.0
        logger.info(f"Test Set Accuracy (numpy): {acc:.4f}")

def main(
    dataset_path: str,
    model_save_path: str,
    test_dataset_path: str = None,
    fine_tune_epochs: int = 5,
    skip_fine_tune: bool = False,
    seed: int = 42
):
    """
    Main training function. Sets seed, configures loaders, executes
    frozen and fine-tuning epochs, logs results, plots history,
    and runs optional test set evaluation.
    
    Args:
        dataset_path (str): Directory containing subfolders of training images.
        model_save_path (str): File destination path for the trained model.
        test_dataset_path (str, optional): Held-out test folder path. Defaults to None.
        fine_tune_epochs (int, optional): Epoch count for phase 2. Defaults to 5.
        skip_fine_tune (bool, optional): If true, bypasses phase 2. Defaults to False.
        seed (int, optional): Global seed for reproducibility. Defaults to 42.
    """
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset path '{dataset_path}' not found!")
        logger.info("Please create a 'dataset' folder with subfolders for each class: " + ", ".join(CLASSES))
        return

    # 1. Reproducibility
    random.seed(seed)
    import numpy as np
    np.random.seed(seed)
    tf.random.set_seed(seed)
    logger.info(f"Configured global random seed = {seed}")

    logger.info(f"Loading dataset from: {dataset_path}")
    
    # Data Augmentation for Training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    val_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    # 2. Class Order Validation
    expected_indices = {class_name: idx for idx, class_name in enumerate(CLASSES)}
    if train_generator.class_indices != expected_indices:
        logger.error(
            f"Class order mismatch! Expected indices {expected_indices}, "
            f"but generators constructed indices {train_generator.class_indices}. "
            "This will cause predictions in classifier.py to map to the wrong labels."
        )
        sys.exit(1)
    logger.info("Class order validated successfully.")

    # 3. Class Imbalance Handling
    class_weights = compute_class_weights(train_generator.classes)

    model = build_model()
    
    # Callbacks configuration
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    checkpoint = ModelCheckpoint(
        model_save_path, 
        monitor='val_accuracy', 
        save_best_only=True, 
        mode='max', 
        verbose=1
    )
    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    # 4. Phase 1 Training (Frozen Base)
    logger.info("Starting Phase 1 Training (Frozen Base)...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        callbacks=[checkpoint, early_stop],
        class_weight=class_weights
    )

    # Log Phase 1 final stats
    p1_best_epoch = np.argmax(history.history['val_accuracy'])
    p1_best_val_acc = history.history['val_accuracy'][p1_best_epoch]
    p1_best_val_loss = history.history['val_loss'][p1_best_epoch]
    logger.info(f"Phase 1 complete. Best Val Acc: {p1_best_val_acc:.4f}, Val Loss: {p1_best_val_loss:.4f} (Epoch {p1_best_epoch + 1})")

    # 5. Phase 2 Fine-Tuning
    history_fine = None
    if not skip_fine_tune and fine_tune_epochs > 0:
        if os.path.exists(model_save_path):
            logger.info(f"Loading best checkpoint from Phase 1 at {model_save_path} for fine-tuning...")
            try:
                model = tf.keras.models.load_model(model_save_path)
            except Exception as e:
                logger.warning(f"Could not load saved model: {e}. Continuing with current in-memory weights.")
        
        unfreeze_last_layers(model, num_layers_to_unfreeze=25)
        
        model.compile(
            optimizer=Adam(learning_rate=1e-5),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        logger.info(f"Starting Phase 2 Fine-Tuning (for {fine_tune_epochs} epochs)...")
        history_fine = model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=fine_tune_epochs,
            callbacks=[checkpoint, early_stop],
            class_weight=class_weights
        )

        # Log Phase 2 final stats
        p2_best_epoch = np.argmax(history_fine.history['val_accuracy'])
        p2_best_val_acc = history_fine.history['val_accuracy'][p2_best_epoch]
        p2_best_val_loss = history_fine.history['val_loss'][p2_best_epoch]
        logger.info(f"Phase 2 complete. Best Val Acc: {p2_best_val_acc:.4f}, Val Loss: {p2_best_val_loss:.4f} (Epoch {p2_best_epoch + 1})")

    # Load the absolute best saved model overall back into memory to ensure it is returned
    if os.path.exists(model_save_path):
        logger.info(f"Loading absolute best model from {model_save_path}...")
        try:
            model = tf.keras.models.load_model(model_save_path)
        except Exception as e:
            logger.warning(f"Could not load best model back from {model_save_path}: {e}")

    logger.info(f"Training Complete! Best model saved/loaded at {model_save_path}")

    # 6. Metrics Logging & Visualizations
    plot_history(history, history_fine, model_save_path)

    # 7. Test Set Evaluation
    if test_dataset_path:
        evaluate_test_set(model_save_path, test_dataset_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Waste Classification Model")
    parser.add_argument("--dataset", type=str, default="dataset", help="Path to the dataset folder")
    parser.add_argument("--save", type=str, default="models/waste_model.h5", help="Path to save the trained model")
    parser.add_argument("--test_dataset", type=str, default=None, help="Optional path to test dataset folder")
    parser.add_argument("--fine_tune_epochs", type=int, default=5, help="Number of fine-tuning epochs")
    parser.add_argument("--skip_fine_tune", action="store_true", help="Skip the second fine-tuning phase")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    main(
        dataset_path=args.dataset,
        model_save_path=args.save,
        test_dataset_path=args.test_dataset,
        fine_tune_epochs=args.fine_tune_epochs,
        skip_fine_tune=args.skip_fine_tune,
        seed=args.seed
    )
