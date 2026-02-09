from typing import Optional

from app.services.url_service import UrlService


class UrlShortener:
    def __init__(self, url_service: UrlService):
        self.url_service = url_service

    async def shorten(self, original_url: str, base_url: str) -> str:
        url_data = await self.url_service.create_short_url(original_url)
        return f"{base_url.rstrip('/')}/{url_data.short_id}"

    async def resolve(self, short_id: str) -> Optional[str]:
        return await self.url_service.get_original_url(short_id)
