import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestShortenAPI:

    async def test_shorten_url_success(self, test_client: AsyncClient):
        url_data = {
            "url": "https://example.com/test/bobik_bilibobik"
        }

        response = await test_client.post("/shorten", json=url_data)
        assert response.status_code == 200
        data = response.json()
        assert "http" in data

    async def test_shorten_url_duplicate(self, test_client: AsyncClient):
        url_data = {
            "url": "https://example.com/duplicate"
        }

        response1 = await test_client.post("/shorten", json=url_data)
        assert response1.status_code == 200
        data1 = response1.json()
        first_short_id = data1

        response2 = await test_client.post("/shorten", json=url_data)
        assert response2.status_code == 200
        data2 = response2.json()

        # Должен вернуться тот же short_id
        assert data2 == first_short_id

    async def test_shorten_url_invalid(self, test_client: AsyncClient):
        """Тест с некорректным URL"""
        invalid_urls = [
            {"url": "not-a-url"},
            {"url": "ftp://example.com"},
            {"url": ""},
            {1: 2}
        ]

        for url_data in invalid_urls:
            response = await test_client.post("/shorten", json=url_data)
            assert response.status_code == 422

    async def test_redirect_success(self, test_client: AsyncClient):
        """Тест успешного редиректа"""
        url_data = {
            "url": "https://example.com/redirect-test"
        }

        create_response = await test_client.post("/shorten", json=url_data)
        assert create_response.status_code == 200

        short_url = create_response.json()

        redirect_response = await test_client.get(short_url, follow_redirects=False)
        assert redirect_response.status_code == 307
        assert redirect_response.headers["location"] == url_data["url"]

    async def test_redirect_not_found(self, test_client: AsyncClient):
        """Тест редиректа с несуществующим кодом"""
        response = await test_client.get("/nonexistent", follow_redirects=False)
        assert response.status_code == 404
