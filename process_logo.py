from PIL import Image, ImageDraw, ImageOps
import numpy as np
import base64
from io import BytesIO
import os

def create_circular_logo(input_path, output_path, size=(200, 200)):
    """Create a circular logo from the input image"""
    try:
        # Open the original image
        img = Image.open(input_path)
        
        # Resize the image to the desired size while maintaining aspect ratio
        img = ImageOps.fit(img, size, Image.LANCZOS)
        
        # Create a mask for circular cropping
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Apply the mask to create circular image
        circular_img = Image.new('RGBA', size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        
        # Save the circular image
        circular_img.save(output_path, format='PNG')
        print(f"Circular logo saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error creating circular logo: {e}")
        return False

def get_image_as_base64(image_path):
    """Convert an image to base64 string for embedding in Streamlit"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

# Process the WhatsApp image if this script is run directly
if __name__ == "__main__":
    input_path = "attached_assets/WhatsApp Image 2025-04-12 at 1.03.31 AM.jpeg"
    output_path = "ivca_logo_circular.png"
    
    if os.path.exists(input_path):
        # Create the circular logo
        success = create_circular_logo(input_path, output_path)
        if success:
            print("Logo processing completed successfully")
        else:
            print("Failed to process logo")
    else:
        print(f"Input file not found: {input_path}")
        
    # Force recreate the logo even if the file doesn't exist
    try:
        print("Attempting to create logo directly...")
        create_circular_logo("attached_assets/WhatsApp Image 2025-04-12 at 1.03.31 AM.jpeg", "ivca_logo_circular.png")
    except Exception as e:
        print(f"Error during force creation: {e}")