import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import MODEL_ID, BASE_CONFIG
from utils.audio_handler import AudioHandler
from utils.video_handler import VideoHandler

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1alpha'})
chat = client.chats.create(model=MODEL_ID, config=BASE_CONFIG)
audio_handler = AudioHandler()
video_handler = VideoHandler()

def handle_chat():
    try:
        while True:
            user_input = audio_handler.record_from_microphone()
            video_handler.stop_recording()
            file = client.files.upload(path=video_handler.video_path)
            video_handler.start_recording()

            while client.files.get(name=file.name).state != "ACTIVE":
                print("Uploading file...")
                time.sleep(1)  # Poll every 5 seconds

            message = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(user_input),
                    types.Part.from_uri(file_uri=file.uri, mime_type="video/mp4")
                ]
            )

            response = chat.send_message(message)
            print(f"Nero-sama: {response.text}")
            audio_handler.speak(response.text)

    except KeyboardInterrupt:
        print("Exiting chat...")

def main():
    video_handler.start_recording()
    handle_chat()
    video_handler.stop_recording()

if __name__ == "__main__":
    main()