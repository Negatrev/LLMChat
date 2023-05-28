from __future__ import annotations

import logging
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from re import Pattern, compile
from aiohttp import ClientTimeout
from dotenv import load_dotenv
from urllib import parse

load_dotenv()


class SingletonMetaClass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# API Server Variables
API_ENV: str = environ.get("API_ENV", "local")
DOCKER_MODE: bool = environ.get("DOCKER_MODE", "True").lower() == "true"

EXCEPT_PATH_LIST: tuple = (
    "/",
    "/openapi.json",
    "/test",
)
EXCEPT_PATH_REGEX: Pattern = compile("^(/docs|/redoc|/admin|/api/auth|/favicon.ico|/chat|/flutter_service_worker.js)")
TOKEN_EXPIRE_HOURS: int = 168
MAX_API_KEY: int = 3
MAX_API_WHITELIST: int = 10
BASE_DIR: Path = Path(__file__).parents[2]
EMBEDDING_VECTOR_DIMENSION: int = 1536

# MySQL Variables
MYSQL_ROOT_PASSWORD: str = environ["MYSQL_ROOT_PASSWORD"]
MYSQL_USER: str = environ["MYSQL_USER"]
MYSQL_PASSWORD: str = environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE: str = environ["MYSQL_DATABASE"]
MYSQL_TEST_DATABASE: str = environ.get("MYSQL_TEST_DATABASE", MYSQL_DATABASE)
MYSQL_PORT: int = int(environ.get("MYSQL_PORT", 3306))

# Redis Variables
REDIS_PORT: int = int(environ.get("REDIS_PORT", 6379))
REDIS_DATABASE: int = int(environ.get("REDIS_DATABASE", 0))
REDIS_PASSWORD: str = environ["REDIS_PASSWORD"]

# Other Required Variables
HOST_MAIN: str = environ.get("HOST_MAIN", "localhost")
JWT_SECRET: str = environ["JWT_SECRET"]
JWT_ALGORITHM: str = "HS256"


# Optional Service Variables
DEFAULT_LLM_MODEL: str = environ.get("DEFAULT_LLM_MODEL", "gpt_3_5_turbo")
OPENAI_API_KEY: str | None = environ.get("OPENAI_API_KEY")
RAPID_API_KEY: str | None = environ.get("RAPID_API_KEY")
GOOGLE_TRANSLATE_API_KEY: str | None = environ.get("GOOGLE_TRANSLATE_API_KEY")
PAPAGO_CLIENT_ID: str | None = environ.get("PAPAGO_CLIENT_ID")
PAPAGO_CLIENT_SECRET: str | None = environ.get("PAPAGO_CLIENT_SECRET")
CUSTOM_TRANSLATE_URL: str | None = environ.get("CUSTOM_TRANSLATE_URL")
AWS_ACCESS_KEY: str | None = environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY: str | None = environ.get("AWS_SECRET_KEY")
AWS_AUTHORIZED_EMAIL: str | None = environ.get("AWS_AUTHORIZED_EMAIL")
SAMPLE_JWT_TOKEN: str | None = environ.get("SAMPLE_JWT_TOKEN")
SAMPLE_ACCESS_KEY: str | None = environ.get("SAMPLE_ACCESS_KEY")
SAMPLE_SECRET_KEY: str | None = environ.get("SAMPLE_SECRET_KEY")
KAKAO_RESTAPI_TOKEN: str | None = environ.get("KAKAO_RESTAPI_TOKEN")
WEATHERBIT_API_KEY: str | None = environ.get("WEATHERBIT_API_KEY")
KAKAO_IMAGE_URL: str | None = (
    "http://k.kakaocdn.net/dn/wwWjr/btrYVhCnZDF/2bgXDJth2LyIajIjILhLK0/kakaolink40_original.png"
)

"""
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway
504 Timeout
200 OK
201 Created
"""


