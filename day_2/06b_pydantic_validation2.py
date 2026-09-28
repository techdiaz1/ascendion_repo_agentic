from pydantic import BaseModel,EmailStr,Field,AnyUrl
from typing import List,Literal,Dict,Optional,Annotated,TypedDict

# class Contact(TypedDict): # if we need multiple contact_details to be added, a new class for contact is a better option 
    # phone : str
    # email : EmailStr

class User(BaseModel):
    name : Annotated[str,Field(max_length=20,title="Name of the user",
        description="Give name of the user in 20 characters or less", 
        examples = ["nitish","amit","hari"])]
    age : int | None = Field(default=None,ge=22,strict=True)
    salary : float = Field(gt=0)
    skills : Optional[List[str]] = None
    married : Annotated[Optional[bool] ,Field(description="Is the user married or not")] = None
    contact_details : Dict[str,EmailStr]
    # contact_details : Contact #if loading multiple data from contact
    linkedin_url : AnyUrl

def add_user_data(user:User):
    print("Name :",user.name)
    print("age :",user.age)
    print("salary :",user.salary)
    print("skills :",user.skills)
    print("married :",user.married)
    print("contact details :",user.contact_details)
    print("LinkedIn :",user.linkedin_url)
    print("User data validated and added!")

# input data 
user_info = {
    "name":"demo1",
    "age" : 25,
    "salary" : 150000.00,
    "skills": ["analyst"],
    "contact_details":{"+919883435":"demo1@gmail.com"},
    "linkedin_url":"https://linkedin.com/22114"
}

user1 = User(**user_info)
add_user_data(user1) #display the outputs 
