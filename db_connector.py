import uuid
import logging
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


class User(BaseModel):
    username = CharField(column_name='username', max_length=100)
    password = CharField(column_name='password', max_length=200)
    email = CharField(column_name='email', max_length=100)
    active = BooleanField(column_name='active')

    class Meta:
        table_name = 'users'


class Item(BaseModel):
    guid = CharField(column_name='guid', max_length=36)
    article = CharField(column_name='article', max_length=50)
    group = CharField(column_name='group', max_length=50)
    collection = CharField(column_name='collection', max_length=50)
    brand = CharField(column_name='brand', max_length=50)
    type = CharField(column_name='type', max_length=50)
    color = CharField(column_name='color', max_length=50)
    segment = CharField(column_name='segment', max_length=50)
    material = CharField(column_name='material', max_length=50)
    lining = CharField(column_name='lining', max_length=50)
    insole = CharField(column_name='insole', max_length=50)
    size_chart = CharField(column_name='size_chart', max_length=100)
    packaged = IntegerField(column_name='packaged')
    price = FloatField(column_name='price')

    class Meta:
        table_name = 'items'


class Image(BaseModel):
    guid = CharField(column_name='guid', max_length=36)
    item = ForeignKeyField(Item, backref='pictures')
    image = BlobField(column_name='image')
    type = IntegerField(column_name='type')
    link = CharField(column_name='link')

    class Meta:
        table_name = 'images'


class Link(BaseModel):  # Uses for create links with content for customers!!!
    ref = CharField(column_name='ref')
    data = TextField(column_name='data')
    created_date = DateField(column_name='created_date')

    class Meta:
        table_name = 'links'


class Demo1(BaseModel):
    guid = UUIDField(primary_key=True, default=uuid.uuid4)
    name = TextField()

    class Meta:
        table_name = 'Demo1'


class Demo2(BaseModel):

    name = TextField()
    demo1 = ForeignKeyField(Demo1, backref='Demo')

    class Meta:
        table_name = 'Demo2'


if not Item.table_exists():
    Item.create_table()
if not Image.table_exists():
    Image.create_table()
if not User.table_exists():
    User.create_table()
if not Link.table_exists():
    Link.create_table()
if not Demo1.table_exists():
    Demo1.create_table()
if not Demo2.table_exists():
    Demo2.create_table()

