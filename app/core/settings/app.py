from typing import Any, Dict

from pydantic_settings import BaseSettings


class Base(BaseSettings):
    debug: bool = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
        }
