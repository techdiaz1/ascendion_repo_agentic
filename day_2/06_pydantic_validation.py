# create a pydantic validation example similar to 05_json_schem_validation (its much easier to do the same with pydantic)
# pydantic returns errors with all details clearly mentioned without us printing the error statements 
from pydantic import BaseModel,Field,EmailStr
from typing import Literal,List,Dict

class User(BaseModel):
    name : str = Field(min_length=3,title="User name")
    age : int | None = Field(default=None,ge=22)
    email : EmailStr
    role : Literal["developer","designer","manager"]
    gender : bool   # 1 - male , 0 - female 

data = {
    "name" : "Arib",
    "age" : "27",
    "email" : "demo@ascendion.com",
    "role":"developer",
    "gender":1
}

user = User(**data)  #pass data as kwargs to unpacking the dictionary
print(user)

print(user.model_json_schema()) # creates a json schema similar to what was created in 05_schema