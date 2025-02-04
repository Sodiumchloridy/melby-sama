from google.genai import types
import os

MODEL_ID = "gemini-2.0-flash-exp"  # Eg: "gemini-2.0-flash-exp" or "gemini-1.5-pro"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT_DIR, 'lore.txt'), 'r') as file:
    SYSTEM_PROMPT = file.read().rstrip()

SAFETY_SETTINGS = [
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
]

TOOLS = [
    types.Tool(google_search=types.GoogleSearch()),
]

BASE_CONFIG = types.GenerateContentConfig(
    temperature=0.4,
    top_p=0.95,
    top_k=20,
    response_modalities=["TEXT"],
    safety_settings=SAFETY_SETTINGS,
    system_instruction=SYSTEM_PROMPT,
    tools=TOOLS,
)