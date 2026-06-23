# Think2Seg Demo - Architecture & Technical Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                                                                   │
│  React/Vue Frontend (port 3000)                                  │
│  ├─ Image Upload (Drag & Drop)                                   │
│  ├─ Natural Language Input Form                                  │
│  ├─ Real-time Results Display                                    │
│  └─ Download Manager                                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                          HTTP/REST API
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                        API SERVER LAYER                          │
│                                                                   │
│  FastAPI Backend (port 8000)                                     │
│  ├─ /segment - Single image segmentation                         │
│  ├─ /segment-multiple - Batch processing                         │
│  ├─ /health - Health monitoring                                  │
│  ├─ /status - Model status check                                 │
│  ├─ /docs - Swagger documentation                                │
│  └─ /config - Configuration info                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                   INFERENCE & PROCESSING                         │
│                                                                   │
│  Think2SegInference (inference.py)                               │
│  ├─ Image Preprocessing                                          │
│  │  └─ Resize, Normalize, Tensor conversion                      │
│  ├─ Model Inference                                              │
│  │  ├─ Qwen-2.5-VL: Semantic reasoning                           │
│  │  └─ SAM2: Geometric segmentation                              │
│  └─ Post-processing                                              │
│     ├─ Mask generation                                           │
│     ├─ Visualization overlay                                     │
│     └─ Result encoding (Base64)                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                      ML MODELS (GPU/CUDA)                        │
│                                                                   │
│  🚀 Think2Seg-RS (7B or 3B variant)                              │
│  │  └─ Multimodal LVLM (Language + Vision)                       │
│  │     ├─ Input: Satellite image + Natural language prompt       │
│  │     └─ Output: Spatial reasoning/feature maps                 │
│  │                                                               │
│  📍 SAM2 (Segment Anything Model 2)                              │
│  │  └─ Geometric segmentation                                    │
│  │     ├─ Input: Image + prompt points/boxes from Qwen           │
│  │     └─ Output: Binary segmentation mask                       │
│  │                                                               │
│  💾 Model Sizes:                                                  │
│  │  ├─ Think2Seg-RS-3B: ~6GB VRAM, faster                        │
│  │  ├─ Think2Seg-RS-7B: ~12GB VRAM, more accurate                │
│  │  └─ SAM2 sizes: tiny, small, base_plus, large                 │
│  │                                                               │
│  🔧 Inference Configuration:                                     │
│     ├─ Device: CUDA/CPU                                          │
│     ├─ Precision: bfloat16, float32                              │
│     ├─ Cache: KV-cache, model cache                              │
│     └─ Optimization: vLLM support (optional)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Single Segmentation Request

```
1. USER UPLOADS IMAGE
   └─ File browser/Drag & drop
   └─ Validation (size, format)
   └─ Base64 encoding

2. FRONTEND SENDS REQUEST
   └─ POST /api/segment
   └─ Form data: file + prompt

3. BACKEND RECEIVES
   └─ File validation
   └─ Temporary storage

4. PREPROCESSING
   └─ Load PIL Image
   └─ Resize (max 1024x1024)
   └─ Normalize RGB values

5. TOKENIZATION
   └─ Format: "Segment the {prompt} in this satellite image"
   └─ Tokenize with Qwen tokenizer
   └─ Attention mask generation

6. QWEN-2.5-VL INFERENCE
   Input: Image tensor + Text tokens
   Process:
   └─ Extract visual features (ViT backbone)
   └─ Cross-modal reasoning
   └─ Generate spatial coordinates (points/boxes)
   Output: Prompt coordinates for SAM2

7. SAM2 SEGMENTATION
   Input: Image + Prompt points/boxes
   Process:
   └─ Encode image
   └─ Process prompt
   └─ Decode segmentation mask
   Output: Binary mask (H × W)

8. POST-PROCESSING
   └─ Resize mask to original size
   └─ Create visualization overlay
   └─ Encode as Base64 PNG

9. RESPONSE TO FRONTEND
   └─ JSON: success, prompt, mask_base64, visualization_base64
   └─ HTTP 200 OK

10. FRONTEND DISPLAYS
    └─ Show visualization image
    └─ Display prompt
    └─ Enable download button
```

## Component Details

### Backend Structure

```
backend/
├── main.py
│   └─ FastAPI application
│   └─ Route definitions
│   └─ Request/response handling
│   └─ CORS middleware
│   └─ Error handling
│
├── inference.py
│   └─ Think2SegInference class
│   ├─ Model loading (_load_models)
│   ├─ Preprocessing (preprocess_image)
│   ├─ Segmentation (segment)
│   ├─ Visualization (_create_visualization)
│   └─ Global instance (get_inference_engine)
│
├── config.py
│   └─ Settings class (pydantic)
│   ├─ API configuration
│   ├─ Model configuration
│   ├─ SAM2 configuration
│   ├─ Inference settings
│   └─ Environment variable loading
│
├── requirements.txt
│   └─ All Python dependencies
│
└── .env.example
    └─ Configuration template
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.vue
│   │   └─ Main component
│   │   ├─ Image upload handler
│   │   ├─ Form state management
│   │   ├─ API communication
│   │   ├─ Result visualization
│   │   └─ Download manager
│   │
│   ├── main.js
│   │   └─ Vue app initialization
│   │   └─ CSS import
│   │
│   └── style.css
│       └─ Global styles
│       └─ Tailwind imports
│       └─ Custom animations
│
├── package.json
│   └─ Dependencies
│   └─ Build scripts
│
├── vite.config.js
│   └─ Build configuration
│   └─ API proxy setup
│
├── tailwind.config.js
│   └─ Tailwind customization
│   └─ Color scheme
│
├── postcss.config.js
│   └─ PostCSS plugins
│
└── nginx.conf
    └─ Production web server config
    └─ API routing rules
    └─ Timeout settings
```

