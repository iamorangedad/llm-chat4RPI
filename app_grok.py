from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import ollama
import json
import asyncio

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


MODEL = "qwen3:0.6B"


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index_grok.html", {"request": request})


async def stream_response(messages):
    try:
        stream = ollama.chat(
            model=MODEL,
            messages=messages,
            stream=True,
            options={
                "temperature": 0.7,
                "num_predict": 128,
            },
        )
        for chunk in stream:
            content = chunk["message"]["content"]
            yield json.dumps({"content": content}, ensure_ascii=False) + "\n"
            await asyncio.sleep(0)
    except Exception as e:
        yield json.dumps({"content": f"[错误] {str(e)}"}) + "\n"


@app.post("/chat")
async def chat(user_input: str = Form(...), history: str = Form("[]")):
    try:
        messages = json.loads(history)
    except:
        messages = []

    if len(messages) > 20:
        messages = messages[-10:]

    messages.append({"role": "user", "content": user_input})

    return StreamingResponse(stream_response(messages), media_type="text/event-stream")


# uvicorn app_grok:app --host 0.0.0.0 --reload
