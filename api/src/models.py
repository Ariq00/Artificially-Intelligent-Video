from mongoengine import (
    Document,
    EmailField,
    IntField,
    ListField,
    StringField,
    ReferenceField
)
from flask_login import UserMixin


class Video(Document):
    user = ReferenceField("User", required=True)
    filepath = StringField(required=True)
    document_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    summary = StringField(required=True)
    sentiment = StringField(choices=["Positive", "Negative", "Neutral"])
    score = IntField(required=True)
    concepts = ListField()
    meta = {"collection": "videos"}


class User(Document, UserMixin):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    meta = {"collection": "users"}
