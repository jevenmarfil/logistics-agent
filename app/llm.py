import os
from dotenv import load_dotenv
from google import genai
import requests

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash",
)

# Initialize Gemini client only if Gemini is selected
gemini_client = None

if LLM_PROVIDER == "gemini":
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is required when "
            "LLM_PROVIDER=gemini"
        )

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


def generate_llm_response(prompt: str) -> str:
    """
    Generate an LLM response using the provider
    configured in the environment.

    Supported providers:
    - gemini
    - openrouter
    """

    if LLM_PROVIDER == "gemini":
        return generate_gemini_response(prompt)

    if LLM_PROVIDER == "openrouter":
        return generate_openrouter_response(prompt)

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. "
        "Use 'gemini' or 'openrouter'."
    )


def generate_gemini_response(prompt: str) -> str:
    """
    Generate a response using Google Gemini.
    """

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text


def generate_openrouter_response(prompt: str) -> str:
    """
    Generate a response using OpenRouter.
    """

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is required when "
            "LLM_PROVIDER=openrouter"
        )

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]