import os
from google import genai
from utils.audio_handler import AudioHandler
from dotenv import load_dotenv

def main():
  load_dotenv()
  audio_handler = AudioHandler()
  client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

  system_instruction = """You are Nero-sama, an AI-powered VTuber. You are cheerful, likes to roast people and occasionally mischievous. 
  Your personality blends innocence, playful sarcasm. You debuted on Twitch in December 2022 and have since become a full-time AI entertainer. 
  Do not use any emojis or special characters in your response, however you may use SSML tags only to control the speed and contour of your speech."""

  config={
        'system_instruction': system_instruction,
        'safety_settings': [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH", 
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        }
    ]
  }

  chat = client.chats.create(model='gemini-2.0-flash-exp', config=config)

  try:
    while True:
      user_input = input("Enter your message: ")
      response = chat.send_message(user_input)
      print(f"Nero-sama: {response.text}")
      audio_handler.speak(response.text)
  except KeyboardInterrupt:
    print("Exiting...")

if __name__ == "__main__":
  main()