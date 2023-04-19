from dataclasses import dataclass, field
import tiktoken


@dataclass
class GptModel:  # gpt model for openai api
    name: str  # model name for openai api
    max_total_tokens: int  # max total tokens for openai api
    max_tokens_per_request: int  # max tokens per request for openai api
    token_margin: int = 8  # token margin for openai api
    api_url: str = "https://api.openai.com/v1/chat/completions"  # api url for openai
    tokenizer: tiktoken.core.Encoding = field(init=False)

    def __post_init__(self):
        self.tokenizer = tiktoken.encoding_for_model(self.name)


@dataclass
class GptModels:  # gpt models for openai api
    gpt_3_5_turbo: GptModel = field(
        default_factory=lambda: GptModel(
            name="gpt-3.5-turbo",
            api_url="https://api.openai.com/v1/chat/completions",
            max_total_tokens=4096,
            max_tokens_per_request=4096,
            token_margin=8,
        )
    )
    gpt_4: GptModel = field(
        default_factory=lambda: GptModel(
            name="gpt-4",
            api_url="https://api.openai.com/v1/chat/completions",
            max_total_tokens=8192,
            max_tokens_per_request=8192,
            token_margin=8,
        )
    )


@dataclass
class MessageHistory:  # message history for user and gpt
    role: str
    content: str
    tokens: int
    is_user: bool

    def __repr__(self) -> str:
        return f"<{self.content}: {self.tokens} tokens>"


@dataclass
class UserGptProfile:  # user gpt profile for user and gpt
    user_id: str
    user_role: str = "user"
    gpt_role: str = "assistant"
    temperature: float = 0.9
    top_p: float = 1.0
    presence_penalty: float = 0
    frequency_penalty: float = 0


@dataclass
class UserGptContext:  # user gpt context for user and gpt
    user_gpt_profile: UserGptProfile
    gpt_model: GptModel
    user_message_histories: list[MessageHistory] = field(default_factory=list)
    gpt_message_histories: list[MessageHistory] = field(default_factory=list)
    system_message_histories: list[MessageHistory] = field(default_factory=list)
    user_message_tokens: int = 0
    gpt_message_tokens: int = 0
    system_message_tokens: int = 0
    is_chat_loaded: bool = False
    is_discontinued: bool = False

    @property
    def left_tokens(self) -> int:
        return self.gpt_model.max_total_tokens - self.total_tokens - self.gpt_model.token_margin

    @property
    def total_tokens(self) -> int:
        return self.user_message_tokens + self.gpt_message_tokens + self.system_message_tokens

    @property
    def token_per_request(self) -> int:
        return min(self.left_tokens, self.gpt_model.max_tokens_per_request)

    def __repr__(self) -> str:
        m: GptModel = self.gpt_model
        return f"""[User Info]
user_id={self.user_gpt_profile.user_id}

[GPT Info]
gpt_model={m.name}
temperature={self.user_gpt_profile.temperature}
top_p={self.user_gpt_profile.top_p}
presence_penalty={self.user_gpt_profile.presence_penalty}
frequency_penalty={self.user_gpt_profile.frequency_penalty}

[Message Histories]
user_message_histories={self.user_message_histories}

gpt_message_histories={self.gpt_message_histories}

system_message_histories={self.system_message_histories}

[Token Info]
Token limit: {m.max_total_tokens}
User token consumed={self.user_message_tokens}
Gpt token consumed={self.gpt_message_tokens}
System token consumed={self.system_message_tokens}
Total token consumed: {self.total_tokens}
Remaining token: {self.left_tokens}"""

    @classmethod
    def make_user_gpt_context_default(cls, user_id: str, gpt_model_name: str | None = None):
        return (
            cls(
                user_gpt_profile=UserGptProfile(user_id=user_id),
                gpt_model=getattr(GPT_MODELS, gpt_model_name),
            )
            if gpt_model_name is not None
            else cls(
                user_gpt_profile=UserGptProfile(user_id=user_id),
            )
        )

    async def add_user_message_history_safely(self, content: str) -> None:
        tokens: int = len(self.gpt_model.tokenizer.encode(content)) + 8
        self.user_message_histories.append(
            MessageHistory(
                role=self.user_gpt_profile.user_role,
                content=content,
                tokens=tokens,
                is_user=True,
            )
        )
        self.user_message_tokens += tokens
        await self.ensure_token_not_exceed()

    async def add_gpt_message_history_safely(self, content: str) -> None:
        tokens: int = len(self.gpt_model.tokenizer.encode(content)) + 8
        self.gpt_message_histories.append(
            MessageHistory(
                role=self.user_gpt_profile.gpt_role,
                content=content,
                tokens=tokens,
                is_user=False,
            )
        )
        self.gpt_message_tokens += tokens
        await self.ensure_token_not_exceed()

    async def ensure_token_not_exceed(
        self,
    ) -> None:
        exceeded_tokens: int = (
            self.gpt_message_tokens
            + self.user_message_tokens
            + self.system_message_tokens
            + self.gpt_model.token_margin
            - self.gpt_model.max_total_tokens
        )
        while exceeded_tokens > 0:
            emptied_user_tokens: int = self.user_message_histories.pop(0).tokens
            emptied_gpt_tokens: int = self.gpt_message_histories.pop(0).tokens
            self.user_message_tokens -= emptied_user_tokens
            self.gpt_message_tokens -= emptied_gpt_tokens
            exceeded_tokens -= emptied_user_tokens + emptied_gpt_tokens


GPT_MODELS = GptModels()