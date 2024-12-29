from minio import Minio

# Настройка клиента MinIO
minio_client = Minio(
    endpoint="minio:9000",
    access_key="accesskey123",
    secret_key="secretkey123",
    secure=False,  # Используем HTTP
)

# Проверка наличия бакета
bucket_name = "pastebin-texts"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

# Имя бакета
BUCKET_NAME = "pastebin-texts"

# Создаём бакет, если он не существует
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)
