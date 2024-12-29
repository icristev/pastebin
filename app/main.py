from fastapi import FastAPI

from app.routers import blocks

# Создание экземпляра FastAPI
app = FastAPI()

# Подключение роутеров
app.include_router(blocks.router, prefix="/api", tags=["blocks"])
