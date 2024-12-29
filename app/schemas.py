from datetime import datetime

from pydantic import BaseModel


class CreateBlock(BaseModel):
    content: str
    expires_in: int  # Секунды до истечения


class GetBlock(BaseModel):
    hash: str
    content: str
    expires_at: datetime
