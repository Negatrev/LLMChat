import asyncio
from datetime import datetime
from os import environ
from fastapi import FastAPI, Response
from starlette.testclient import TestClient
import pytest
from httpx import AsyncClient
import pytest_asyncio
from app.utils.auth.token import create_access_token
from app.utils.tests.tests_utils import random_user_generator

environ["API_ENV"] = "test"
from app.database.connection import db
from app.database.schemas.auth import Users
from app.common.app_settings import create_app
from app.common.config import Config, config
from app.viewmodels.base_models import UserToken

"""
1. DB 생성
2. 테이블 생성
3. 테스트 코드 작동
4. 테이블 레코드 삭제
"""

db.init(config=Config.get(option="test"))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    _app = create_app(config)
    return _app


@pytest.fixture(scope="session")
def base_http_url() -> str:
    return "http://localhost"


@pytest.fixture(scope="session")
def base_websocket_url() -> str:
    return "ws://localhost"


@pytest_asyncio.fixture(scope="session")
async def real_client(app: FastAPI, base_http_url: str) -> AsyncClient:
    async with AsyncClient(app=app, base_url=base_http_url) as ac:
        yield ac


@pytest.fixture
def fake_client(app: FastAPI) -> TestClient:
    with TestClient(app) as tc:
        yield tc


@pytest_asyncio.fixture(scope="session")
async def login_header(random_user: dict[str, str]) -> dict[str, str]:
    """
    테스트 전 사용자 미리 등록
    """
    new_user = await Users.add_one(autocommit=True, refresh=True, **random_user)
    access_token = create_access_token(
        data=UserToken.from_orm(new_user).dict(exclude={"password", "marketing_agree"}),
        expires_delta=24,
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="session")
async def api_key_dict(real_client: AsyncClient, login_header: str):
    api_key_memo: str = f"TESTING : {str(datetime.now())}"
    response: Response = await real_client.post(
        "/api/user/apikeys",
        json={"user_memo": api_key_memo},
        headers=login_header,
    )
    response_body = response.json()
    assert response.status_code == 200
    assert "access_key" in response_body
    assert "secret_key" in response_body
    apikey = {
        "access_key": response_body["access_key"],
        "secret_key": response_body["secret_key"],
    }

    response = await real_client.get("/api/user/apikeys", headers=login_header)
    response_body = response.json()
    assert response.status_code == 200
    assert api_key_memo in response_body[0]["user_memo"]
    return apikey


@pytest.fixture(scope="session")
def random_user():
    return random_user_generator()
