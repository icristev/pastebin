import base64
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from app.redis_cache import redis_client

# Загрузка переменных окружения
load_dotenv()

# Подключение к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

logging.basicConfig(level=logging.INFO)


def generate_hashes(batch_size=1000):
    """Генерация хэшей и добавление их в Redis."""
    logging.info("Генерация новых хешей началась...")
    hashes = []
    with engine.connect() as connection:
        for _ in range(batch_size):
            # Получение следующего значения из последовательности
            result = connection.execute(text("SELECT nextval('hash_sequence')"))
            sequence_number = result.scalar()
            # Преобразование числа в base64
            hash_value = base64_encode(sequence_number)
            hashes.append(hash_value)
    # Добавление хэшей в Redis
    redis_client.rpush("hashes", *hashes)
    logging.info("Генерация новых хешей завершена.")


def base64_encode(number):
    """Преобразование числа в base64."""
    return base64.b64encode(
        number.to_bytes((number.bit_length() + 7) // 8, "big")
    ).decode("utf-8")
