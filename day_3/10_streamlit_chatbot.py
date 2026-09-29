# streamlit llm chatbot

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os 
from dotenv import load_dotenv
load_dotenv()
import streamlit as st


model = ChatOpenRouter(
    model = "deepseek/deepseek-v4.1-flash",api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.1,max_tokens=5000
)

st.title("LLM Chatbot")

# chat history 

# add the system message to memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful assistant")
    ]

# Display the chat_history ("user" :"content" and "assistant":"content") equivalent
for message in st.session_state.messages:
    if isinstance(message,HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)

    elif isinstance(message,AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# user input and responses 

user_input = st.chat_input("Enter your message :")

if user_input:

    # show user prompt 
    with st.chat_message("user"):
        st.write(user_input)
    # add the user prompt to the memory 
    st.session_state.messages.append(HumanMessage(content=user_input))
    # invoke the llm 
    response = model.invoke(st.session_state.messages)
    # add the ai message to memory 
    st.session_state.messages.append(response)
    #print the response 
    with st.chat_message("assistant"):
        st.write(response.content)

