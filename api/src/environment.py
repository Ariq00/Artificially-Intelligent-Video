import os
from dotenv import load_dotenv

load_dotenv()

stt_api_key = os.environ.get("STT_API_KEY")
stt_url = os.environ.get("STT_URL")
assistant_api_key = os.environ.get("ASSISTANT_API_KEY")
assistant_url = os.environ.get("ASSISTANT_URL")
assistant_id = os.environ.get("ASSISTANT_ID")
