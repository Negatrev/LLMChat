from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel

# from pydantic.networks import EmailStr, IPvanyAddress


class UserRegister(BaseModel):
    email: str = None
    password: str = None


class SnsType(str, Enum):
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel):
    Authorization: str = None


class EmailRecipients(BaseModel):
    name: str
    email: str


class SendEmail(BaseModel):
    email_to: list[EmailRecipients] = None


class KakaoMsgBody(BaseModel):
    msg: str = None


class MessageOk(BaseModel):
    message: str = Field(default="OK")


class UserToken(BaseModel):
    id: int
    email: str = None
    name: str = None
    phone_number: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True


class UserMe(BaseModel):
    id: int
    email: str = None
    name: str = None
    phone_number: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True


class AddApiKey(BaseModel):
    user_memo: str = None

    class Config:
        orm_mode = True


class GetApiKey(AddApiKey):
    id: int = None
    access_key: str = None
    created_at: datetime = None


class GetApiKeyFirstTime(GetApiKey):
    secret_key: str = None


class CreateApiWhiteList(BaseModel):
    ip_address: str = None


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
    msg: str
    finish: bool
    chat_room_id: str
    is_user: bool
    init: bool = False

    class Config:
        orm_mode = True


class MessageFromWebsocket(BaseModel):
    msg: str
    translate: bool
    chat_room_id: str

    class Config:
        orm_mode = True


class CreateChatRoom(BaseModel):  # stub
    chat_room_type: str
    name: str
    description: str = None
    user_id: int

    class Config:
        orm_mode = True


class SendToOpenAI(BaseModel):
    role: str
    content: str

    class Config:
        orm_mode = True


class SendInitToWebsocket(BaseModel):
    content: str
    tokens: int
    is_user: bool
    timestamp: int

    class Config:
        orm_mode = True
