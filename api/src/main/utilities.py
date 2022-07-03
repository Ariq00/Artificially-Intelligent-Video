from flask_login import current_user
from models import Video


def check_if_video_saved(document_id):
    if current_user and Video.objects(user=current_user,
                                      document_id=document_id):
        video_is_saved = True
    else:
        video_is_saved = False

    return video_is_saved
