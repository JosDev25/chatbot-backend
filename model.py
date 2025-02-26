from pydantic import BaseModel, Field

class Model(BaseModel):
    text: str=Field(min_length=10,max_length=400)
