from PIL import Image
import os

def convert():
    try:
        img_path = "resources/icon.png"
        out_path = "resources/icon.ico"
        
        if not os.path.exists(img_path):
            print(f"Error: {img_path} not found.")
            return

        img = Image.open(img_path)
        img.save(out_path, format='ICO', sizes=[(256, 256)])
        print(f"Successfully converted {img_path} to {out_path}")
    except Exception as e:
        print(f"Conversion failed: {e}")

if __name__ == "__main__":
    convert()
