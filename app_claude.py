from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx
import json
from typing import Optional

app = FastAPI(title="树莓派 LLM 助手")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama API配置
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:0.6B"  # 使用qwen3模型


class ChatMessage(BaseModel):
    message: str
    model: Optional[str] = DEFAULT_MODEL
    stream: Optional[bool] = True


class ChatHistory(BaseModel):
    messages: list
    model: Optional[str] = DEFAULT_MODEL


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index_claude.html", {"request": request})


@app.post("/chat")
async def chat(chat_msg: ChatMessage):
    """处理聊天请求，支持流式响应，包含思考过程"""
    try:

        async def generate():
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "model": chat_msg.model,
                    "prompt": chat_msg.message,
                    "stream": True,
                }

                async with client.stream(
                    "POST", f"{OLLAMA_BASE_URL}/api/generate", json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)

                                # 构建返回数据，包含思考和响应
                                result = {}

                                # 检查是否有思考内容（reasoning字段）
                                if "reasoning" in data and data["reasoning"]:
                                    result["thinking"] = data["reasoning"]

                                # 检查是否有响应内容
                                if "response" in data and data["response"]:
                                    result["response"] = data["response"]

                                # 如果有内容，发送给前端
                                if result:
                                    yield f"data: {json.dumps(result)}\n\n"

                            except json.JSONDecodeError:
                                continue

            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """获取可用的模型列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                return {"status": "healthy", "ollama": "connected"}
    except:
        pass
    return {"status": "unhealthy", "ollama": "disconnected"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
