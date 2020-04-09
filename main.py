import os
from classification import classify_data
from data_cleaning import clean_image_data, delete_generated_data

def create_directories(*args):
    for files in args:
        if os.path.isdir("./{}".format(files)):
            pass
        else:
            os.mkdir(os.path.join("./", files))


if __name__ == "__main__":
    source_path = "test_images"
    destination_path = "tested"
    text_path = "text"
    create_directories(source_path,destination_path, text_path)
    clean_image_data(source_path, destination_path, text_path)
    classify_data()
    delete_generated_data(destination_path, text_path)