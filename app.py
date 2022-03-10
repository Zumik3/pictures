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
    return resp(401, {'error': UNAUTHORIZED_ACCESS_MESSAGE})


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    if code != 200:
        logging.error(str(request.remote_addr) + " " + str(data))

    return Response(status=code,
                    mimetype="application/json",
                    response=to_json(data))


def create_response(success=True, error=None, ref=None):
    """
    Creates dict for HTTP response
    :param success:
    :param error:
    :param ref:
    :return: Dict
    """
    result = {"success": success}
    if error is not None:
        result["error"] = error
    if ref is not None:
        result["ref"] = ref
    return result


def append_picture_for_select(element):
    """
    Add pictures to container and push this list to front
    :param element:
    :type element: dict()

    :return: New dict with image
    """
    return dict(article=element.item.article, collection=element.item.collection,
                image_base64=base64.encodebytes(element.image).decode('UTF-8'))


def append_picture_for_insert(element) -> dict:
    """
    Add pictures to container and insert them to DB
    :param element:
    :type element: dict

    :return: New dict with image of element, ready for DB insertion
    """
    item = db_connector.Item.get_or_none(db_connector.Item.guid == element["guid"])
    if item is not None:
        return dict(item=item, image=base64.b64decode(element["image"]), link=element["link"])


@app.route("/pictures/api/1.0/set_sku", methods=['POST'])
@auth.login_required
def set_sku():
    request_data = request.get_json(force=True)
    data_array = request_data["data"]

    try:
        db_connector.Item.insert_many(data_array).execute()
        db_connector.db.close()
        return resp(200, create_response())

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@app.route("/pictures/api/1.0/set_picture", methods=['POST'])
@auth.login_required
def set_picture():
    request_data = request.get_json(force=True)
    picture_data = [append_picture_for_insert(element) for element in request_data["data"]]

    try:
        db_connector.Image.insert_many(picture_data).execute()
        db_connector.db.close()
        return resp(200, create_response())

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@app.route("/pictures/api/1.0/create_link", methods=['POST'])
@auth.login_required
def create_link():
    request_data = request.get_json(force=True)
    data_array = request_data["data"]
    for element in data_array:
        item = db_connector.Item.get_or_none(db_connector.Item.guid == element)
        if item is None:
            return resp(400, {"success": False, "error": "Element not found in DB"})

    try:
        link = db_connector.Link(ref=uuid.uuid4().hex, data=request_data, created_date=datetime.datetime.now())
        link.save()
        return resp(200, create_response(True, None, link.ref))

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@app.route("/pictures/show/", methods=['GET'])
def show_icon():

    ref = request.args.get('ref')
    link = db_connector.Link.get_or_none(db_connector.Link.ref == ref)
    if link is None:
        return resp(404, create_response(False, "Link is not found"))

    data_array = json.loads(str(link.data).replace("'", "\""))["data"]
    query_result = db_connector.Image.select().join(db_connector.Item).where(db_connector.Item.guid << data_array)
    image_collection = [append_picture_for_select(element) for element in query_result]

    return render_template("index.html", image_collection=image_collection)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
