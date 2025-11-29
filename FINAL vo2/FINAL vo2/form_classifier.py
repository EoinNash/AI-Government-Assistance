"""
Florida Government Forms CNN Classifier
Extracted from Florida_Forms_AI_FIXED.ipynb
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from PIL import Image, ImageDraw, ImageFont
import io
import random

# Clear any existing TensorFlow sessions to prevent conflicts
tf.keras.backend.clear_session()


class FormClassifier:
    """CNN-based classifier for government forms"""
    
    def __init__(self):
        self.img_size = (128, 128)
        self.form_categories = [
            'drivers_license',
            'vehicle_registration', 
            'vehicle_title',
            'building_permit',
            'state_id'
        ]
        self.model = None
        
    def build_model(self):
        """Build the CNN architecture"""
        # Clear session before building to prevent graph issues
        tf.keras.backend.clear_session()
        
        model = models.Sequential([
            # Input layer
            layers.Input(shape=(128, 128, 1)),
            
            # First Conv Block - larger kernels
            layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Second Conv Block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Third Conv Block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Flatten and Dense layers
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            
            # Output layer
            layers.Dense(5, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def create_distinctive_form(self, form_type, seed=None):
        """Create synthetic form image for training"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        img = Image.new('L', self.img_size, color=255)
        draw = ImageDraw.Draw(img)
        
        # Different visual patterns for each form type
        if form_type == 'drivers_license':
            # Photo box + horizontal lines
            draw.rectangle([10, 10, 50, 50], outline=0, width=2)
            for y in range(60, 120, 10):
                draw.line([10, y, 118, y], fill=0, width=1)
                
        elif form_type == 'vehicle_registration':
            # Grid pattern
            for x in range(10, 120, 20):
                draw.line([x, 10, x, 118], fill=0, width=1)
            for y in range(10, 120, 20):
                draw.line([10, y, 118, y], fill=0, width=1)
                
        elif form_type == 'vehicle_title':
            # Large boxes with diagonal
            draw.rectangle([10, 10, 60, 60], outline=0, width=3)
            draw.rectangle([68, 10, 118, 60], outline=0, width=3)
            draw.line([10, 70, 118, 118], fill=0, width=3)
            
        elif form_type == 'building_permit':
            # Black header + vertical bars
            draw.rectangle([10, 10, 118, 30], fill=0)
            for x in range(20, 110, 15):
                draw.rectangle([x, 40, x+8, 118], fill=0)
                
        elif form_type == 'state_id':
            # Card border + circle
            draw.rectangle([15, 15, 113, 113], outline=0, width=3)
            draw.ellipse([45, 45, 83, 83], outline=0, width=2)
        
        # Add some noise for variation
        img_array = np.array(img)
        noise = np.random.normal(0, 10, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        return img_array
    
    def create_training_data(self, samples_per_category=50):
        """Generate synthetic training dataset"""
        X = []
        y = []
        
        for idx, form_type in enumerate(self.form_categories):
            for i in range(samples_per_category):
                img = self.create_distinctive_form(form_type, seed=idx*1000 + i)
                X.append(img)
                y.append(idx)
        
        X = np.array(X).reshape(-1, 128, 128, 1) / 255.0
        y = np.array(y)
        
        return X, y
    
    def quick_train(self):
        """Quick training for demo"""
        try:
            # Clear session before training
            tf.keras.backend.clear_session()
            
            # Generate minimal training data
            X, y = self.create_training_data(samples_per_category=10)
            
            # Build model if not exists
            if self.model is None:
                self.build_model()
            
            # Quick training - force CPU to avoid GPU issues
            with tf.device('/CPU:0'):
                self.model.fit(X, y, epochs=10, batch_size=16, verbose=0)
            
            return True
        except Exception as e:
            print(f"Training error: {str(e)}")
            return False
    
    def train(self, epochs=50, samples_per_category=50):
        """Train the CNN model"""
        print("📊 Generating training data...")
        X, y = self.create_training_data(samples_per_category)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        print(f"✅ Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
        
        # Build and train model
        if self.model is None:
            self.build_model()
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5
            )
        ]
        
        print("🚀 Training CNN model...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        test_loss, test_acc = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"\n✅ Test Accuracy: {test_acc*100:.2f}%")
        
        return history, (X_test, y_test)
    
    def predict_form(self, image_input):
        """
        Predict form type from image
        
        Args:
            image_input: PIL Image, numpy array, or bytes
            
        Returns:
            dict with 'form_type', 'confidence', and 'probabilities'
        """
        if self.model is None:
            raise ValueError("Model not trained! Call train() first.")
        
        # Handle different input types
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            image = Image.fromarray(image_input)
        
        # Convert to grayscale and resize
        image = image.convert('L')
        image = image.resize(self.img_size)
        
        # Normalize
        img_array = np.array(image).reshape(1, 128, 128, 1) / 255.0
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_idx]
        
        # Create probability dict
        probabilities = {
            form_type: float(prob) 
            for form_type, prob in zip(self.form_categories, predictions[0])
        }
        
        return {
            'form_type': self.form_categories[predicted_idx],
            'confidence': float(confidence),
            'probabilities': probabilities
        }
    
    def save_model(self, filepath='form_classifier_model.keras'):
        """Save trained model"""
        if self.model is None:
            raise ValueError("No model to save!")
        self.model.save(filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath='form_classifier_model.keras'):
        """Load pre-trained model"""
        self.model = keras.models.load_model(filepath)
        print(f"✅ Model loaded from {filepath}")


# Helper function for easy use
def classify_form_image(image_input, model_path='form_classifier_model.keras'):
    """
    Convenience function to classify a form image
    
    Args:
        image_input: PIL Image, numpy array, or bytes
        model_path: Path to saved model
        
    Returns:
        dict with prediction results
    """
    classifier = FormClassifier()
    classifier.load_model(model_path)
    return classifier.predict_form(image_input)
