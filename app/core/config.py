from functools import lru_cache
from typing import Literal

from pydantic import BaseModel

from app.core.settings.production import ProdBase
from app.core.settings.test import TestBase


class AppSettings(BaseModel):
    app: ProdBase | TestBase


@lru_cache
def get_app_settings(scope: Literal["prod", "test"]) -> AppSettings:
    app_env = AppSettings(app=ProdBase()) if scope == "prod" else AppSettings(app=TestBase())
    return app_env
