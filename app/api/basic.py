from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.services.url_shortener import UrlShortener

router = APIRouter(route_class=DishkaRoute)


class ShortenRequest(BaseModel):
    url: HttpUrl


@router.post("/shorten")
async def shorten_url(
        request: Request,
        data: ShortenRequest,
        url_shortener: FromDishka[UrlShortener]
):
    return await url_shortener.shorten(
        original_url=str(data.url),
        base_url=str(request.base_url)
    )


@router.get("/{code}")
async def redirect_to_url(
        code: str,
        url_shortener: FromDishka[UrlShortener]
):
    original_url = await url_shortener.resolve(code)
    if not original_url:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=original_url)
