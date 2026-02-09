import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from app.core.settings.app import Base


class ProdBase(Base):
    model_config = SettingsConfigDict(env_file=".env")

    DB_NAME: str = Field(default="app.db")
    DB_PATH: str = Field(default=".")

    @field_validator("DB_PATH", mode="after")
    def create_db_directory(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def db_full_path(self) -> str:
        return os.path.join(self.DB_PATH, self.DB_NAME)
