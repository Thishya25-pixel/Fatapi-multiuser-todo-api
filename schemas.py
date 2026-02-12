from pydantic import BaseModel,ConfigDict,Field

class TodoCreate(BaseModel):
    title:str

class TodoResponse(BaseModel):
    id:int
    title:str
    completed:bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username:str
    password:str= Field(min_length=4, max_length=72)

class UserResponse(BaseModel):
    id:int
    username:str

    model_config = ConfigDict(from_attributes=True)






