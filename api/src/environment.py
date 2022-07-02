import os
from dotenv import load_dotenv

load_dotenv()

stt_api_key = os.environ.get("STT_API_KEY")
stt_url = os.environ.get("STT_URL")

assistant_api_key = os.environ.get("ASSISTANT_API_KEY")
assistant_url = os.environ.get("ASSISTANT_URL")
assistant_id = os.environ.get("ASSISTANT_ID")

discovery_api_key = os.environ.get("DISCOVERY_API_KEY")
discovery_url = os.environ.get("DISCOVERY_URL")
discovery_environment_id = os.environ.get("DISCOVERY_ENVIRONMENT_ID")
discovery_collection_id = os.environ.get("DISCOVERY_COLLECTION_ID")

nlu_api_key = os.environ.get("NLU_API_KEY")
nlu_url = os.environ.get("NLU_URL")

meaningcloud_license_key = os.environ.get("MEANINGCLOUD_LICENSE_KEY")

secret_key = os.environ.get("SECRET_KEY")

mongo_host = os.environ.get("MONGO_HOST")
