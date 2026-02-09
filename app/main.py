from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_app_settings
from app.core.providers import BLProvider, ConfigProvider, DatabaseProvider, DatabaseSessionProvider, \
    ServiceProvider


def setup_dependencies(app: FastAPI):
    container = make_async_container(
        ConfigProvider("prod"),
        DatabaseProvider(),
        DatabaseSessionProvider(),
        ServiceProvider(),
        BLProvider(),
    )
    setup_dishka(container, app)
    return container


def get_application() -> FastAPI:
    settings = get_app_settings(scope="prod")

    application = FastAPI(**settings.app.fastapi_kwargs)
    setup_dependencies(application)
    application.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from app.api.basic import router
    application.include_router(router)
    return application


app = get_application()
