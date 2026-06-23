# Quick Start Guide - Think2Seg Demo

## 🚀 Fastest Path to Running

### Prerequisites Check
- [ ] Python 3.10+
- [ ] Node.js 18+ (or just use Docker)
- [ ] NVIDIA GPU with CUDA 12.2+ (or use CPU, slower)
- [ ] 50GB free disk space
- [ ] 16GB RAM minimum

### Method 1: Docker (Easiest - 5 minutes)

```bash
cd c:\Users\lwj_n\Projects\ISR\Think2Seg-Demo

# Start everything
docker-compose up --build

# Wait for startup (first run ~10 min for model download)
# Then open: http://localhost:3000
```

**That's it!** The frontend will open, use it to upload satellite images and segment them.

### Method 2: Local Development (15 minutes)

#### Terminal 1 - Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000 (or http://localhost:5173 if local dev)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 What to Expect First Run

1. **Backend Startup** (2-10 minutes)
   - Downloads Think2Seg-RS model from HuggingFace
   - Loads SAM2 model
   - Initializes CUDA/GPU
   - Shows "Model Ready" in console

2. **Frontend Ready** (1 minute)
   - Vue.js app compiles
   - Connects to backend
   - Shows "✓ Model Ready"

3. **Test It**
   - Upload a satellite image
   - Type: "buildings"
   - Click "✨ Segment Image"
   - Wait 2-5 seconds
   - See highlighted buildings!

## 🎮 Usage Examples

### Example 1: Urban Buildings
1. Upload urban satellite image
2. Prompt: "buildings in urban areas"
3. Result: Red overlay on buildings

### Example 2: Forest Segmentation
1. Upload forest/vegetation image
2. Prompt: "forest coverage and vegetation"
3. Result: Segmented forest areas

### Example 3: Water Detection
1. Upload water/lakes image
2. Prompt: "water bodies and lakes"
3. Result: Identified water regions

## ⚙️ Configuration Quick Reference

**Adjust model size** (faster but less accurate):
- Edit `backend/.env`
- Change: `SAM2_MODEL_SIZE=tiny` (was: base_plus)
- Restart backend

**Adjust image size** (faster but lower quality):
- Edit `backend/.env`
- Change: `MAX_IMAGE_SIZE=512` (was: 1024)
- Restart backend

**Use CPU instead of GPU** (much slower):
- Edit `backend/.env`
- Change: `DEVICE=cpu`
- Restart backend

## 🆘 Common Issues

**"Address already in use"**
- Port 3000 or 8000 taken
- Solution: `docker-compose down` or kill using processes

**"Model download fails"**
- No internet or HuggingFace down
- Solution: Check internet, wait, retry

**"Out of memory"**
- GPU VRAM too low (<8GB)
- Solution: Use smaller model or reduce image size

**"Frontend can't connect to backend"**
- CORS issue or backend not running
- Solution: Check backend is running at http://localhost:8000/health

## 📊 Performance Guide

| Setting | Speed | Quality | VRAM |
|---------|-------|---------|------|
| SAM2 tiny | ⚡⚡ | ⭐⭐ | 4GB |
| SAM2 small | ⚡ | ⭐⭐⭐ | 6GB |
| SAM2 base_plus | 🟡 | ⭐⭐⭐⭐ | 10GB |
| SAM2 large | 🟠 | ⭐⭐⭐⭐⭐ | 16GB |

Default is `base_plus` - good balance.

## 📁 Important Files

- `backend/main.py` - API server
- `backend/inference.py` - Model inference
- `backend/.env` - Configuration
- `frontend/src/App.vue` - UI component

## 🔗 API Examples

```bash
# Check if backend is ready
curl http://localhost:8000/health

# Segment image with curl
curl -X POST "http://localhost:8000/segment" \
  -F "file=@myimage.jpg" \
  -F "prompt=buildings"

# View API docs
open http://localhost:8000/docs
```

## 📚 Learn More

- See `README.md` for full documentation
- Backend logs: `docker-compose logs -f backend`
- Frontend console: Browser DevTools (F12)
- API docs: `http://localhost:8000/docs`

## ✅ Verification Checklist

- [ ] Backend running: `curl http://localhost:8000/health` returns `200`
- [ ] Frontend running: Browser shows Think2Seg UI
- [ ] Model loaded: Console shows "✓ Model Ready"
- [ ] Can upload image
- [ ] Can type prompt
- [ ] Segmentation button works
- [ ] Results display after 2-5 seconds

## 🎉 Ready to Go!

You're all set! Enjoy exploring satellite image segmentation with natural language! 🛰️

---

**Need help?** Check README.md Troubleshooting section or check backend logs.
