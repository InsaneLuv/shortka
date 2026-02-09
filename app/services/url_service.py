from typing import Optional
import secrets
import sqlite3
import string
from dataclasses import dataclass

from app.services.database import Database


@dataclass
class UrlData:
    short_id: str
    original_url: str


class UrlService:
    def __init__(self, db: Database):
        self.db = db

    async def get_short_id_by_url(self, original_url: str) -> Optional[str]:
        result = await self.db.fetchone(
            "SELECT short_id FROM urls WHERE original_url = ? LIMIT 1",
            (original_url,)
        )
        return result[0] if result else None

    async def create_short_url(self, original_url: str, length: int = 6) -> UrlData:
        # Проверяем существующую запись
        existing_short_id = await self.get_short_id_by_url(original_url)
        if existing_short_id:
            return UrlData(short_id=existing_short_id, original_url=original_url)

        # Генерируем новый уникальный ID
        alphabet = string.ascii_letters + string.digits

        for _ in range(100):  # Ограничиваем попытки
            short_id = ''.join(secrets.choice(alphabet) for _ in range(length))

            try:
                await self.db.execute(
                    "INSERT INTO urls (short_id, original_url) VALUES (?, ?)",
                    (short_id, original_url)
                )
                return UrlData(short_id=short_id, original_url=original_url)
            except sqlite3.IntegrityError:
                continue

        # Если не удалось сгенерировать уникальный ID
        raise RuntimeError("Не удалось сгенерировать уникальный короткий идентификатор")

    async def get_original_url(self, short_id: str) -> Optional[str]:
        result = await self.db.fetchone(
            "SELECT original_url FROM urls WHERE short_id = ?",
            (short_id,)
        )
        return result[0] if result else None