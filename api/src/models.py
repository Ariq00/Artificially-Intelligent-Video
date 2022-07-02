from mongoengine import (
    BooleanField,
    Document,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    IntField,
    ListField,
    StringField,
)


class Videos(EmbeddedDocument):
    video_filename = StringField(required=True)
    title = StringField(required=True)
    summary = IntField(required=True)
    sentiment = StringField(choices=["positive", "negative", "neutral"])
    score = IntField(required=True)
    concepts = ListField()


class User(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    saved_videos = EmbeddedDocumentListField(Videos, default=[])
    meta = {"collection": "users"}
