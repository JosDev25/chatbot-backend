from pydantic import BaseModel, EmailStr, Field

class Model(BaseModel):
    text: str=Field(min_length=10,max_length=1000)

class User(BaseModel):
    name: str = Field(min_length=5, max_length=100)
    email: EmailStr 
    api_calls: int = 0
    chats: list[dict] = []
    
class AnonymousSession(BaseModel):
    session_id: str
    api_calls: int = 0
    chats: list[dict] = []