from fastapi import FastAPI
from dotenv import load_dotenv
import os
import openai
from model import Model

app = FastAPI()

load_dotenv()


openai.api_key = os.getenv("SECRET_KEY")


@app.post('/chat')
def generate_response(prompt: Model):
    response = openai.ChatCompletion.create(  
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt.text}],
        max_tokens=1024,
        n=1,
        temperature=0.3
    )
    
    return response["choices"][0]["message"]["content"]
