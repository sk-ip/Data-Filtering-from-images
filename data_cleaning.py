import os
import re
import cv2
import time
import shutil
import imutils
import pathlib
import pytesseract
import random, string
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))

def clean_image_data(source_path, destination_path, text_path):
    for e_image in os.listdir(source_path):
        filename = cv2.imread(os.path.join(source_path, e_image))
        gray = cv2.cvtColor(filename, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        gray2 = cv2.medianBlur(gray1, 3)
        '''filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)'''
        '''
        scale_percent = 220 # percent of original size
        width = int(filename.shape[1] * scale_percent / 100)
        height = int(filename.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(filename, dim, interpolation = cv2.INTER_AREA)
        lab= cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        final = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(final,(5,5),0)
        ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        dst = cv2.fastNlMeansDenoising(th3,None,10,7,21)
        '''
        try:
            extractedInformation = pytesseract.image_to_osd(Image.open(os.path.join(source_path, e_image)))
            p=re.search('(?<=Rotate: )\d+',extractedInformation).group(0)

            if int(p) == 90:
                imgg = cv2.rotate(gray2, cv2.ROTATE_90_CLOCKWISE)
                cv2.imwrite(os.path.join(destination_path, e_image), imgg)
            elif int(p) == 270:
                imgg = cv2.rotate(gray2, cv2.ROTATE_90_COUNTERCLOCKWISE)
                cv2.imwrite(os.path.join(destination_path, e_image), imgg)
            else:
                cv2.imwrite(os.path.join(destination_path, e_image), gray2)

            text = pytesseract.image_to_string(Image.open(os.path.join(destination_path, e_image)))
            with open(os.path.join("./"+text_path+"/"+e_image.split(".")[0]+".txt"), "w") as text_file:
                text_file.write(text)
            print("done", e_image)

        except pytesseract.TesseractError:
            pass


def delete_generated_data(c_path, t_path, option=True):
    if option:
        delete(c_path)
        delete(t_path)
    pass

def delete(dirpath):
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)