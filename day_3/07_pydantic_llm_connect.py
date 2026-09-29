from pydantic import BaseModel,EmailStr,Field,AnyUrl
from typing import List,Literal,Dict,Optional,Annotated,TypedDict
import json 
from openrouter import OpenRouter
import os 

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
# user_info = {
    # "name":"demo1",
    # "age" : 25,
    # "salary" : 150000.00,
    # "skills": ["analyst"],
    # "contact_details":{"+919883435":"demo1@gmail.com"},
    # "linkedin_url":"https://linkedin.com/22114"
# }
# 
# user1 = User(**user_info)
# add_user_data(user1) #display the outputs 

user_schema = User.model_json_schema()

user_schema_json = json.dumps(user_schema,indent=2)

# This can come from a user, chatbot, form, resume, etc.
user_input = """
My name is Rahul.
I am 27 years old.
My salary is 120000.
I work as a data analyst.
My skills are Python, SQL and Excel.
I am married.
My email is rahul@gmail.com.
My LinkedIn is https://linkedin.com/in/rahul
"""


# Call DeepSeek through OpenRouter
with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:

    response = client.chat.send(
        model="deepseek/deepseek-v4.1-flash",

        messages=[
            {
                "role": "system",
                "content": f"""
You are a data extraction assistant.

Extract user information from the user's input.

Return ONLY valid JSON.

The JSON must follow this schema:

{user_schema_json}

Do not add any fields that are not present
in the schema.
"""
            },

            {
                "role": "user",
                "content": user_input
            }
        ],max_tokens=5000
    )


# Get DeepSeek's response
llm_output = response.choices[0].message.content

print("\n========== DEEPSEEK OUTPUT ==========")
print(llm_output)








