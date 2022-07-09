from mongoengine import (
    Document,
    EmailField,
    IntField,
    ListField,
    StringField,
    ReferenceField,
    BooleanField
)
from flask_login import UserMixin
import jwt
import datetime
from environment import secret_key


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

    def to_dict(self):
        return {
            "id": str(self.id),
            "filepath": self.filepath,
            "document_id": self.document_id,
            "title": self.title,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "score": self.score,
            "concepts": self.concepts
        }


class User(Document, UserMixin):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    new_email = StringField(default="")
    email_verified = BooleanField(default=False)
    meta = {"collection": "users"}

    def get_token(self, expires_sec=3600):
        token = jwt.encode(
            {
                "confirm": str(self.id),
                "exp": datetime.datetime.now(
                    tz=datetime.timezone.utc) + datetime.timedelta(
                    seconds=expires_sec)
            },
            secret_key,
            algorithm="HS256"
        )
        return token

    @staticmethod
    def verify_token(token):
        try:
            data = jwt.decode(
                token,
                secret_key,
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"]
            )
        except:
            return False
        return User.objects(id=data.get("confirm")).first()
