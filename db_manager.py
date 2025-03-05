
import hashlib
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

uri = os.getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db=client["chatbot_db"]
users_collection = db["users"]
anonymous_sessions_collection = db["anonymous_sessions"]

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_user(name, email, password, session_id=None):
    existing_user = users_collection.find_one({"email": email})
    
    if existing_user:
        return {"message": "User already exist"}
    
    hashed_password = pwd_context.hash(password)
    
    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password,  
        "api_calls": 0,
        "chats": []
    }
    
    if session_id:
        session = anonymous_sessions_collection.find_one({"session_id": session_id})
        if session and "chats" in session:
            new_user["chats"] = session["chats"] 
            anonymous_sessions_collection.delete_one({"session_id": session_id})  
            
    users_collection.insert_one(new_user)
     
    return {"message": "User created succesfully and chat history transferred" if session_id else "User created"}

def get_user(email):
    user = users_collection.find_one({"email": email}, {"_id": 0})  
    
    if user:
        return user
    else:
        return{"message": "User not found"}
    

def increment_api_calls(email):
    user = users_collection.find_one({"email": email})

    if user:
        users_collection.update_one({"email": email}, {"$inc": {"api_calls": 1}})
        return {"message": "API calls incremented successfully"}
    
    return {"message": "User not found"}

        
def add_anonymous_session(session_id, user_text, bot_text):
    session = anonymous_sessions_collection.find_one({"session_id": session_id})
    
    if session:
        anonymous_sessions_collection.update_one(
            {"session_id": session_id},
            {
                "$inc": {"api_calls": 1},
                "$push": {"chats": {"user": user_text, "bot": bot_text}}
            }
        )
        return {"message": "Anonymous session updated"}
    
    new_session = {
        "session_id": session_id,
        "api_calls": 1,
        "chats": [{"user": user_text, "bot": bot_text}]  
    }
    anonymous_sessions_collection.insert_one(new_session)
    return {"message": "New anonymous session created"}

        
def get_anonymous_session(session_id):
    session = anonymous_sessions_collection.find_one({"session_id": session_id}, {"_id": 0})  
    
    if session:
        return session
    else:
        return {"message": "No session found"}