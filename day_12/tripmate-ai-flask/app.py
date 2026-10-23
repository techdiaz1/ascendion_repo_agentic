from pathlib import Path
import traceback
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend import run_travel_agent

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="TripMate AI",
    description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
    version="1.0.0"
)

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        # Await the async backend function safely
        result = await run_travel_agent(
            user_input=request_data.message,
            thread_id=request_data.thread_id,
        )

        return JSONResponse(content={
            "success": True,
            "thread_id": result["thread_id"],
            "answer": result["answer"],
            "flight_results": result.get("flight_results", ""),
            "hotel_results": result.get("hotel_results", ""),
            "weather_results": result.get("weather_results", ""),
            "itinerary": result.get("itinerary", ""),
            "llm_calls": result.get("llm_calls", 0),
        })

    except Exception as e:
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )