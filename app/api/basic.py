import structlog
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.services.url_shortener import UrlShortener

router = APIRouter(route_class=DishkaRoute)

logger = structlog.get_logger(__name__)


class ShortenRequest(BaseModel):
    url: HttpUrl


@router.post("/shorten")
async def shorten_url(
        request: Request,
        data: ShortenRequest,
        url_shortener: FromDishka[UrlShortener]
) -> str:
    logger.info(
        "Запрос на создание сокращённой ссылки", url=str(data.url)
    )
    resp = await url_shortener.shorten(
        original_url=str(data.url),
        base_url=str(request.base_url)
    )
    logger.info(
        "Сокращённаяя ссылка", url=resp
    )
    return resp


@router.get("/{code}")
async def redirect_to_url(
        code: str,
        url_shortener: FromDishka[UrlShortener]
):
    logger.info(
        "Запрос на редирект по коду", code=code
    )
    original_url = await url_shortener.resolve(code)
    if not original_url:
        logger.warning(
            "Редирект не найден", url=code
        )
        raise HTTPException(status_code=404)
    logger.info(
        "Редирект выполнен", code=code, url=original_url
    )
    return RedirectResponse(url=original_url)
