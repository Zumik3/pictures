import db_connector
import re
from io import BytesIO
import base64
from config import main_dict
from uuid import uuid4


def append_picture_for_select(element):
    result = {key: getattr(element.item, key) for key in main_dict}
    result['guid'] = element.item.guid
    result['image_base64'] = base64.encodebytes(element.image).decode('UTF-8')

    return result


def append_picture_for_insert(element):
    item = db_connector.Item.get_or_none(db_connector.Item.guid == element['guid'])
    if item is not None:
        return dict(item=item, guid=uuid4(), type=element['type'],
                    image=base64.b64decode(element['image']), link=element['link'])
    else:
        return None


def add_picture_to_excel(worksheet, image_base64, column, row):
    base64_data = re.sub('^data:image/.+;base64,', '', image_base64)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)

    worksheet.insert_image(row, column, 'image', {'image_data': image_data, 'x_scale': 0.35, 'y_scale': 0.35,
                                                  'x_offset': 2, 'y_offset': 2})
