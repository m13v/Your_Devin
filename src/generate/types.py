from typing import List, Optional
from enum import Enum, IntEnum
from pydantic import BaseModel

class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class Message(BaseModel):
    role: Role
    content: str

class Conversation(BaseModel):
    messages: List[Message]

