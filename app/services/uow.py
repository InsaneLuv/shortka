import secrets
import sqlite3
import string
from typing import Optional

from app.services.database import Database


class UOW:
    def __init__(self, db: Database):
        self.db = db

    async def get_short_id_by_url(self, original_url: str) -> Optional[str]:
        result = await self.db.fetchone(
            "SELECT short_id FROM urls WHERE original_url = ? LIMIT 1",
            (original_url,)
        )
        return result[0] if result else None

    async def create_url_record(self, original_url: str, length: int = 6) -> str:
        existing_short_id = await self.get_short_id_by_url(original_url)
        if existing_short_id:
            return existing_short_id

        alphabet = string.ascii_letters + string.digits

        while True:
            short_id = ''.join(secrets.choice(alphabet) for _ in range(length))

            try:
                await self.db.execute(
                    "INSERT INTO urls (short_id, original_url) VALUES (?, ?)",
                    (short_id, original_url)
                )
                return short_id
            except sqlite3.IntegrityError:
                continue

    async def get_original_url(self, short_id: str) -> Optional[str]:
        result = await self.db.fetchone(
            "SELECT original_url FROM urls WHERE short_id = ?",
            (short_id,)
        )
        return result[0] if result else None

    async def url_exists(self, short_id: str) -> bool:
        result = await self.db.fetchone(
            "SELECT 1 FROM urls WHERE short_id = ?",
            (short_id,)
        )
        return result is not None