import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncGenerator, AsyncIterator, Callable, Generator, Iterator, Optional, Union

from fastapi import WebSocket
from app.common.config import ChatConfig

from app.errors.chat_exceptions import ChatLengthException, ChatModelNotImplementedException
from app.models.chat_models import MessageHistory
from app.models.llms import LLMModel, LLMModels
from app.utils.chat.buffer import BufferedUserContext
from app.utils.chat.prompts import cutoff_message_histories, message_histories_to_list
from app.utils.logger import api_logger
from app.viewmodels.base_models import InitMessage, MessageToWebsocket, SendInitToWebsocket, StreamProgress


class SyncToAsyncGenerator:
    def __init__(self, sync_gen: Iterator):
        self._gen: Iterator[Any] = sync_gen
        self._queue: asyncio.Queue = asyncio.Queue()

    def __aiter__(self):
        return self

    async def __anext__(self):
        value = await self._queue.get()
        if value is self:  # using `self` as sentinel
            raise StopAsyncIteration
        return value

    async def run(self, executor: Optional[ThreadPoolExecutor] = None):
        it = iter(self._gen)  # Get an iterator from the generator
        while True:
            try:
                # Use 'self' as a sentinel value to avoid raising StopIteration
                value = await asyncio.get_running_loop().run_in_executor(executor, next, it, self)
                if value is self:  # Check if the iterator is exhausted
                    await self._queue.put(self)  # Notify of completion
                    break
                else:
                    await self._queue.put(value)
            except StopIteration:
                # This exception is expected and handled gracefully
                break
            except Exception as e:
                # Other exceptions are unexpected and should propagate up
                api_logger.exception(f"Unexpected exception in SyncToAsyncGenerator: {e}")
                raise e


