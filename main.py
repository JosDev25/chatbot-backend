from fastapi import FastAPI
from dotenv import load_dotenv
import os
import uuid
import openai
from model import User
from model import ChatRequest, LoginRequest 
from db_manager import add_user, get_user, get_anonymous_session, add_anonymous_session, increment_api_calls, users_collection
from db_manager import pwd_context
from request_manager import validate_chat_request
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

allowed_origins=[
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


load_dotenv()
openai.api_key = os.getenv("SECRET_KEY")

@app.post('/session')
def create_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@app.post('/login')
def login_user(request: LoginRequest):
    user = users_collection.find_one({"email": request.email}, {"_id": 0})
    
    if not user:
        return {"message": "Invalid email or password", "success": False}
    
    if not pwd_context.verify(request.password, user["password"]):
        return {"message": "Invalid email or password", "success": False}
    
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return {
        "message": "Login successful", 
        "user": user_data,
        "success": True
    }

@app.post('/chat')
def generate_response(request: dict):
    text = request.get("text")
    email = request.get("email")
    session_id = request.get("session_id")
    
    if not text or len(text) < 10:
        return {"message": "El texto debe tener al menos 10 caracteres"}
    
    if not email and not session_id:
        return {"message": "Either email or session_id is required"}
    
    if session_id and not email:
        session = get_anonymous_session(session_id)
        if isinstance(session, dict) and "api_calls" in session and session["api_calls"] >= 5:
            return {
                "message": "You've reached the maximum number of free API calls. Please register to continue.",
                "limit_reached": True
            }
    
    response = openai.ChatCompletion.create(  
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        max_tokens=1024,
        n=1,
        temperature=0.3
    )
    
    bot_response = response["choices"][0]["message"]["content"]
    
    if email:
        increment_api_calls(email)
        from db_manager import users_collection
        users_collection.update_one(
            {"email": email},
            {"$push": {"chats": {"user": text, "bot": bot_response}}}
        )
    elif session_id:
        add_anonymous_session(session_id, text, bot_response)
    
    return {"response": bot_response}

@app.get('/history')
def get_chat_history(email: str, session_id:str=None):
    
    if email:
        user=get_user(email)
        if "chats" in user:
            return{"email": email, "chats": user["chats"]}
        return{"message": "User not found or chat history"}
    
    elif session_id:
        session = get_anonymous_session(session_id)
        if "chats" in session:
            return {"session_id": session_id, "chats": session["chats"]}
        return {"message": "No chat history for this session"}

    return {"message": "You must provide either an email or a session_id"}

@app.post('/register')
def register_user(request: User, session_id: str = None):
    result = add_user(request.name, request.email, request.password, session_id)
    return result

@app.get("/api_calls")
def get_api_calls(session_id: str):
    session = get_anonymous_session(session_id)
    if isinstance(session, dict) and "api_calls" in session:
        return {"api_calls": session["api_calls"]}
    return {"error": "Session not found"}, 404