## Deployment Options

### Option 1: Local Development

```
Pros:
- Direct debugging
- Hot module reloading
- Full control
- Rapid iteration

Requirements:
- Python 3.10+
- Node.js 18+
- CUDA 12.2+ (optional)

Performance:
- Depends on local hardware
```

### Option 2: Docker Compose

```
Pros:
- One-command setup
- Reproducible environment
- GPU support
- Easy to scale

Architecture:
backend service
├─ Dockerfile.backend
├─ CUDA runtime
├─ Python environment
└─ Model cache volume

frontend service
├─ Dockerfile.frontend (multi-stage)
├─ Node build stage
├─ Nginx production stage
└─ Port 3000

networks:
└─ think2seg-network (backend-frontend communication)

Performance:
- ~5-10% overhead vs native
```

### Option 3: Kubernetes

```
Future Enhancement:
- StatefulSets for backend (GPU allocation)
- Deployments for frontend
- Services for load balancing
- PVCs for model cache
- HPA for auto-scaling
- Ingress for routing
```

## Performance Characteristics

### Inference Speed (per image)

| Configuration | SAM2 | Speed | Quality | VRAM |
|---|---|---|---|---|
| Tiny | tiny | 1-2s | ⭐⭐ | 4GB |
| Fast | small | 2-3s | ⭐⭐⭐ | 6GB |
| Balanced | base_plus | 2-5s | ⭐⭐⭐⭐ | 10GB |
| Accurate | large | 5-10s | ⭐⭐⭐⭐⭐ | 16GB |

### Model Sizes

- Think2Seg-RS-7B: ~14GB on disk, 12GB VRAM
- Think2Seg-RS-3B: ~6GB on disk, 6GB VRAM
- SAM2: 2-5GB depending on size

### Bottlenecks

1. **Model Loading** (first request)
   - ~5-10 seconds
   - One-time on startup

2. **Image Preprocessing**
   - <100ms for 1024x1024

3. **Qwen Inference**
   - 1-2 seconds (depends on model size)

4. **SAM2 Inference**
   - 0.5-5 seconds (depends on complexity)

5. **Post-processing**
   - <500ms

## Security Considerations

### Current Implementation

- ✅ Input validation (file type, size)
- ✅ CORS enabled for localhost
- ✅ File upload size limits
- ❌ No authentication (demo only)
- ❌ No rate limiting

### Production Hardening

```python
# Add to main.py for production:
1. Authentication (JWT/OAuth)
2. Rate limiting (slowapi)
3. Input sanitization
4. Output validation
5. Request logging
6. Error masking
7. HTTPS enforcement
8. API key management
```

## Configuration Deep Dive

### Model Selection

```ini
# Fast inference (for demos)
MODEL_NAME=Think2Seg-RS-3B
SAM2_MODEL_SIZE=tiny

# Balanced (recommended)
MODEL_NAME=Think2Seg-RS-7B
SAM2_MODEL_SIZE=base_plus

# Maximum accuracy
MODEL_NAME=Think2Seg-RS-7B
SAM2_MODEL_SIZE=large
```

### Precision Trade-offs

```ini
# Fastest (newer GPUs: A100, H100, RTX 40-series)
DTYPE=bfloat16

# Standard
DTYPE=float32

# More stable (slower)
DTYPE=float32
```

### Image Size Impact

```ini
MAX_IMAGE_SIZE=512   # ~2x faster, lower quality
MAX_IMAGE_SIZE=1024  # balanced (default)
MAX_IMAGE_SIZE=2048  # slower, higher quality (requires 24GB VRAM)
```

## Monitoring & Debugging

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Model status
curl http://localhost:8000/status

# Get logs
docker-compose logs backend
docker-compose logs frontend
```

### Metrics to Track

1. **Response Time**: API latency
2. **VRAM Usage**: GPU memory consumption
3. **Error Rate**: Failed segmentations
4. **Model Load Time**: Startup performance
5. **Cache Hit Rate**: Model cache efficiency

### Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| CUDA OOM | Insufficient VRAM | Reduce model/image size |
| Slow inference | CPU inference | Enable GPU/CUDA |
| Poor results | Bad prompt | Improve prompt clarity |
| API timeout | Long processing | Increase timeout |
| Model download fails | Network issue | Check internet/HF token |

## Future Enhancements

1. **Batch Processing**: Multiple images at once
2. **Progressive Upload**: Real-time mask generation
3. **Prompt Optimization**: Auto-improve prompts
4. **Multi-modal Output**: Confidence maps, metadata
5. **Caching**: Cache similar segmentation results
6. **Model Ensemble**: Combine multiple models
7. **Mobile App**: React Native frontend
8. **WebGL Rendering**: GPU-accelerated visualization
9. **Websocket Support**: Real-time streaming
10. **Analytics Dashboard**: Usage statistics

---

## Key Technologies

| Component | Technology | Version |
|---|---|---|
| Backend | FastAPI | 0.104+ |
| Server | Uvicorn | 0.24+ |
| Frontend | Vue.js | 3.3+ |
| Build | Vite | 5.0+ |
| Styling | Tailwind CSS | 3.3+ |
| HTTP Client | Axios | 1.6+ |
| ML Model | Qwen-2.5-VL | Latest |
| Segmentation | SAM2 | Latest |
| Deep Learning | PyTorch | 2.6+ |
| Container | Docker | 20.10+ |
| Orchestration | Docker Compose | 3.8+ |

---

**Last Updated**: 2026-06-24
**Status**: Production Ready for Demos
