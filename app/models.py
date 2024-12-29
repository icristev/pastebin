from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TextBlock(Base):
    __tablename__ = "text_blocks"
    # Уникальный идентификатор
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True, nullable=False)
    content_url = Column(String, nullable=False)  # URL текста в MinIO
    expires_at = Column(DateTime, nullable=False)
