from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic.main import BaseModel

from app.database.schemas.auth import UserStatus

# from pydantic.networks import EmailStr, IPvanyAddress


class UserRegister(BaseModel):
    email: str
    password: str


class SnsType(str, Enum):
    EMAIL = "email"
    FACEBOOK = "facebook"
    GOOGLE = "google"
    KAKAO = "kakao"


class Token(BaseModel):
    Authorization: str


class EmailRecipients(BaseModel):
    name: str
    email: str


class SendEmail(BaseModel):
    email_to: list[EmailRecipients]


class KakaoMsgBody(BaseModel):
    msg: str


class MessageOk(BaseModel):
    message: str = Field(default="OK")


class UserToken(BaseModel):
    id: int
    status: UserStatus
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class UserMe(BaseModel):
    id: int
    email: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_img: Optional[str] = None
    sns_type: Optional[str] = None

    class Config:
        orm_mode = True


class AddApiKey(BaseModel):
    user_memo: Optional[str] = None

    class Config:
        orm_mode = True


class GetApiKey(AddApiKey):
    id: int
    access_key: str
    created_at: datetime


class GetApiKeyFirstTime(GetApiKey):
    secret_key: str


class CreateApiWhiteList(BaseModel):
    ip_address: str


class GetApiWhiteList(CreateApiWhiteList):
    id: int

    class Config:
        orm_mode = True


class CreateChatMessage(BaseModel):  # stub
    message: str
    role: str
    user_id: int
    chat_room_id: str

    class Config:
        orm_mode = True


class MessageToWebsocket(BaseModel):
    msg: Optional[str]
    finish: bool
    chat_room_id: Optional[str] = None
    is_user: bool
    init: bool = False
    model_name: Optional[str] = None
    uuid: Optional[str] = None
    wait_next_query: Optional[bool] = None

    class Config:
        orm_mode = True


class MessageFromWebsocket(BaseModel):
    msg: str
    translate: Optional[str] = None
    chat_room_id: str


class CreateChatRoom(BaseModel):  # stub
    chat_room_type: str
    name: str
    description: Optional[str] = None
    user_id: int

    class Config:
        orm_mode = True


class OpenAIChatMessage(BaseModel):
    role: str
    content: str

    class Config:
        orm_mode = True


class SendInitToWebsocket(BaseModel):
    content: str
    tokens: int
    is_user: bool
    timestamp: int
    model_name: Optional[str] = None
    uuid: Optional[str] = None

    class Config:
        orm_mode = True


class InitMessage(BaseModel):
    previous_chats: Optional[list[dict]] = None
    chat_rooms: Optional[list[dict[str, str]]] = None
    models: Optional[list[str]] = None
    selected_model: Optional[str] = None
    tokens: Optional[int] = None


class StreamProgress(BaseModel):
    response: str = ""
    buffer: str = ""
    uuid: Optional[str] = None


class UserChatRoles(BaseModel):
    ai: str
    system: str
    user: str


class SummarizedResult(BaseModel):
    user_id: str
    chat_room_id: str
    role: str
    content: str
    uuid: str