# Raspberry Pi LLM Chat Assistant

A local AI chat assistant based on Ollama + FastAPI + Qwen3, featuring real-time thinking process visualization.

[中文文档](README.md) | English

## ✨ Features

- 🚀 **Streaming Responses** - Real-time AI reply display
- 🧠 **Thinking Process Visualization** - See how the AI reasons
- 💬 **Interactive Chat Interface** - Clean and modern UI
- 🔄 **Connection Monitoring** - Real-time backend health status
- 📱 **Responsive Design** - Works on mobile and desktop
- 🎯 **Lightweight** - Optimized for Raspberry Pi

## 📁 Project Structure

```
raspberry-pi-llm-assistant/
├── backend/
│   └── main.py              # FastAPI backend service
├── frontend/
│   ├── index.html           # Frontend page
│   ├── styles.css           # Stylesheet
│   └── app.js               # JavaScript logic
├── requirements.txt         # Python dependencies
├── README.md               # Chinese documentation
├── README_EN.md            # English documentation
├── start.sh                # Startup script
└── stop.sh                 # Stop script
```

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi (3/4/5) or any Linux system
- Python 3.8+
- 2GB+ RAM (4GB+ recommended)

### 1. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Qwen3 model
ollama pull qwen3:0.6b
```

**Model Recommendations:**
- `qwen3:0.6b` - Ultra-lightweight, suitable for Raspberry Pi 3/4 (600MB)
- `qwen3:1.8b` - Small, good performance (1.8GB)
- `phi3:mini` - Alternative option (3.8GB)
- `qwen3:7b` - Best quality, requires Raspberry Pi 5 or better (7GB)

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Services

#### Option 1: One-Click Startup (Recommended)

```bash
chmod +x start.sh stop.sh
./start.sh
```

#### Option 2: Manual Startup

```bash
# Terminal 1 - Start backend
cd backend
python main.py

# Terminal 2 - Start frontend
cd frontend
python3 -m http.server 3000
```

### 4. Access the Application

Open your browser and visit:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

For network access from other devices:
- Replace `localhost` with your Raspberry Pi's IP address
- Example: `http://192.168.1.100:3000`

### 5. Stop Services

```bash
./stop.sh
```

Or press `Ctrl+C` in the terminal.

## 📡 API Reference

### POST `/api/chat`
Send a chat message

**Request Body:**
```json
{
  "message": "Hello",
  "model": "qwen3:0.6b",
  "stream": true
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"thinking": "reasoning content", "response": "reply content"}
data: {"response": "more content"}
data: [DONE]
```

### GET `/api/models`
Get list of available models

**Response:**
```json
{
  "models": [
    {
      "name": "qwen3:0.6b",
      "modified_at": "2024-01-01T00:00:00Z",
      "size": 600000000
    }
  ]
}
```

### GET `/api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "ollama": "connected"
}
```

### POST `/api/chat/history`
Chat with conversation history (reserved for future use)

## ⚙️ Configuration

### Change Default Model

Edit `backend/main.py`:
```python
DEFAULT_MODEL = "qwen3:0.6b"  # Change to your preferred model
```

### Change Ports

**Backend Port** (in `backend/main.py`):
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000 to your port
```

**Frontend Port** (when starting HTTP server):
```bash
python3 -m http.server 3000  # Change 3000 to your port
```

### CORS Configuration

To restrict access origins, modify CORS settings in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 Performance Optimization

### 1. Choose the Right Model

Different models for different hardware:

| Model | Size | Best For | Performance |
|-------|------|----------|-------------|
| qwen3:0.6b | 600MB | RPi 3/4 | Fast, basic quality |
| qwen3:1.8b | 1.8GB | RPi 4 | Balanced |
| phi3:mini | 3.8GB | RPi 4/5 | Good quality |
| qwen3:7b | 7GB | RPi 5+ | Best quality |

### 2. Increase Swap Space

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 3. Optimize Ollama Parameters

Create a custom model configuration:
```
FROM qwen3:0.6b
PARAMETER num_ctx 2048
PARAMETER num_thread 4
PARAMETER temperature 0.7
```

Save as `modelfile` and load:
```bash
ollama create mymodel -f modelfile
```

### 4. System Optimization

```bash
# Increase GPU memory (edit /boot/config.txt)
gpu_mem=128

# Overclock (Raspberry Pi 4)
over_voltage=6
arm_freq=2000
```

## 🐛 Troubleshooting

### Issue 1: CORS Error

**Symptoms:** Browser console shows CORS policy error

**Solution:**
- Ensure CORS is properly configured in backend
- Use same-origin access (serve frontend through FastAPI)
- Or disable browser security for testing (not recommended for production)

