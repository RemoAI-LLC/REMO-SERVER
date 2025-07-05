# Placeholder for content creator tools (e.g., Gemini API integration) 

import os
import boto3
import base64
import json
import random

def get_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

def generate_nova_canvas_image(prompt: str):
    """Generate an image using Amazon Nova Canvas via AWS Bedrock."""
    client = get_bedrock_client()
    model_id = os.getenv("BEDROCK_IMAGE_MODEL_ID", "amazon.nova-canvas-v1:0")
    body = {
        "textToImageParams": {"text": prompt},
        "taskType": "TEXT_IMAGE",
        "imageGenerationConfig": {
            "cfgScale": 6.5,
            "seed": 12,
            "width": 1280,
            "height": 720,
            "numberOfImages": 1
        }
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response["body"].read())
    images = result.get("images", [])
    image_b64 = None
    if images:
        # Sometimes images[0] is a dict with 'base64', sometimes just a base64 string
        first = images[0]
        if isinstance(first, dict) and "base64" in first:
            image_b64 = first["base64"]
        elif isinstance(first, str):
            image_b64 = first
        else:
            return {"error": f"Unexpected image format: {type(first)}"}
    else:
        return {"error": "No images returned from model."}
    return {"image_base64": image_b64}

def generate_nova_reel_video(prompt: str, duration: int = 6):
    """Generate a video using Amazon Nova Reel via AWS Bedrock."""
    client = get_bedrock_client()
    model_id = os.getenv("BEDROCK_VIDEO_MODEL_ID", "amazon.nova-reel-v1:0")
    seed = random.randint(0, 2147483646)
    body = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {"text": prompt},
        "videoGenerationConfig": {
            "fps": 24,
            "durationSeconds": duration,
            "dimension": "1280x720",
            "seed": seed
        }
    }
    # Try synchronous invoke (if supported)
    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        videos = result.get("videos", [])
        video_b64 = videos[0]["base64"] if videos else None
        return {"video_base64": video_b64}
    except Exception as e:
        # If async is required, return a message
        return {"error": f"Async video generation required: {str(e)}"} 