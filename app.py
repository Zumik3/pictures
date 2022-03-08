import datetime
from flask import Flask
from flask import request, Response, json, render_template
import logging
from logging.config import dictConfig
from config import *
import db_connector
import base64
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from flask_bootstrap import Bootstrap5
import uuid

app = Flask(__name__)
dictConfig(LOGGING_CONFIG)
logging.getLogger(__name__)
auth = HTTPBasicAuth()
bootstrap = Bootstrap5(app)


@auth.verify_password
def verify_password(username, password):

    user = db_connector.User.get_or_none(db_connector.User.username == username)
    if user is not None and check_password_hash(user.password, password):
        return username


@auth.error_handler
def unauthorized():
    return resp(401, {'error': 'Unauthorized access'})


def string_to_base64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64_to_string(b):
    return base64.b64decode(b).decode('utf-8')


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    if code != 200:
        logging.error(str(request.remote_addr) + " " + str(data))

    return Response(status=code,
                    mimetype="application/json",
                    response=to_json(data))


@app.route("/pictures/api/1.0/set_sku", methods=['POST'])
@auth.login_required
def set_sku():
    request_data = request.get_json(force=True)
    data_array = request_data["data"]
    sku_data = []
    for item in data_array:
        sku_data.append({'guid': item["guid"], 'name': item["name"], 'article': item["article"],
                         'group': item["group"], 'collection': item["collection"]})

    try:
        db_connector.Item.insert_many(sku_data).execute()
        db_connector.db.close()
        return resp(200, {"success": True})

    except db_connector.IntegrityError as e:
        return resp(400, {"success": False, "error": str(e)})


@app.route("/pictures/api/1.0/set_picture", methods=['POST'])
@auth.login_required
def set_picture():
    request_data = request.get_json(force=True)
    data_array = request_data["data"]
    picture_data = []
    for element in data_array:
        item = db_connector.Item.get_or_none(db_connector.Item.guid == element["id"])
        if item is not None:
            picture_data.append({"item": item, "image": base64.b64decode(element["image"]), "link": element["link"]})

    try:
        db_connector.Image.insert_many(picture_data).execute()
        db_connector.db.close()
        return resp(200, {"success": True})

    except db_connector.IntegrityError as e:
        return resp(400, {"success": False, "error": str(e)})


@app.route("/pictures/api/1.0/create_link", methods=['POST'])
@auth.login_required
def create_link():
    request_data = request.get_json(force=True)
    data_array = request_data["data"]
    for element in data_array:
        item = db_connector.Item.get_or_none(db_connector.Item.guid == element)
        if item is None:
            return resp(200, {"success": False, "error": "Element not found in DB"})

    try:
        link = db_connector.Link(ref=uuid.uuid4().hex, data=request_data, created_date=datetime.datetime.now())
        link.save()
        return resp(200, {"success": True, "ref": link.ref})

    except db_connector.IntegrityError as e:
        return resp(400, {"success": False, "error": str(e)})


@app.route("/pictures/show/")
def show_icon():

    ref = request.args.get('ref')
    if ref and ref != "":
        link = db_connector.Link.get_or_none(db_connector.Link.ref == ref)
        data_array = json.loads(str(link.data).replace("'", "\""))["data"]
        image_collection = []
        for element in db_connector.Image.select().join(db_connector.Item).where(
                                              db_connector.Item.guid << data_array):
            image_collection.append({"article": element.item.article, "collection": element.item.collection,
                                    "image_base64": base64.encodebytes(element.image).decode('UTF-8')})

        return render_template("index.html", image_collection=image_collection)

    else:
        return resp(404, {})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
