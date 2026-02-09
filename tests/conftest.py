import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from typing import AsyncGenerator

import pytest
from dishka import make_async_container
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import AppSettings
from app.core.providers import (BLProvider, ConfigProvider, DatabaseProvider, DatabaseSessionProvider,
                                ServiceProvider)
from app.services.database import Database


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def di_container() -> AsyncGenerator:
    container = make_async_container(
        ConfigProvider("test"),
        DatabaseProvider(),
        DatabaseSessionProvider(),
        ServiceProvider(),
        BLProvider(),
    )
    async with container() as state:
        settings = await state.get(AppSettings)
        db_path = settings.app.db_full_path
        db = await state.get(Database)
    yield container
    await container.close()
    await db.close()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="session")
async def test_app(di_container) -> AsyncGenerator[FastAPI, None]:
    """Тестовое приложение"""
    test_app = FastAPI()

    from app.api.basic import router
    test_app.include_router(router)

    from dishka.integrations.fastapi import setup_dishka
    setup_dishka(di_container, test_app)

    yield test_app


@pytest.fixture(scope="session")
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный тестовый клиент"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield client
