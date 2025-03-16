import numpy as np
from PIL import Image, ImageDraw

def create_icon(size):
    # Create a new image with a white background
    image = Image.new('RGBA', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a shield shape
    margin = size // 8
    shield_points = [
        (margin, size//3),  # Top left
        (size//2, margin),  # Top middle
        (size-margin, size//3),  # Top right
        (size-margin, size*2//3),  # Bottom right
        (size//2, size-margin),  # Bottom middle
        (margin, size*2//3)  # Bottom left
    ]
    
    # Draw shield outline
    draw.polygon(shield_points, fill='#1a73e8', outline='#1557b0')
    
    # Draw check mark
    check_points = [
        (size*0.3, size*0.5),
        (size*0.45, size*0.65),
        (size*0.7, size*0.35)
    ]
    draw.line(check_points, fill='white', width=size//8)
    
    return image

# Create icons directory
import os
if not os.path.exists('icons'):
    os.makedirs('icons')

# Generate icons of different sizes
for size in [16, 48, 128]:
    icon = create_icon(size)
    icon.save(f'icons/icon{size}.png')
