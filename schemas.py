# schemas.py
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class PromptResponse(BaseModel):
    prompt: str
    response: str
    timestamp: datetime


class HistoryItem(BaseModel):
    timestamp: datetime
    prompt: str
    response: str


class HistoryResponse(BaseModel):
    history: List[HistoryItem]
