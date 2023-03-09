import pytest
from sqlalchemy import select
from uuid import uuid4
from app.models import AddApiKey, UserToken
from app.database.schema import Users, ApiKeys, db
from app.database.crud import create_api_key, get_api_key_and_owner
from app.middlewares.token_validator import (
    validate_api_key,
)
from app.utils.date_utils import UTC
from app.utils.query_utils import parse_params
from app.utils.encoding_and_hashing import hash_params


@pytest.mark.asyncio
async def test_apikey_idenfitication(random_user):
    user: Users = await Users.add_one(autocommit=True, refresh=True, **random_user)
    additional_key_info: AddApiKey = AddApiKey(user_memo="[Testing] test_apikey_query")
    new_api_key: ApiKeys = await create_api_key(
        user_id=user.id, additional_key_info=additional_key_info
    )
    matched_api_key, matched_user = await get_api_key_and_owner(
        access_key=new_api_key.access_key
    )
    assert matched_api_key.access_key == new_api_key.access_key
    assert random_user["email"] == matched_user.email


@pytest.mark.asyncio
async def test_api_key_validation(random_user):
    user: Users = await Users.add_one(autocommit=True, refresh=True, **random_user)
    additional_key_info: AddApiKey = AddApiKey(user_memo="[Testing] test_apikey_query")
    new_api_key: ApiKeys = await create_api_key(
        user_id=user.id, additional_key_info=additional_key_info
    )
    timestamp: str = str(UTC.timestamp(hour_diff=9))
    parsed_qs: str = parse_params(
        params={"key": new_api_key.access_key, "timestamp": timestamp}
    )
    user_token: UserToken = await validate_api_key(
        api_access_key=new_api_key.access_key,
        hashed_secret=hash_params(
            query_params=parsed_qs, secret_key=new_api_key.secret_key
        ),
        query_params=parsed_qs,
        timestamp=timestamp,
    )
    assert user_token.id == user.id


@pytest.mark.asyncio
async def test_crud():
    total_users: int = 4
    users: list[dict[str, str]] = [
        {"email": str(uuid4())[:18], "password": str(uuid4())[:18]}
        for _ in range(total_users)
    ]
    user_1, user_2, user_3, user_4 = users

    # C/U
    await Users.add_all(user_1, user_2, autocommit=True, refresh=True)
    await Users.add_one(autocommit=True, refresh=True, **user_3)
    await Users.update_where(
        user_2,
        {"email": "UPDATED", "password": "updated"},
        autocommit=True,
    )

    # R
    result_1_stmt = select(Users).filter(
        Users.email.in_([user_1["email"], "UPDATED", user_3["email"]])
    )
    result_1 = await db.scalars__fetchall(result_1_stmt)
    assert len(result_1) == 3
    for user_idx, fetched_user in enumerate(result_1):
        assert (
            fetched_user.email == users[user_idx]["email"]
            if user_idx != 1
            else fetched_user.email == "UPDATED"
        )
    result_2 = await Users.one_filtered_by(**user_3)
    assert result_2.email == user_3["email"]
    result_3 = await Users.fetchall_filtered_by(**user_4)
    assert len(result_3) == 0

    # D
    await db.delete(result_2, autocommit=True)
    result_4_stmt = select(Users).filter_by(**user_3)
    result_4 = (await db.scalars(stmt=result_4_stmt)).first()
    assert result_4 is None
