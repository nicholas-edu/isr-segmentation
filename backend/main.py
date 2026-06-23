"""
Think2Seg FastAPI Backend
REST API for satellite image segmentation using natural language prompts.
"""

import logging
from contextlib import asynccontextmanager
import io
import base64

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
import numpy as np

from config import settings
from inference import get_inference_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentationRequest(BaseModel):
    """Segmentation request model."""
    prompt: str


class SegmentationResponse(BaseModel):
    """Segmentation response model."""
    success: bool
    prompt: str
    mask: list = None
    visualization: str = None
    error: str = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown."""
    # Startup
    logger.info("Think2Seg API starting...")
    try:
        engine = get_inference_engine()
        logger.info(f"Model status: {engine.get_status()}")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise

    yield

    # Shutdown
    logger.info("Think2Seg API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Think2Seg Demo API",
    description="Natural Language Satellite Image Segmentation",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    engine = get_inference_engine()
    return {
        "status": "healthy",
        "model_loaded": engine.loaded,
        "model": settings.model_path,
    }


@app.get("/status")
async def get_status():
    """Get model status."""
    engine = get_inference_engine()
    return engine.get_status()


@app.post("/segment")
async def segment_image(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """
    Segment satellite image based on natural language prompt.

    Args:
        file: Uploaded image file
        prompt: Natural language description of what to segment

    Returns:
        Segmentation results with mask and visualization
    """
    try:
        # Validate file
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and validate image
        image_data = await file.read()
        try:
            image = Image.open(io.BytesIO(image_data))
            image = image.convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

        if image.size[0] * image.size[1] > 25000000:  # ~5000x5000
            raise HTTPException(
                status_code=400,
                detail="Image too large. Maximum ~5000x5000 pixels.",
            )

        # Get inference engine
        engine = get_inference_engine()

        # Run segmentation
        results = engine.segment(image, prompt, return_visualization=True)

        if not results["success"]:
            raise HTTPException(status_code=500, detail=results.get("error"))

        # Convert results for JSON response
        response_data = {
            "success": True,
            "prompt": prompt,
            "original_size": results["original_size"],
        }

        # Encode mask as base64
        if "mask" in results:
            mask = results["mask"]
            mask_uint8 = (mask * 255).astype(np.uint8)
            mask_image = Image.fromarray(mask_uint8)
            mask_buffer = io.BytesIO()
            mask_image.save(mask_buffer, format="PNG")
            response_data["mask_base64"] = base64.b64encode(
                mask_buffer.getvalue()
            ).decode()

        # Encode visualization as base64
        if "visualization" in results:
            viz_image = results["visualization"]
            viz_buffer = io.BytesIO()
            viz_image.save(viz_buffer, format="PNG")
            response_data["visualization_base64"] = base64.b64encode(
                viz_buffer.getvalue()
            ).decode()

        return JSONResponse(response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in segment endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/segment-multiple")
async def segment_multiple(
    file: UploadFile = File(...),
    prompts: str = Form(...),  # Comma-separated prompts
):
    """
    Segment satellite image with multiple natural language prompts.

    Args:
        file: Uploaded image file
        prompts: Comma-separated natural language descriptions

    Returns:
        List of segmentation results
    """
    try:
        # Parse prompts
        prompt_list = [p.strip() for p in prompts.split(",") if p.strip()]
        if not prompt_list:
            raise HTTPException(status_code=400, detail="No valid prompts provided")

        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image = image.convert("RGB")

        engine = get_inference_engine()

        # Process each prompt
        results = []
        for prompt in prompt_list:
            result = engine.segment(image, prompt, return_visualization=False)
            results.append(result)

        return JSONResponse({"success": True, "results": results})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in segment-multiple endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get API configuration."""
    return {
        "model_name": settings.model_name,
        "model_path": settings.model_path,
        "device": settings.device,
        "dtype": settings.dtype,
        "max_image_size": settings.max_image_size,
        "inference_timeout": settings.inference_timeout,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info" if settings.debug else "warning",
    )