@dataclass
class Config(metaclass=SingletonMetaClass):
    app_title: str = "FastAPI"
    app_description: str = ""
    app_version: str = "1.0.0"
    host_main: str = HOST_MAIN
    port: int = 8000
    db_pool_recycle: int = 900
    db_echo: bool = False
    debug: bool = False
    test_mode: bool = False
    database_url_format: str = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    mysql_root_password: str = MYSQL_ROOT_PASSWORD
    mysql_user: str = MYSQL_USER
    mysql_password: str = MYSQL_PASSWORD
    mysql_database: str = MYSQL_DATABASE
    mysql_host: str = "db"
    mysql_port: int = MYSQL_PORT
    redis_url_format: str = "redis://{username}:{password}@{host}:{port}/{db}"
    redis_host: str = "cache"
    redis_port: int = REDIS_PORT
    redis_database: int = REDIS_DATABASE
    redis_password: str = REDIS_PASSWORD
    trusted_hosts: list[str] = field(default_factory=lambda: ["*"])
    allowed_sites: list[str] = field(default_factory=lambda: ["*"])

    def __post_init__(self):
        if not DOCKER_MODE:
            self.port = 8001
            self.mysql_host = "localhost"
            self.redis_host = "localhost"
        self.mysql_root_url = self.database_url_format.format(
            dialect="mysql",
            driver="pymysql",
            user="root",
            password=parse.quote(self.mysql_root_password),
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
        )
        self.mysql_url = self.database_url_format.format(
            dialect="mysql",
            driver="aiomysql",
            user=self.mysql_user,
            password=parse.quote(self.mysql_password),
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
        )
        self.redis_url = self.redis_url_format.format(
            username="",
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_database,
        )

    @staticmethod
    def get(
        option: str | None = None,
    ) -> LocalConfig | ProdConfig | TestConfig:
        if environ.get("PYTEST_RUNNING") is not None:
            return TestConfig()
        else:
            if option is not None:
                return {
                    "prod": ProdConfig,
                    "local": LocalConfig,
                    "test": TestConfig,
                }[option]()
            else:
                if API_ENV is not None:
                    return {
                        "prod": ProdConfig,
                        "local": LocalConfig,
                        "test": TestConfig,
                    }[API_ENV]()
                else:
                    return LocalConfig()


@dataclass
class LocalConfig(Config):
    debug: bool = True


@dataclass
class ProdConfig(Config):
    db_echo: bool = False
    trusted_hosts: list = field(
        default_factory=lambda: [
            f"*.{HOST_MAIN}",
            HOST_MAIN,
            "localhost",
        ]
    )
    allowed_sites: list = field(
        default_factory=lambda: [
            f"*.{HOST_MAIN}",
            HOST_MAIN,
            "localhost",
        ]
    )


@dataclass
class TestConfig(Config):
    test_mode: bool = True
    debug: bool = False
    mysql_database: str = MYSQL_TEST_DATABASE
    mysql_host: str = "localhost"
    redis_host: str = "localhost"
    port: int = 8001


@dataclass
class LoggingConfig:
    logger_level: int = logging.DEBUG
    console_log_level: int = logging.INFO
    file_log_level: int | None = logging.DEBUG
    file_log_name: str | None = "./logs/debug.log"
    logging_format: str = "[%(asctime)s] %(name)s:%(levelname)s - %(message)s"


@dataclass
class ChatConfig:
    api_url: str = "https://api.openai.com/v1/chat/completions"  # api url for openai
    timeout: ClientTimeout = ClientTimeout(sock_connect=30.0, sock_read=20.0)
    read_timeout: float = 30.0  # wait for this time before timeout
    wait_for_reconnect: float = 3.0  # wait for this time before reconnecting
    api_regex_pattern: Pattern = compile(r"data:\s*({.+?})\n\n")
    extra_token_margin: int = 512  # number of tokens to remove when tokens exceed token limit
    continue_message: str = "...[CONTINUED]"  # message to append when tokens exceed token limit
    summarize_for_chat: bool = True  # whether to summarize chat messages
    summarization_threshold: int = 512  # token threshold for summarization. if message tokens exceed this, summarize
    summarization_openai_model: str = "gpt-3.5-turbo"
    summarization_token_limit: int = 2048  # token limit for summarization
    summarization_token_overlap: int = 100  # number of tokens to overlap between chunks


config = Config.get()
logging_config = LoggingConfig()
chat_config = ChatConfig()
