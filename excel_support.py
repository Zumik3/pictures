import pandas as pd
import base64
from config import *
import image_support
import os


def file_to_base64(file_name):
    with open(file_name, 'rb') as file:
        raw_data = file.read()
        return base64.encodebytes(raw_data).decode('UTF-8')


def main_table_to_excel(file_name, image_collection, remove_file=False):
    df = pd.DataFrame({main_dict[x]: [a[x] for a in image_collection] for x in main_dict})
    df.insert(0, IMAGE_COLUMN_NAME, "")

    excel_writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(excel_writer, sheet_name='Sheet1', index=False)

    worksheet = excel_writer.sheets['Sheet1']
    worksheet.set_column(0, 0, DEFAULT_PICTURE_COLUMN_WIDTH)
    worksheet.set_column(1, 0, DEFAULT_PICTURE_COLUMN_WIDTH)
    worksheet.set_default_row(DEFAULT_ROW_HEIGHT)

    for i in range(len(image_collection)):
        image_support.add_picture_to_excel(worksheet, image_collection[i]['image_base64'], 0, i + 1)

    excel_writer.save()
    base64result = file_to_base64(file_name)

    if remove_file:
        os.remove(file_name)

    return base64result
