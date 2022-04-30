import datetime
import uuid

from flask import Flask, render_template

import db_connector
from auth import *
from support import *
from flask_bootstrap import Bootstrap5
import excel_support
import image_support


app = Flask(__name__)
bootstrap = Bootstrap5(app)


@app.route("/pictures/api/1.0/set_sku", methods=['POST'])
@auth.login_required
def set_sku():
    request_data = request.get_json(force=True)
    data_array = request_data['data']

    try:
        db_connector.Item.insert_many(data_array).execute()
        return resp(200, create_response())

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@app.route('/pictures/api/1.0/set_picture', methods=['POST'])
@auth.login_required
def set_picture():
    request_data = request.get_json(force=True)
    picture_data = [image_support.append_picture_for_insert(element) for element in request_data["data"]]

    filtered_picture_data = list(filter(lambda x: x is not None, picture_data))

    try:
        logging.error(picture_data)

        if len(filtered_picture_data) > 0:
            db_connector.Image.insert_many(filtered_picture_data).execute()

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
        link = db_connector.Link(ref=image_support.uuid4().hex, data=request_data, created_date=datetime.datetime.now())
        link.save()
        return resp(200, create_response(True, None, link.ref))

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@app.route("/pictures/getfile/", methods=['GET'])
def get_file():

    ref = request.args.get('ref')

    link = db_connector.Link.get_or_none(db_connector.Link.ref == ref)
    if link is None:
        return resp(404, create_response(False, LINK_NOT_FOUND_MESSAGE))

    file_name = './tmp/' + ref + '.xlsx'
    data_array = json.loads(str(link.data).replace("'", "\""))["data"]

    query_result = db_connector.Image.select().join(db_connector.Item).where(
        (db_connector.Item.guid << data_array) & (db_connector.Image.type == 0))

    image_collection = [image_support.append_picture_for_select(element) for element in query_result]
    result = excel_support.main_table_to_excel(file_name, image_collection, True)

    return Response(status=200, mimetype="text/plain", response=result)


@app.route('/pictures/list/', methods=['GET'])
def show_list():

    ref = request.args.get('ref')
    keyword = request.args.get('keyword')

    link = db_connector.Link.get_or_none(db_connector.Link.ref == ref)
    if link is None:
        return resp(404, create_response(False, LINK_NOT_FOUND_MESSAGE))

    data_array = json.loads(str(link.data).replace("'", "\""))["data"]
    if keyword is not None:
        query_result = db_connector.Image.select().join(db_connector.Item).where(
            (db_connector.Item.guid << data_array) & (db_connector.Item.article.contains(keyword)))
    else:
        query_result = db_connector.Image.select().join(db_connector.Item).where(
            (db_connector.Item.guid << data_array) & (db_connector.Image.type == 0))

    image_collection = [image_support.append_picture_for_select(element) for element in query_result]

    test1 = db_connector.Demo1(name='test111', guid=uuid.uuid4())
    test1.save(force_insert=True)

    test2 = db_connector.Demo2(name='test111', demo1=test1)
    test2.save()

    # test1 = db_connector.Demo2.select().join(db_connector.Demo1).where(db_connector.Demo1.name == 'trtrrtr')
    # if test1 is None:
    #     logging.error('not found')
    # else:
    #     logging.error(test1[0].demo1.name)

    return render_template('index.html', image_collection=image_collection, main_dict=MainFrame().table)


@app.route("/pictures/article/", methods=['GET'])
def show_article():

    article_guid = request.args.get('article')
    query_result = db_connector.Image.select().join(db_connector.Item).where(db_connector.Item.guid == article_guid)
    image_collection = [image_support.append_picture_for_select(element) for element in query_result]

    return render_template("article.html", image_collection=image_collection)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
