import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Configuration
CLASSES = ['driver_license', 'vehicle_registration', 'vehicle_title', 'insurance_card', 'unknown_garbage']
IMAGES_PER_CLASS = 60  # Generates 300 images total
OUTPUT_DIR = 'dataset'

def create_noisy_background():
    # Create a random colored background (simulates a table or seat)
    color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    img = Image.new('RGB', (224, 224), color=color)
    return img

def add_document_shape(img, doc_type):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Randomize document size and position slightly
    doc_w = random.randint(140, 180)
    doc_h = random.randint(90, 120)
    x1 = (w - doc_w) // 2 + random.randint(-10, 10)
    y1 = (h - doc_h) // 2 + random.randint(-10, 10)
    
    # Different colors for different docs to help the AI learn quickly for this test
    if doc_type == 'driver_license':
        doc_color = (230, 240, 255) # Light Blueish
        text = "DRIVER LICENSE\nUSA"
    elif doc_type == 'vehicle_registration':
        doc_color = (255, 255, 240) # White/Yellowish
        text = "REGISTRATION\nVALID"
    elif doc_type == 'vehicle_title':
        doc_color = (255, 230, 230) # Pinkish
        text = "CERTIFICATE OF TITLE\nOWNER"
    elif doc_type == 'insurance_card':
        doc_color = (240, 255, 240) # Greenish
        text = "INSURANCE CARD\nPOLICY #"
    else:
        # Unknown/Garbage: Draw random shapes instead of a doc
        for _ in range(5):
            draw.rectangle(
                [random.randint(0, w), random.randint(0, h), random.randint(0, w), random.randint(0, h)],
                fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
        return img

    # Draw the document rectangle
    draw.rectangle([x1, y1, x1 + doc_w, y1 + doc_h], fill=doc_color, outline='black')
    
    # Add Text (Simulating content)
    # Note: On Colab, default fonts are limited, using default.
    try:
        # Try to load a generic font, fallback to default
        font = ImageFont.load_default()
    except:
        font = None
        
    # Draw text in the center of the document
    text_pos = (x1 + 10, y1 + 10)
    draw.text(text_pos, text, fill='black', font=font)
    
    # Draw fake lines of text
    for i in range(3, 8):
        line_y = y1 + (i * 12)
        draw.line((x1 + 10, line_y, x1 + doc_w - 10, line_y), fill='grey', width=2)

    return img

def apply_augmentations(img):
    # Rotation
    img = img.rotate(random.randint(-15, 15), expand=False)
    
    # Blur (Simulate bad camera focus)
    if random.random() > 0.7:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
        
    # Noise
    np_img = np.array(img)
    noise = np.random.normal(0, 5, np_img.shape).astype(np.uint8)
    np_img = np.clip(np_img + noise, 0, 255)
    img = Image.fromarray(np_img)
    
    return img

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Generating {IMAGES_PER_CLASS * len(CLASSES)} synthetic images...")

    for class_name in CLASSES:
        class_dir = os.path.join(OUTPUT_DIR, class_name)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
            
        for i in range(IMAGES_PER_CLASS):
            img = create_noisy_background()
            img = add_document_shape(img, class_name)
            img = apply_augmentations(img)
            
            # Save
            save_path = os.path.join(class_dir, f"synthetic_{i}.jpg")
            img.save(save_path)
            
    print("✅ Dataset generation complete.")

if __name__ == "__main__":
    main()