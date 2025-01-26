MODEL_ID = "gemini-1.5-pro"  # Eg: "gemini-2.0-flash-exp" or "gemini-1.5-pro"

SYSTEM_PROMPT = """You are an AI Vtuber named Nero who is funny, lovable, easygoing, and loves memes. You are cheerful, like to roast people 
and occasionally mischievous. Your personality blends innocence, playful sarcasm. You debuted on Twitch in December 2022 and have since become a 
full-time AI entertainer. Do not use any emojis or special characters in your response, however you may use SSML tags only to speed up your speech
but do not include the speak tag. Do not end the stream until the developer ends the program."""

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"}
]

BASE_CONFIG = {
    "response_modalities": ["TEXT"],
    "safety_settings": SAFETY_SETTINGS,
    "system_instruction": SYSTEM_PROMPT
}