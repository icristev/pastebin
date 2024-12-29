import io
import logging
import os
import uuid
from datetime import timedelta
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from hashids import Hashids
from sqlalchemy.orm import Session, InstrumentedAttribute

from app.database import get_db
from app.models import TextBlock
from app.redis_cache import get_cache, redis_client, set_cache
from app.schemas import CreateBlock
from app.utils.minio_client import BUCKET_NAME, minio_client
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

load_dotenv()
router = APIRouter()





hashids = Hashids(min_length=8)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("pastebin")

@router.post("/create", response_class=PlainTextResponse)
def create_block(data: CreateBlock, db: Session = Depends(get_db)):
    # Генерация уникального имени для файла
    file_name = f"{uuid.uuid4()}.txt"

    # Сохранение текста в MinIO
    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=file_name,
        data=io.BytesIO(data.content.encode("utf-8")),
        length=len(data.content.encode("utf-8")),
        content_type="text/plain",
    )

    # Создание URL для доступа к тексту, который находится в S3
    content_url = f"http://127.0.0.1:9000/{BUCKET_NAME}/{file_name}"

    # Создание текстового блока с URL
    hash_value = redis_client.lpop("hashes")
    block = TextBlock(
        hash=hash_value,
        content_url=content_url,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=data.expires_in),
    )

    db.add(block)
    db.commit()
    db.refresh(block)

    return f"{BASE_URL}/api/get_block/{block.hash} \n"


def check_expiration(expires_at: datetime, block_id: str):
    """
    Проверяет, истек ли срок действия блока.

    :param expires_at: Дата и время истечения срока действия.
    :param block_id: Идентификатор блока для логирования.
    :raises HTTPException: Если срок действия истек.
    """
    expires_at_utc = expires_at.replace(tzinfo=timezone.utc)
    if expires_at_utc < datetime.now(timezone.utc):
        logger.info(f"Сообщение {block_id} истекло в {expires_at_utc}")
        raise HTTPException(status_code=410, detail="Сообщение больше недоступно: срок истёк")


def fetch_content_from_s3(content_url: str) -> str:
    """
    Извлекает содержимое текста из S3.

    :param content_url: URL содержимого в S3.
    :return: Содержимое в текстовом формате.
    :raises HTTPException: В случае ошибки при получении содержимого.
    """
    try:
        file_name = content_url.split("/")[-1]
        object_response = minio_client.get_object(bucket_name=BUCKET_NAME, object_name=file_name)
        return object_response.read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving content: {str(e)}")


def extract_attribute_value(attribute: InstrumentedAttribute, instance: object, attr_name: str):
    """
    Извлекает значение атрибута из объекта модели SQLAlchemy.

    :param attribute: Атрибут SQLAlchemy.
    :param instance: Объект модели.
    :param attr_name: Имя атрибута.
    :return: Значение атрибута.
    """
    if isinstance(attribute, InstrumentedAttribute):
        return getattr(instance, attr_name)
    return attribute


@router.get("/get_block/{block_id}", response_class=PlainTextResponse)
def get_block(block_id: str, db: Session = Depends(get_db)) -> str:
    """
    Получает текстовый блок по идентификатору. Проверяет наличие в кеше, истечение срока действия
    и при необходимости извлекает содержимое из базы данных и S3.

    :param block_id: Идентификатор текстового блока.
    :param db: Сессия подключения к базе данных.
    :return: Содержимое текстового блока.
    :raises HTTPException: Если блок не найден или срок действия истёк.
    """
    # Проверка кеша
    cached_data = get_cache(block_id)
    if cached_data:
        cached_data = json.loads(cached_data)
        content = cached_data.get("content")
        expires_at = datetime.fromisoformat(cached_data.get("expires_at"))

        # Проверяем истечение срока
        check_expiration(expires_at, block_id)
        return content

    # Запрос в БД
    block = db.query(TextBlock).filter(TextBlock.hash == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    # Проверка истечения срока
    expires_at_value = extract_attribute_value(block.expires_at, block, 'expires_at')
    check_expiration(expires_at_value, block_id)

    # Извлечение content_url
    content_url = extract_attribute_value(block.content_url, block, 'content_url')

    # Получение текста из S3
    content = fetch_content_from_s3(content_url)

    # Сохранение в кеш с expires_at
    cached_data = json.dumps({"content": content, "expires_at": block.expires_at.isoformat()})
    set_cache(block_id, cached_data, ttl=3600)

    return content
