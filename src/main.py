import os
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import MODEL_ID, BASE_CONFIG, ROOT_DIR
from utils.livechat_retrieval import YouTubeLiveChat
from utils.audio_handler import AudioHandler
from utils.video_handler import VideoHandler
from utils.subtitle import generate_subtitle

def main_loop():
    try:
        while True:
            user_input = audio_handler.record_from_microphone()
            video_handler.stop_recording()
            if user_input:
                file = client.files.upload(path=video_handler.video_path)
                print("System: Uploading file...")
                while client.files.get(name=file.name).state != "ACTIVE":
                    time.sleep(1)  # Poll every 1 second
                print("System: Upload complete!")

                message = types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(user_input),
                        types.Part.from_uri(file_uri=file.uri, mime_type="video/mp4")
                    ],
                )
                response = chat.send_message(message)

            else:
                user_input = YouTubeLiveChat.get_message("jfKfPfyJRdk")
                user_input = re.sub(r':[^\s]+:', '', user_input)
                print(user_input)
                response = chat.send_message(user_input)

            response_text = re.sub(r'(</?speak>|pitch=".*?")', "", response.text)
            clean_text = re.sub(r'<[^>]+>', '', response_text)
            print(f"Melby-sama: {clean_text}") # TODO - Remove this line after testing

            output_file = os.path.join(temp_dir, 'output.txt')
            generate_subtitle(output_file, clean_text)

            audio_handler.speak(response_text)
            video_handler.start_recording()

    except KeyboardInterrupt:
        print("System: Exiting chat...")
    except Exception as e:
        print(f"System: An error occurred: {e}")
    finally:
        video_handler.stop_recording()

def main():
    # Init
    load_dotenv()
    global client, chat, audio_handler, video_handler, temp_dir
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model=MODEL_ID, config=BASE_CONFIG)
    audio_handler = AudioHandler()
    video_handler = VideoHandler()
    temp_dir = os.path.join(ROOT_DIR, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # Melby-sama starts the stream
    audio_handler.speak("Hello, this is Melby-sama. Welcome to the stream!")
    video_handler.start_recording()
    main_loop()
    audio_handler.speak("Goodbye everyone! I'm going to end the stream now. Thanks for coming guys.")
    print("System: Stream ended.")

if __name__ == "__main__":
    main()