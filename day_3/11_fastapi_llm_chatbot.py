# fastapi llm chatbot
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List
import os 
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel


#initialize fastapi 
app = FastAPI()

# define the model 
model = ChatOpenRouter(
    model = "deepseek/deepseek-v4.1-flash",api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.1,max_tokens=5000
)

# create memory for conversation history 
chat_history = {}

# request model 
class ChatRequest(BaseModel):
    session_id : str 
    message : str 

# response model 
class ChatResponse(BaseModel):
    session_id : str 
    message : str 
    chat_history1 : List

@app.get("/")
def read_data():
    return {"message":"hello world"}

#chat endpoint 
@app.post("/chat",response_model=ChatResponse)
def chat(request: ChatRequest):

    if request.session_id not in chat_history:
        chat_history[request.session_id] = [
            SystemMessage(content="You are a helpful assistant")
        ]
    messages = chat_history[request.session_id] # extract the system message from the chat history 

    # add the user's prompt to the messages
    messages.append(HumanMessage(content=request.message)) 

    # we now have system message,human message, let us send it to the LLM to invoke 

    response = model.invoke(messages)

    # add the response/AI message to the memory/conversation history 
    messages.append(AIMessage(content=response.content))

    # Print the response/ output of LLM invoke 
    return ChatResponse(session_id=request.session_id,message=response.content,chat_history1=messages)




