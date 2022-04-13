from peewee import *
from config import MYSQL_DATABASE
from config import MYSQL_HOST
from config import MYSQL_PASSWORD
from config import MYSQL_USER
from playhouse.mysql_ext import MySQLConnectorDatabase


db = MySQLConnectorDatabase(host=MYSQL_HOST,
                            database=MYSQL_DATABASE,
                            user=MYSQL_USER,
                            password=MYSQL_PASSWORD)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):  # Uses for user authorization
    username = CharField(column_name='username', max_length=100)
    password = CharField(column_name='password', max_length=200)
    email = CharField(column_name='email', max_length=100)
    active = BooleanField(column_name='active')

    class Meta:
        table_name = 'users'


class Item(BaseModel):
    guid = CharField(column_name='guid', max_length=36)
    name = CharField(column_name='name', max_length=100)
    article = CharField(column_name='article', max_length=50)
    group = CharField(column_name='group', max_length=50)
    collection = CharField(column_name='collection', max_length=50)

    class Meta:
        table_name = 'items'


class Image(BaseModel):
    item = ForeignKeyField(Item, backref='pictures')
    image = BlobField(column_name='image')
    link = CharField(column_name='link')

    class Meta:
        table_name = 'images'


class Link(BaseModel):  # Uses for create links with content for customers!!!
    ref = CharField(column_name='ref')
    data = TextField(column_name='data')
    created_date = DateField(column_name='created_date')

    class Meta:
        table_name = 'links'


if not Item.table_exists():
    Item.create_table()
if not Image.table_exists():
    Image.create_table()
if not User.table_exists():
    User.create_table()
if not Link.table_exists():
    Link.create_table()
