from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import json
import asyncio

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index_openai.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")

    async def stream_response():
        process = await asyncio.create_subprocess_exec(
            "ollama",
            "run",
            "llama3",
            "--json",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        await process.stdin.write(user_input.encode() + b"\n")
        await process.stdin.drain()
        process.stdin.close()

        async for line in process.stdout:
            try:
                msg = json.loads(line.decode())
                if "response" in msg:
                    yield msg["response"]
            except Exception:
                pass

    return StreamingResponse(stream_response(), media_type="text/plain")


# uvicorn app_openai:app --reload
