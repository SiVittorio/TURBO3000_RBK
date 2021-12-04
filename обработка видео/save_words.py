resolution_1 = 720
resolution_2 = 1280

import glob
import numpy as np
from PIL import Image

X_data = []
files = glob.glob(r"video-moviepy\*.jpg")
for my_file in files:
    print(my_file)
    
    image = Image.open(my_file).convert('RGB')
    image = np.array(image)
    if image is None or image.shape != (resolution_1, resolution_2, 3):
        print(f'This image is bad: {my_file} {image.shape if image is not None else "None"}')
    else:
        X_data.append(image)

print('X_data shape:', np.array(X_data).shape)



import pytesseract
from PIL import Image

text_main = '_'
for i in range (len(X_data)):
    img = X_data[i]
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    text = pytesseract.image_to_string(img, lang="rus")
    print(text.strip())
    text_main += text

    with open('text_from_image_2.txt', 'a') as f:
        f.write(text_main.strip())

    
with open('text_from_image_2.txt', 'a') as f:
        f.write(text_main.strip())

