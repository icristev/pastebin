FROM python:3.13-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска генератора
CMD ["python", "generator.py"]
