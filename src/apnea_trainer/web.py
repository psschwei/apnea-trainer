from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from pathlib import Path
from .timer import parse_time, format_time, apply_delta, load_config
import uuid
from typing import Dict, Optional

app = FastAPI(title="Apnea Trainer")

# Set up templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# Store active sessions
active_sessions: Dict[str, dict] = {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Load config file
    config = load_config()
    if config:
        # Format times for display
        default_config = {
            "training_time": format_time(*parse_time(str(config["training"]["initial_length"]))),
            "training_delta": format_time(*parse_time(str(config["training"]["delta"]))),
            "rest_time": format_time(*parse_time(str(config["rest"]["initial_length"]))),
            "rest_delta": format_time(*parse_time(str(config["rest"]["delta"]))),
            "rounds": str(config["session"]["rounds"])
        }
    else:
        # Fallback defaults if config file is not found
        default_config = {
            "training_time": "1:30",
            "training_delta": "-0:05",
            "rest_time": "0:30",
            "rest_delta": "-0:02",
            "rounds": "5"
        }
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "config": default_config
    })

@app.post("/session/start")
async def start_session(config: dict, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    
    # Parse configuration
    training_time = parse_time(config["training_time"])
    training_delta = parse_time(config["training_delta"])
    rest_time = parse_time(config["rest_time"])
    rest_delta = parse_time(config["rest_delta"])
    rounds = int(config["rounds"])
    
    # Create session
    active_sessions[session_id] = {
        "is_running": True,
        "current_round": 1,
        "total_rounds": rounds,
        "training_time": training_time,
        "training_delta": training_delta,
        "rest_time": rest_time,
        "rest_delta": rest_delta,
        "event_queue": asyncio.Queue()
    }
    
    # Start the session in the background
    background_tasks.add_task(run_session, active_sessions[session_id])
    
    return {"session_id": session_id}

@app.post("/session/{session_id}/stop")
async def stop_session(session_id: str):
    if session_id in active_sessions:
        session = active_sessions[session_id]
        session["is_running"] = False
        await session["event_queue"].put({
            "type": "status",
            "message": "Session stopped"
        })
        return {"status": "stopped"}
    return {"status": "not_found"}

@app.get("/session/{session_id}/events")
async def get_events(session_id: str):
    if session_id not in active_sessions:
        return {"error": "Session not found"}
    
    session = active_sessions[session_id]
    
    async def event_generator():
        try:
            while session["is_running"]:
                event = await session["event_queue"].get()
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "session_complete":
                    # Wait a bit to ensure the event is processed
                    await asyncio.sleep(1)
                    break
        finally:
            # Only delete if the session was stopped externally
            if session_id in active_sessions and not session["is_running"]:
                del active_sessions[session_id]
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.post("/session/{session_id}/complete")
async def session_complete(session_id: str):
    if session_id in active_sessions:
        session = active_sessions[session_id]
        session["is_running"] = False
        await session["event_queue"].put({
            "type": "session_complete",
            "message": "All rounds completed!"
        })
        return {"status": "complete"}
    return {"status": "not_found"}

async def run_session(session):
    try:
        while session["is_running"] and session["current_round"] <= session["total_rounds"]:
            # Calculate current round times
            current_training = apply_delta(
                *session["training_time"],
                session["training_delta"][0] * (session["current_round"] - 1),
                session["training_delta"][1] * (session["current_round"] - 1)
            )
            current_rest = apply_delta(
                *session["rest_time"],
                session["rest_delta"][0] * (session["current_round"] - 1),
                session["rest_delta"][1] * (session["current_round"] - 1)
            )
            
            # Training round
            await session["event_queue"].put({
                "type": "round_start",
                "round": session["current_round"],
                "total_rounds": session["total_rounds"],
                "time": format_time(*current_training),
                "phase": "training"
            })
            
            # Countdown training
            total_seconds = current_training[0] * 60 + current_training[1]
            while total_seconds > 0 and session["is_running"]:
                mins, secs = divmod(total_seconds, 60)
                await session["event_queue"].put({
                    "type": "tick",
                    "time": format_time(mins, secs),
                    "phase": "training"
                })
                await asyncio.sleep(1)
                total_seconds -= 1
            
            if not session["is_running"]:
                break
                
            # Show 00:00 before transition
            await session["event_queue"].put({
                "type": "tick",
                "time": "00:00",
                "phase": "training"
            })
                
            # Rest period
            await session["event_queue"].put({
                "type": "phase_change",
                "phase": "rest",
                "time": format_time(*current_rest)
            })
            
            # Countdown rest
            total_seconds = current_rest[0] * 60 + current_rest[1]
            while total_seconds > 0 and session["is_running"]:
                mins, secs = divmod(total_seconds, 60)
                await session["event_queue"].put({
                    "type": "tick",
                    "time": format_time(mins, secs),
                    "phase": "rest"
                })
                await asyncio.sleep(1)
                total_seconds -= 1
            
            if not session["is_running"]:
                break
                
            # Show 00:00 before transition
            await session["event_queue"].put({
                "type": "tick",
                "time": "00:00",
                "phase": "rest"
            })
                
            # End of rest period
            await session["event_queue"].put({
                "type": "phase_change",
                "phase": "training",
                "time": format_time(*current_training)
            })
            
            session["current_round"] += 1
            
            # If this was the last round, send completion event
            if session["current_round"] > session["total_rounds"]:
                await session["event_queue"].put({
                    "type": "completion",
                    "message": "Session complete!"
                })
                break
            
        # Session is done
        session["is_running"] = False
            
    except Exception as e:
        print(f"Error in session: {e}")
        session["is_running"] = False 