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
    
    

