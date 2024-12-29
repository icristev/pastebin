import os

import redis
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение конфигурации Redis из .env
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Подключение к Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,  # Чтение данных как строки (для удобства)
)


# Установить ключ с временем жизни (в секундах)
def set_cache(key: str, value: str, ttl: int = 3600):
    """Установить значение в Redis с временем жизни."""
    redis_client.setex(key, ttl, value)


# Получить значение по ключу
def get_cache(key: str) -> str:
    """Получить значение из Redis по ключу."""
    return redis_client.get(key)


# Удалить ключ
def delete_cache(key: str):
    """Удалить ключ из Redis."""
    redis_client.delete(key)
