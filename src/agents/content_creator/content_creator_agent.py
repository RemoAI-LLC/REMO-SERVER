from .content_creator_tools import get_bedrock_client, generate_nova_canvas_image, generate_nova_reel_video
import time
import requests
from langsmith import traceable

class ContentCreatorAgent:
    """
    Agent responsible for generating images and short videos using AWS Bedrock (Nova Canvas & Nova Reel).
    """
    def __init__(self):
        self.name = "Content Creator Agent"
        self.description = "Generates images and short videos using AWS Bedrock (Nova Canvas & Nova Reel)."

    def handle_request(self, request_type: str, prompt: str, **kwargs):
        if request_type == 'image':
            return self.generate_image(prompt)
        elif request_type == 'video':
            return "Hi there! I wish I could generate videos for you, but I don't have that ability just yet. However, I can create amazing images! If you'd like an image instead, just let me know what you'd like to see."
        else:
            raise ValueError(f"Unknown request type: {request_type}")

    def invoke(self, input_data):
        """
        Standard entry point for agent frameworks.
        Expects input_data to be a dict with keys like 'request_type', 'prompt', etc.
        """
        request_type = input_data.get('request_type')
        prompt = input_data.get('prompt')
        kwargs = {k: v for k, v in input_data.items() if k not in ['request_type', 'prompt']}
        return self.handle_request(request_type, prompt, **kwargs)

    def stream_invoke(self, input_data):
        request_type = input_data.get('request_type')
        prompt = input_data.get('prompt')
        kwargs = {k: v for k, v in input_data.items() if k not in ['request_type', 'prompt']}
        if request_type == 'image':
            yield from self.stream_generate_image(prompt)
        elif request_type == 'video':
            yield "Hi there! I wish I could generate videos for you, but I don't have that ability just yet. However, I can create amazing images! If you'd like an image instead, just let me know what you'd like to see."
        else:
            yield {"error": f"Unknown request type: {request_type}"}

    @traceable
    def generate_image(self, prompt: str):
        try:
            return generate_nova_canvas_image(prompt)
        except Exception as e:
            return {"error": str(e)}

    @traceable
    def stream_generate_image(self, prompt: str):
        yield {"progress": "Generating your image. This may take a few moments..."}
        try:
            result = generate_nova_canvas_image(prompt)
            yield {"result": result}
        except Exception as e:
            yield {"error": str(e)}

    def get_agent(self):
        # For LangGraph or supervisor integration, return a callable or agent object
        # Here, we return self, assuming supervisor expects a .handle_request method
        return self

    def get_description(self):
        return self.description 

    # Helper to clean video URLs
    @staticmethod
    def _sanitize_video_urls(response):
        if not isinstance(response, dict):
            return response
        # Traverse to generatedSamples if present
        try:
            samples = response.get('response', {}).get('generateVideoResponse', {}).get('generatedSamples', [])
            for sample in samples:
                if 'video' in sample and 'uri' in sample['video']:
                    uri = sample['video']['uri']
                    if isinstance(uri, str):
                        sample['video']['uri'] = uri.rstrip("'\"")
        except Exception:
            pass
        return response 