import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

provider = os.getenv("LLM_PROVIDER")
model = os.getenv("LLM_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

print(f"Provider: {provider}")
print(f"Model: {model}")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=model,
    contents="Explain what an AI logistics agent does in one sentence."
)

print("\nResponse:")
print(response.text)