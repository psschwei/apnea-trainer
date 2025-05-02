from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from pathlib import Path
from .timer import parse_time, format_time, apply_delta, load_config
import uuid
from fastapi import WebSocketDisconnect

app = FastAPI(title="Apnea Trainer")

# Set up templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# Store active sessions
active_sessions = {}

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "websocket": websocket,
        "is_running": False,
        "current_round": 1,
        "total_rounds": 0,
        "training_time": (0, 0),
        "training_delta": (0, 0),
        "rest_time": (0, 0),
        "rest_delta": (0, 0),
        "task": None
    }
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "start":
                # Parse configuration
                training_time = parse_time(data["config"]["training_time"])
                training_delta = parse_time(data["config"]["training_delta"])
                rest_time = parse_time(data["config"]["rest_time"])
                rest_delta = parse_time(data["config"]["rest_delta"])
                rounds = int(data["config"]["rounds"])
                
                # Update session
                session = active_sessions[session_id]
                session["is_running"] = True
                session["current_round"] = 1
                session["total_rounds"] = rounds
                session["training_time"] = training_time
                session["training_delta"] = training_delta
                session["rest_time"] = rest_time
                session["rest_delta"] = rest_delta
                
                # Start the session in a new task
                session["task"] = asyncio.create_task(run_session(session))
                
            elif data["action"] == "stop":
                # Stop the session
                session = active_sessions[session_id]
                session["is_running"] = False
                if session["task"]:
                    session["task"].cancel()
                    try:
                        await session["task"]
                    except asyncio.CancelledError:
                        pass
                # Send a final status message
                await websocket.send_json({
                    "type": "status",
                    "message": "Session stopped"
                })
                
    except WebSocketDisconnect:
        if session_id in active_sessions:
            session = active_sessions[session_id]
            if session["task"]:
                session["task"].cancel()
            del active_sessions[session_id]
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
        if session_id in active_sessions:
            session = active_sessions[session_id]
            if session["task"]:
                session["task"].cancel()
            del active_sessions[session_id]

async def run_session(session):
    websocket = session["websocket"]
    
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
            await websocket.send_json({
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
                await websocket.send_json({
                    "type": "tick",
                    "time": format_time(mins, secs),
                    "phase": "training"
                })
                await asyncio.sleep(1)
                total_seconds -= 1
            
            if not session["is_running"]:
                break
                
            # Show 00:00 before transition
            await websocket.send_json({
                "type": "tick",
                "time": "00:00",
                "phase": "training"
            })
                
            # Rest period
            await websocket.send_json({
                "type": "phase_change",
                "phase": "rest",
                "time": format_time(*current_rest)
            })
            
            # Countdown rest
            total_seconds = current_rest[0] * 60 + current_rest[1]
            while total_seconds > 0 and session["is_running"]:
                mins, secs = divmod(total_seconds, 60)
                await websocket.send_json({
                    "type": "tick",
                    "time": format_time(mins, secs),
                    "phase": "rest"
                })
                await asyncio.sleep(1)
                total_seconds -= 1
            
            if not session["is_running"]:
                break
                
            # Show 00:00 before transition
            await websocket.send_json({
                "type": "tick",
                "time": "00:00",
                "phase": "rest"
            })
                
            # End of rest period
            await websocket.send_json({
                "type": "phase_change",
                "phase": "training",
                "time": format_time(*current_training)
            })
                
            session["current_round"] += 1
        
        if session["is_running"]:
            await websocket.send_json({
                "type": "session_complete",
                "message": "All rounds completed!"
            })
            session["is_running"] = False
    except asyncio.CancelledError:
        session["is_running"] = False
        raise 