from flask import request, Response, json
from config import *
import logging
from logging.config import dictConfig


dictConfig(LOGGING_CONFIG)
logging.getLogger(__name__)


class MainFrame:

    def __init__(self):
        self.table = dict(article='Артикул', collection='Сезон',
                          brand='Марка', type='Тип', color='Цвет',
                          segment='Сегмент', material='Материал',
                          lining='Подкладка', insole='Стелька',
                          size_chart='Размерная сетка', packaged='В коробе',
                          price='Цена')


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    if code != 200:
        logging.error(str(request.remote_addr) + " " + str(data))

    return Response(status=code,
                    mimetype="application/json",
                    response=to_json(data))


def create_response(success=True, error=None, ref=None):
    result = {"success": success}
    if error is not None:
        result["error"] = error
    if ref is not None:
        result["ref"] = ref
    return result

