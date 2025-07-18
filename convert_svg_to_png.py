"""
Convert SVG files to PNG for better compatibility with PyInstaller
Requires: pip install cairosvg pillow
"""

import os
import sys

try:
    from cairosvg import svg2png
    from PIL import Image
except ImportError:
    print("Please install required packages:")
    print("pip install cairosvg pillow")
    sys.exit(1)

def convert_svg_to_png():
    # Create output directory
    os.makedirs("assets/tiles_png", exist_ok=True)
    
    # Convert each SVG to PNG
    svg_dir = "assets/tiles"
    png_dir = "assets/tiles_png"
    
    for filename in os.listdir(svg_dir):
        if filename.endswith(".svg"):
            svg_path = os.path.join(svg_dir, filename)
            png_filename = filename.replace(".svg", ".png")
            png_path = os.path.join(png_dir, png_filename)
            
            print(f"Converting {filename} to PNG...")
            
            # Convert SVG to PNG at high resolution
            svg2png(url=svg_path, write_to=png_path, output_width=120, output_height=160)
            
            # Optimize PNG size
            img = Image.open(png_path)
            img.save(png_path, optimize=True)
    
    print(f"\nConversion complete! PNG files saved in {png_dir}")
    print("Update your code to use .png files instead of .svg")

if __name__ == "__main__":
    convert_svg_to_png()