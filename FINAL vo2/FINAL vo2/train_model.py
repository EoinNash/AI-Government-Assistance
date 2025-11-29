"""
Train the Form Classifier CNN Model
Run this script once to train and save the model
"""

from form_classifier import FormClassifier
import os

def main():
    print("=" * 60)
    print("🎓 TRAINING FLORIDA FORMS CNN CLASSIFIER")
    print("=" * 60)
    
    # Initialize classifier
    classifier = FormClassifier()
    
    # Train model
    print("\n📚 Starting training...")
    history, test_data = classifier.train(
        epochs=50,
        samples_per_category=50
    )
    
    # Save model
    model_path = 'form_classifier_model.keras'
    classifier.save_model(model_path)
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\n📦 Model saved to: {model_path}")
    print(f"📊 Model size: {os.path.getsize(model_path) / 1024:.2f} KB")
    print("\nYou can now use this model in your Streamlit app!")
    print("\nForm categories:")
    for i, category in enumerate(classifier.form_categories, 1):
        print(f"  {i}. {category}")
    
    return classifier

if __name__ == "__main__":
    main()
