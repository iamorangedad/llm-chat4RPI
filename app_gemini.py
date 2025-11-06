import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 定义 Ollama 服务的 URL
OLLAMA_API_URL = "http://localhost:11434/api/chat"

# 初始化 FastAPI 应用
app = FastAPI()

# --- 配置 CORS (跨域资源共享) ---
# 这是至关重要的一步。因为你的前端 (HTML) 和后端 (FastAPI)
# 运行在不同的 "源" (origin) 上，浏览器会阻止它们通信，
# 除非后端明确允许。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源 (为了简单起见)
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头部
)
# ---------------------------------


# Pydantic 模型，用于验证请求体
# 我们期望前端发送一个包含 "prompt" 字段的 JSON
class ChatRequest(BaseModel):
    prompt: str
    model: str = "qwen3:0.6B"  # 允许前端指定模型，默认为 llama3


@app.get("/")
async def get_index():
    return FileResponse("templates/index_gemini.html")


# 定义一个 POST 端点 "/api/chat"
@app.post("/api/chat")
async def chat_with_ollama(request: ChatRequest):
    """
    接收前端的聊天请求，转发给 Ollama，并返回模型的响应。
    """

    # 构建发送给 Ollama 的数据
    # 注意：Ollama 的 /api/chat 接受一个消息列表
    ollama_data = {
        "model": request.model,
        "messages": [{"role": "user", "content": request.prompt}],
        "stream": False,  # 为简单起见，我们不使用流式响应
    }

    # 使用 httpx 异步发送请求到 Ollama
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_API_URL, json=ollama_data)

            # 检查 Ollama 是否返回了错误
            response.raise_for_status()

            response_data = response.json()

            # 提取模型返回的具体内容
            # 根据 Ollama 的 API 格式，内容在 response_data['message']['content']
            bot_response = response_data.get("message", {}).get("content", "")

            return {"response": bot_response}

    except httpx.HTTPStatusError as e:
        # 处理 Ollama API 返回的错误
        return {"error": f"Ollama API error: {e}"}
    except httpx.RequestError as e:
        # 处理连接到 Ollama 的错误 (比如 Ollama 没运行)
        return {"error": f"Failed to connect to Ollama: {e}"}
    except Exception as e:
        # 处理其他意外错误
        return {"error": f"An unexpected error occurred: {e}"}


# 一个简单的根端点，用来测试服务器是否在运行
@app.get("/")
def read_root():
    return {"message": "Local LLM Chat API is running!"}


# uvicorn app_gemini:app --reload
