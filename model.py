from pydantic import BaseModel, EmailStr, Field

class ChatRequest(BaseModel):
    text: str=Field(min_length=10,max_length=2000)

class User(BaseModel):
    name: str = Field(min_length=5, max_length=100)
    email: EmailStr 
    password: str = Field(min_length=8) 
    api_calls: int = 0
    chats: list[dict] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 
    
class AnonymousSession(BaseModel):
    session_id: str
    api_calls: int = 0
    chats: list[dict] = []
