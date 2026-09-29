from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from dotenv import load_dotenv
import psycopg2
import os
import uuid


load_dotenv()

app = FastAPI()


# LLM
model = ChatOpenRouter(
    model="deepseek/deepseek-v4.1-flash",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.1,
    max_tokens=5000
)


# PostgreSQL
def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# Create tables
conn = db()
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id UUID PRIMARY KEY,
        title TEXT
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        chat_id UUID,
        role TEXT,
        content TEXT
    )
""")

conn.commit()
conn.close()


class ChatRequest(BaseModel):
    chat_id: str
    message: str


# New chat
@app.post("/new-chat")
def new_chat():

    chat_id = str(uuid.uuid4())

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chats VALUES (%s, %s)",
        (chat_id, "New Chat")
    )

    conn.commit()
    conn.close()

    return {"chat_id": chat_id}


# Previous chats
@app.get("/chats")
def chats():

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title FROM chats ORDER BY id DESC"
    )

    data = cur.fetchall()

    conn.close()

    return [
        {"chat_id": str(x[0]), "title": x[1]}
        for x in data
    ]


# Messages of one chat
@app.get("/chats/{chat_id}")
def messages(chat_id: str):

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content
        FROM messages
        WHERE chat_id = %s
        ORDER BY id
        """,
        (chat_id,)
    )

    data = cur.fetchall()

    conn.close()

    return [
        {"role": x[0], "content": x[1]}
        for x in data
    ]


# Chat + streaming
@app.post("/chat")
def chat(request: ChatRequest):

    conn = db()
    cur = conn.cursor()

    # Get history
    cur.execute(
        """
        SELECT role, content
        FROM messages
        WHERE chat_id = %s
        ORDER BY id
        """,
        (request.chat_id,)
    )

    history = cur.fetchall()
    conn.close()


    # Convert PostgreSQL history
    # to LangChain messages

    messages = [
        SystemMessage(
            content="You are a helpful assistant."
        )
    ]

    for role, content in history:

        if role == "user":
            messages.append(
                HumanMessage(content=content)
            )
        else:
            messages.append(
                AIMessage(content=content)
            )


    messages.append(
        HumanMessage(content=request.message)
    )


    # Stream response
    def generate():

        answer = ""

        for chunk in model.stream(messages):

            if chunk.content:

                answer += chunk.content

                yield chunk.content


        # Save conversation
        conn = db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO messages
            VALUES (DEFAULT, %s, %s, %s)
            """,
            (
                request.chat_id,
                "user",
                request.message
            )
        )

        cur.execute(
            """
            INSERT INTO messages
            VALUES (DEFAULT, %s, %s, %s)
            """,
            (
                request.chat_id,
                "assistant",
                answer
            )
        )


        # First message becomes title
        if not history:

            cur.execute(
                """
                UPDATE chats
                SET title = %s
                WHERE id = %s
                """,
                (
                    request.message[:30],
                    request.chat_id
                )
            )


        conn.commit()
        conn.close()


    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )


# UI
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/")
def home():

    return FileResponse(
        "static/index.html"
    )
