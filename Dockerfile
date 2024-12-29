# Первый этап: сборка зависимостей
FROM python:3.13-slim AS builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt /app/requirements.txt

# Установка зависимостей
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Второй этап: финальный образ
FROM python:3.13-slim

# Установка минимальных системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование приложения и зависимостей из первого этапа
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
