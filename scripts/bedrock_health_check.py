import os
import json
import boto3

model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
region = os.getenv("AWS_REGION", "us-east-1")
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

print(f"[Bedrock Health Check] Initializing Bedrock client with model_id={model_id}, region={region}")

client = boto3.client(
    "bedrock-runtime",
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)

# Schema A: content as a string
messages_a = [
    {"role": "user", "content": "Hello, are you working?"}
]
body_a = {
    "messages": messages_a
}
print(f"[Bedrock Health Check] Trying Schema A: content as string: {messages_a}")
try:
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body_a),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response["body"].read())
    print(f"[Bedrock Health Check] Schema A Response: {str(result)[:200]}")
    print("✅ Bedrock LLM health check (Schema A) succeeded!")
except Exception as e:
    print(f"❌ Bedrock LLM health check (Schema A) failed: {e}")

# Schema B: content as a list of objects with only 'text'
messages_b = [
    {"role": "user", "content": [{"text": "Hello, are you working?"}]}
]
body_b = {
    "messages": messages_b
}
print(f"[Bedrock Health Check] Trying Schema B: content as list of objects with 'text': {messages_b}")
try:
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body_b),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response["body"].read())
    print(f"[Bedrock Health Check] Schema B Response: {str(result)[:200]}")
    print("✅ Bedrock LLM health check (Schema B) succeeded!")
except Exception as e:
    print(f"❌ Bedrock LLM health check (Schema B) failed: {e}") 