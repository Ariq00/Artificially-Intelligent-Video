import os
from dotenv import load_dotenv

load_dotenv()

stt_api_key = os.environ.get("STT_API_KEY")
stt_url = os.environ.get("STT_URL")
