import json
from typing import Literal
from app.database.connection import RedisFactory, cache
from app.viewmodels.gpt_models import GPT_MODELS, MessageHistory, UserGptContext, UserGptProfile


class ChatGptCacheManager:
    _string_fields: tuple[str] = (
        "user_gpt_profile",
        "gpt_model",
    )
    _list_fields: tuple[str] = (
        "user_message_histories",
        "gpt_message_histories",
        "system_message_histories",
    )

    def __init__(self, cache: RedisFactory):
        self.cache = cache

    def _generate_key(self, user_id: str, field: str) -> str:
        return f"chatgpt:user:{user_id}:{field}"

    def _get_string_fields(self, user_id: str) -> dict[str, str]:
        return {field: self._generate_key(user_id, field) for field in self._string_fields}

    def _get_list_fields(self, user_id: str) -> dict[str, str]:
        return {field: self._generate_key(user_id, field) for field in self._list_fields}

    async def read_context(self, user_id: str) -> UserGptContext:
        stored_string: dict[str, str | None] = {
            field: await self.cache.redis.get(key) for field, key in self._get_string_fields(user_id).items()
        }
        stored_list: dict[str, list[str] | None] = {
            field: await self.cache.redis.lrange(key, 0, -1) for field, key in self._get_list_fields(user_id).items()
        }

        # if any of stored strings are None, create new context
        if any([value is None for value in stored_string.values()]):
            default: UserGptContext = UserGptContext.construct_default(user_id=user_id)
            self.create_context(user_id=user_id, user_gpt_context=default)
            return default

        for field, value in stored_string.items():
            if value is not None:
                stored_string[field] = json.loads(value)
        for field, value in stored_list.items():
            if value is not None:
                stored_list[field] = [json.loads(v) for v in value]

        user_message_histories = [MessageHistory(**m) for m in stored_list["user_message_histories"]]
        gpt_message_histories = [MessageHistory(**m) for m in stored_list["gpt_message_histories"]]
        system_message_histories = [MessageHistory(**m) for m in stored_list["system_message_histories"]]
        return UserGptContext(
            user_gpt_profile=UserGptProfile(**stored_string["user_gpt_profile"]),
            gpt_model=getattr(GPT_MODELS, stored_string["gpt_model"].replace(".", "_").replace("-", "_")),
            user_message_histories=user_message_histories,
            gpt_message_histories=gpt_message_histories,
            system_message_histories=system_message_histories,
            user_message_tokens=sum([m.tokens for m in user_message_histories]),
            gpt_message_tokens=sum([m.tokens for m in gpt_message_histories]),
            system_message_tokens=sum([m.tokens for m in system_message_histories]),
            is_discontinued=False,
        )

    async def create_context(
        self,
        user_id: str,
        user_gpt_context: UserGptContext,
        only_if_exists: bool = False,
        only_if_not_exists: bool = True,
    ) -> bool:
        json_data = user_gpt_context.json()
        success: bool = True

        for field, key in self._get_string_fields(user_id=user_id).items():
            result = await self.cache.redis.set(
                key,
                json.dumps(json_data[field]),
                xx=only_if_exists,
                nx=only_if_not_exists,
            )
            success &= bool(result)
        for field, key in self._get_list_fields(user_id=user_id).items():
            result = await self.cache.redis.delete(key)
            for item in json_data[field]:
                result = await self.cache.redis.rpush(key, json.dumps(item))
                success &= bool(result)

        return success

    async def reset_context(
        self,
        user_id: str,
        only_if_exists: bool = True,
        only_if_not_exists: bool = False,
    ) -> bool:
        return self.create_context(
            user_id=user_id,
            user_gpt_context=UserGptContext.construct_default(user_id=user_id),
            only_if_exists=only_if_exists,
            only_if_not_exists=only_if_not_exists,
        )

    async def update_context(
        self,
        user_gpt_context: UserGptContext,
        only_if_exists: bool = True,
    ) -> bool:
        json_data = user_gpt_context.json()
        success = True

        for field, key in self._get_string_fields(user_id=user_gpt_context.user_gpt_profile.user_id).items():
            result = await self.cache.redis.set(
                key,
                json.dumps(json_data[field]),
                xx=only_if_exists,
            )
            success &= bool(result)
        for field, key in self._get_list_fields(user_id=user_gpt_context.user_gpt_profile.user_id).items():
            result = await self.cache.redis.delete(key)
            success &= bool(result)
            for item in json_data[field]:
                result = await self.cache.redis.rpush(key, json.dumps(item))
                success &= bool(result)
        return success

    async def update_profile_and_model(
        self,
        user_gpt_context: UserGptContext,
        only_if_exists: bool = True,
    ) -> bool:
        json_data = user_gpt_context.json()
        success = True

        for field, key in self._get_string_fields(user_id=user_gpt_context.user_gpt_profile.user_id).items():
            result = await self.cache.redis.set(
                key,
                json.dumps(json_data[field]),
                xx=only_if_exists,
            )
            success &= bool(result)
        return success

    async def update_message_histories(
        self,
        user_id: str,
        role: Literal["user", "gpt", "system"],
        message_histories: list[MessageHistory],
    ) -> bool:
        assert role in ("user", "gpt", "system")
        key = self._generate_key(user_id, f"{role}_message_histories")
        message_histories_json = [json.dumps(message_history.__dict__) for message_history in message_histories]
        result = await self.cache.redis.delete(key)
        result &= await self.cache.redis.rpush(key, *message_histories_json)
        return bool(result)

    async def lpop_message_history(
        self,
        user_id: str,
        role: Literal["user", "gpt", "system"],
        count: int | None = None,
    ) -> MessageHistory | None:
        assert role in ("user", "gpt", "system")
        assert count is None or count > 0
        message_history_json = await self.cache.redis.lpop(
            self._generate_key(user_id, f"{role}_message_histories"), count=count
        )
        if message_history_json is None:
            return None
        # if message_history_json is instance of list, then it is a list of message histories
        if isinstance(message_history_json, list):
            return [MessageHistory(**json.loads(m)) for m in message_history_json]
        # otherwise, it is a single message history
        return MessageHistory(**json.loads(message_history_json))

    async def rpop_message_history(
        self,
        user_id: str,
        role: Literal["user", "gpt", "system"],
        count: int | None = None,
    ) -> MessageHistory | None:
        assert role in ("user", "gpt", "system")
        assert count is None or count > 0
        message_history_json = await self.cache.redis.rpop(
            self._generate_key(user_id, f"{role}_message_histories"), count=count
        )
        if message_history_json is None:
            return None
        # if message_history_json is instance of list, then it is a list of message histories
        if isinstance(message_history_json, list):
            return [MessageHistory(**json.loads(m)) for m in message_history_json]
        # otherwise, it is a single message history
        return MessageHistory(**json.loads(message_history_json))

    async def append_message_history(
        self,
        user_id: str,
        role: Literal["user", "gpt", "system"],
        message_history: MessageHistory,
        if_exists: bool = False,
    ) -> bool:
        assert role in ("user", "gpt", "system")
        message_history_key = self._generate_key(user_id, f"{role}_message_histories")
        message_history_json = json.dumps(message_history.__dict__)
        result = (
            await self.cache.redis.rpush(message_history_key, message_history_json)
            if not if_exists
            else await self.cache.redis.rpushx(message_history_key, message_history_json)
        )
        return bool(result)

    async def get_message_history(
        self,
        user_id: str,
        role: Literal["user", "gpt", "system"],
    ) -> list[MessageHistory]:
        assert role in ("user", "gpt", "system")
        key = self._generate_key(user_id, f"{role}_message_histories")
        raw_message_histories = await self.cache.redis.lrange(key, 0, -1)
        if raw_message_histories is None:
            return []
        return [MessageHistory(**json.loads(raw_message_history)) for raw_message_history in raw_message_histories]

    async def delete_message_history(
        self,
        user_id: str,
        role: Literal["user", "gpt", "system"],
    ) -> bool:
        assert role in ("user", "gpt", "system")
        key = self._generate_key(user_id, f"{role}_message_histories")
        result = await self.cache.redis.delete(key)
        return bool(result)

    async def set_message_history(
        self,
        user_id: str,
        message_history: MessageHistory,
        index: int,
        role: Literal["user", "gpt", "system"],
    ) -> bool:
        assert role in ("user", "gpt", "system")
        key = self._generate_key(user_id, f"{role}_message_histories")
        # value in redis is a list of message histories
        # set the last element of the list to the new message history
        result = await self.cache.redis.lset(key, index, json.dumps(message_history.__dict__))
        return bool(result)


chatgpt_cache_manager: ChatGptCacheManager = ChatGptCacheManager(cache=cache)