from fastapi import FastAPI
from dotenv import load_dotenv
import os
import openai
from model import ChatRequest 
from db_manager import get_user, get_anonymous_session

app = FastAPI()

load_dotenv()
openai.api_key = os.getenv("SECRET_KEY")

@app.post('/chat')
def generate_response(request: ChatRequest):  
    response = openai.ChatCompletion.create(  
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": request.text}],
        max_tokens=1024,
        n=1,
        temperature=0.3
    )
    
    return response["choices"][0]["message"]["content"]

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