### Issue 2: Ollama Connection Failed

**Symptoms:** Backend shows "disconnected" status

**Solution:**
```bash
# Check Ollama service status
systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# Check if Ollama is listening
curl http://localhost:11434/api/tags
```

### Issue 3: Thinking Content Not Displayed

**Symptoms:** Only responses show, no thinking process

**Solution:**
- Verify the model supports reasoning output
- Check browser console for network errors
- Some models may not output thinking process
- Try a different model that explicitly supports reasoning

### Issue 4: Slow Response Time

**Symptoms:** AI takes too long to respond

**Solution:**
- Use a smaller model (qwen3:0.6b instead of 7b)
- Increase swap space
- Close other applications to free up memory
- Consider upgrading to Raspberry Pi 5
- Reduce context window size

### Issue 5: Out of Memory

**Symptoms:** Application crashes or system becomes unresponsive

**Solution:**
```bash
# Monitor memory usage
free -h
htop

# Increase swap as shown above
# Use smaller model
# Reduce num_ctx parameter
```

### Issue 6: Port Already in Use

**Symptoms:** Error: "Address already in use"

**Solution:**
```bash
# Find process using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Kill the process
kill -9 <PID>

# Or change ports in configuration
```

## 🎨 Customization

### Change Theme Colors

Edit `frontend/styles.css`:
```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* User message color */
.message.user .response-box {
    background: #667eea;  /* Change this */
}
```

### Add New Features

1. **Message History Storage**: Implement localStorage or backend database
2. **Multi-Model Selector**: Add dropdown to switch models
3. **Voice Input**: Integrate Web Speech API
4. **File Upload**: Support document analysis
5. **Export Chat**: Add export to PDF/TXT functionality

### Modify UI Layout

The responsive breakpoint is at 768px. Edit in `frontend/styles.css`:
```css
@media (max-width: 768px) {
    /* Mobile styles */
}
```

## 📊 System Requirements

### Minimum Requirements
- Raspberry Pi 3B+ or better
- 2GB RAM
- 8GB storage (including OS)
- Internet connection (for initial model download)

### Recommended Requirements
- Raspberry Pi 4/5
- 4GB+ RAM
- 16GB+ storage
- Active cooling

### Network Requirements
- Initial setup: Internet connection required
- Runtime: Completely offline capable after model download

## 🔒 Security Considerations

### For Production Use

1. **Enable Authentication**: Add JWT or OAuth2
2. **Use HTTPS**: Set up SSL/TLS certificates
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Sanitize user inputs
5. **CORS Restrictions**: Limit to specific origins

Example with basic auth:
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.post("/api/chat")
async def chat(
    chat_msg: ChatMessage,
    credentials: HTTPBasicCredentials = Depends(security)
):
    # Verify credentials
    # ... existing code
```

## 📈 Monitoring and Logging

### Enable Logging

Add to `backend/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor System Resources

```bash
# CPU and Memory
htop

# Temperature
vcgencmd measure_temp

# Disk usage
df -h
```

## 🚀 Deployment Options

### Option 1: Local Network Access

No additional setup needed - just use your Raspberry Pi's local IP.

### Option 2: Internet Access (Ngrok)

```bash
# Install ngrok
sudo snap install ngrok

# Expose backend
ngrok http 8000
```

### Option 3: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "main.py"]
```

### Option 4: Systemd Service

Create `/etc/systemd/system/llm-assistant.service`:
```ini
[Unit]
Description=LLM Assistant Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/raspberry-pi-llm-assistant/backend
ExecStart=/home/pi/raspberry-pi-llm-assistant/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable llm-assistant
sudo systemctl start llm-assistant
```

## 📝 Development Roadmap

- [ ] Multi-user support with authentication
- [ ] Conversation history persistence (SQLite/PostgreSQL)
- [ ] Multi-model switching in UI
- [ ] Voice input/output support
- [ ] Document upload and analysis
- [ ] Mobile app (React Native)
- [ ] Docker compose deployment
- [ ] Metrics and analytics dashboard
- [ ] Plugin system for extensions
- [ ] Multilingual support

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Add comments for complex logic
- Update documentation for new features
- Test on actual Raspberry Pi hardware when possible

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Qwen](https://github.com/QwenLM/Qwen) - Alibaba's open-source LLM
- The Raspberry Pi community

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/raspberry-pi-llm-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/raspberry-pi-llm-assistant/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/raspberry-pi-llm-assistant/wiki)

## 🌟 Star History

If you find this project helpful, please consider giving it a star! ⭐

---

**Made with ❤️ for the Raspberry Pi community**