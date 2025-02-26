import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv


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

def add_user(name, email):
    existing_user=users_collection.find_one({"email": email})
    
    if existing_user:
        return {"message": "User already exist"}
    new_user={
        "name": name,
        "email": email,
        "api_calls": 0,
        "chats": []
    }
    
    users_collection.insert_one(new_user)
    
    return{"message": "User created succesfully"}

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

        
def add_anonymous_session(session_id):
    session=anonymous_sessions_collection.find_one({"session_id": session_id})
    
    if session:
        anonymous_sessions_collection.update_one({"session_id": session_id}, {"$inc": {"api_calls": 1}})
        return {"message": "Anonymous session API calls incremented"}
    
    new_session={
        "session_id": session_id,
        "api_calls": 1
    }
    anonymous_sessions_collection.insert_one(new_session)
    return {"message": "New anonymous session created"}


        
def get_anonymous_session(session_id):
    session = anonymous_sessions_collection.find_one({"session_id": session_id}, {"_id": 0})  
    
    if session:
        return session
    else:
        return {"message": "No session found"}