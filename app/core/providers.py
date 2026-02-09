from typing import AsyncIterable, Literal

from dishka import provide, Provider, Scope

from app.core.config import AppSettings, get_app_settings
from app.services.database import Database
from app.services.migrations import run_migrations
from app.services.url_service import UrlService
from app.services.url_shortener import UrlShortener


class DatabaseLayout(Database):
    """Обёртка для предотвращения цикла зависимостей"""
    pass


class ConfigProvider(Provider):
    def __init__(self, scope: Literal["prod", "test"] = "prod"):
        super().__init__()
        self.settings_scope = scope

    @provide(scope=Scope.APP)
    def get_settings(self) -> AppSettings:
        return get_app_settings(self.settings_scope)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_database(self, settings: AppSettings) -> DatabaseLayout:
        db = DatabaseLayout(settings.app.db_full_path)
        await db.connect()
        await run_migrations(db)
        return db


class DatabaseSessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self, db: DatabaseLayout) -> AsyncIterable[Database]:
        try:
            yield db
        finally:
            pass


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_url_service(self, db: Database) -> UrlService:
        return UrlService(db)


class BLProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_url_shortener(self, url_service: UrlService) -> UrlShortener:
        return UrlShortener(url_service)
