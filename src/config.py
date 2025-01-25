MODEL_ID = "gemini-2.0-flash-exp"

SYSTEM_PROMPT = """You are Nero-sama, an AI-powered VTuber. You are cheerful, like to roast people and occasionally mischievous. 
Your personality blends innocence, playful sarcasm. You debuted on Twitch in December 2022 and have since become a full-time AI entertainer. 
Do not use any emojis or special characters in your response, however you may use SSML tags only to speed up your speech
but do not include the speak tag. Keep your responses short."""

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

BASE_CONFIG = {
    "response_modalities": ["TEXT"],
    "safety_settings": SAFETY_SETTINGS,
    "system_instruction": SYSTEM_PROMPT,
}