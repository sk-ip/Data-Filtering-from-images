import os
from main import create_directories
from generate_csv import generate_csv
from data_cleaning import clean_image_data, delete_generated_data

def extract_data(dirpath):
    txt_List = []
    for t_file in os.listdir(dirpath):
        with open(os.path.join(dirpath, t_file), "r") as text_file:
            for line in text_file.readlines():
                line = line.strip("\n").strip()
                txt_List.append(line.split(" "))
            print(txt_List)

    generate_csv(txt_List, "excel_data.csv")


if __name__ == "__main__":
    source_path = "Excel_dataset"
    destination_path = "excel_tested"
    t_path = "excel_text"
    create_directories(source_path,destination_path, t_path)
    clean_image_data(source_path, destination_path, t_path)
    extract_data(t_path)

