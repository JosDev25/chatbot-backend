from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import uuid
import openai
from model import ChatRequest 
from db_manager import add_user, get_user, get_anonymous_session, add_anonymous_session, increment_api_calls

app = FastAPI()

load_dotenv()
openai.api_key = os.getenv("SECRET_KEY")

@app.post('/session')
def create_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@app.post('/chat')
def generate_response(request: ChatRequest, email: str = None, session_id: str = None):

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
        messages=[{"role": "user", "content": request.text}],
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
            {"$push": {"chats": {"user": request.text, "bot": bot_response}}}
        )
    elif session_id:
        add_anonymous_session(session_id, request.text, bot_response)
    
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
def register_user(name: str, email: str, session_id: str = None):
    result = add_user(name, email, session_id)
    return result