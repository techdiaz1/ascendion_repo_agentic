from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os 
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenRouter(
    model = "deepseek/deepseek-v4.1-flash",api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.1,max_tokens=5000
)
# 
# while True:
    # user_input = input("You: ")
    # if user_input.lower() == "exit":
        # break
    # result = model.invoke(user_input)
    # print("AI: ",result.content)
# 

# Chatbot with memory (LIST)

chat_history = [SystemMessage(content="You are a helpful assistant!")]

while True:
    
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    chat_history.append(HumanMessage(content=user_input))

    result = model.invoke(chat_history)
    chat_history.append(AIMessage(content=result.content))
    print("AI: ",result.content)

print(chat_history)

