import os

from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")


MINIO_CONFIG = {
    "endpoint": ENDPOINT,
    "access_key": ACCESS_KEY,
    "secret_key": SECRET_KEY,
    "secure": True
}
