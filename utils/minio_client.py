from minio import Minio
from config.minio_config import MINIO_CONFIG

minio_client = Minio(
    endpoint=MINIO_CONFIG["endpoint"],
    access_key=MINIO_CONFIG["access_key"],
    secret_key=MINIO_CONFIG["secret_key"],
    secure=MINIO_CONFIG["secure"],
)