class SendToWebsocket:
    @staticmethod
    async def init(
        buffer: BufferedUserContext,
        send_chat_rooms: bool = False,
        send_previous_chats: bool = False,
        send_models: bool = False,
        send_selected_model: bool = False,
        send_tokens: bool = False,
        wait_next_query: bool = False,
    ) -> None:
        def parse_method(message_history: MessageHistory) -> dict[str, Any]:
            return SendInitToWebsocket.from_orm(message_history).dict()

        """Send initial message to websocket, providing current state of user"""
        await SendToWebsocket.message(
            websocket=buffer.websocket,
            msg=InitMessage(
                chat_rooms=buffer.sorted_chat_rooms if send_chat_rooms else None,
                previous_chats=message_histories_to_list(
                    parse_method=parse_method,
                    user_message_histories=buffer.current_user_message_histories,
                    ai_message_histories=buffer.current_ai_message_histories,
                    system_message_histories=buffer.current_system_message_histories,
                )
                if send_previous_chats
                else None,
                models=LLMModels._member_names_ if send_models else None,
                selected_model=buffer.current_user_chat_context.llm_model.name
                if send_selected_model or send_previous_chats or send_models
                else None,
                tokens=buffer.current_user_chat_context.total_tokens if send_tokens else None,
                wait_next_query=wait_next_query,
            ).json(),
            chat_room_id=buffer.current_chat_room_id,
            init=True,
            finish=False,
        )

    @staticmethod
    async def message(
        websocket: WebSocket,
        chat_room_id: str,
        finish: bool = True,
        is_user: bool = False,
        init: bool = False,
        msg: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Send whole message to websocket"""
        await websocket.send_json(  # send stream message
            MessageToWebsocket(
                msg=msg,
                finish=finish,
                chat_room_id=chat_room_id,
                is_user=is_user,
                init=init,
                model_name=model_name,
            ).dict()
        )

    @classmethod
    async def stream(
        cls,
        buffer: BufferedUserContext,
        stream_func: Callable[
            [BufferedUserContext, list[MessageHistory], list[MessageHistory], list[MessageHistory], int],
            Union[AsyncGenerator, Generator],
        ],
        stream_progress: StreamProgress,
        finish: bool = True,
        is_user: bool = False,
        chunk_size: int = 1,
        model_name: Optional[str] = None,
    ) -> None:
        """Send SSE stream to websocket"""
        current_model: LLMModel = buffer.current_llm_model.value
        token_limit: int = (
            current_model.max_total_tokens
            - current_model.token_margin
            - int(getattr(current_model, "description_tokens", 0))
        )

        async def hand_shake() -> None:
            # Send initial message
            await cls.message(
                websocket=buffer.websocket,
                msg=None,
                chat_room_id=buffer.current_chat_room_id,
                finish=False,
                is_user=is_user,
                model_name=model_name,
            )

        async def consumer(async_stream: AsyncIterator) -> None:
            """Helper function to send chunks of data"""
            api_logger.info("Sending stream to websocket")
            iteration: int = 0
            async for delta in async_stream:  # stream from api
                if buffer.done.is_set():
                    raise InterruptedError(stream_progress.response + stream_progress.buffer)
                stream_progress.buffer += delta
                iteration += 1
                if iteration % chunk_size == 0:
                    stream_progress.response += stream_progress.buffer
                    await cls.message(
                        websocket=buffer.websocket,
                        msg=stream_progress.buffer,
                        chat_room_id=buffer.current_chat_room_id,
                        finish=False,
                        is_user=is_user,
                        model_name=model_name,
                    )
                    stream_progress.buffer = ""

        async def transmission(
            user_message_histories: list[MessageHistory],
            ai_message_histories: list[MessageHistory],
            system_message_histories: list[MessageHistory],
            response_in_progress: Optional[MessageHistory] = None,
        ) -> None:
            if response_in_progress is not None:
                ai_message_histories.append(response_in_progress)
            user_message_histories, ai_message_histories = cutoff_message_histories(
                ai_message_histories=ai_message_histories,
                user_message_histories=user_message_histories,
                system_message_histories=system_message_histories,
                token_limit=token_limit - ChatConfig.extra_token_margin,
            )
            try:
                match stream_func(
                    buffer,
                    user_message_histories,
                    ai_message_histories,
                    system_message_histories,
                    (
                        token_limit
                        - sum([m.tokens for m in ai_message_histories])
                        - sum([m.tokens for m in user_message_histories])
                        - sum([m.tokens for m in system_message_histories])
                    ),
                ):
                    case _stream if isinstance(_stream, (AsyncGenerator, AsyncIterator)):
                        await consumer(async_stream=_stream)

                    case _stream if isinstance(_stream, (Generator, Iterator)):
                        async_stream = SyncToAsyncGenerator(sync_gen=_stream)
                        await asyncio.gather(consumer(async_stream=async_stream), async_stream.run(executor=None))

                    case _:
                        raise ChatModelNotImplementedException(msg="Stream type is not AsyncGenerator or Generator.")
            except ChatLengthException as e:
                if e.msg is None:
                    return
                if response_in_progress is not None:
                    ai_message_histories.pop()
                    new_content: str = response_in_progress.content + e.msg + ChatConfig.continue_message
                else:
                    new_content: str = e.msg + ChatConfig.continue_message
                await transmission(
                    ai_message_histories=ai_message_histories,
                    user_message_histories=user_message_histories,
                    system_message_histories=system_message_histories,
                    response_in_progress=MessageHistory(
                        role=buffer.current_user_chat_roles.ai,
                        content=new_content,
                        tokens=buffer.current_user_chat_context.get_tokens_of(new_content),
                        is_user=False,
                    ),
                )

        async def good_bye() -> None:
            await cls.message(
                websocket=buffer.websocket,
                msg=stream_progress.buffer,
                chat_room_id=buffer.current_chat_room_id,
                finish=finish,
                is_user=is_user,
                model_name=model_name,
            )

        try:
            await hand_shake()
            await transmission(
                ai_message_histories=buffer.current_ai_message_histories,
                user_message_histories=buffer.current_user_message_histories,
                system_message_histories=buffer.current_system_message_histories,
            )

        finally:
            await good_bye()
