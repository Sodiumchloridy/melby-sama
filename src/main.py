import os
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
import pytchat

from config import MODEL_ID, BASE_CONFIG
from utils.livechat_retrieval import YouTubeLiveChat
from utils.audio_handler import AudioHandler
from utils.video_handler import VideoHandler
from utils.subtitle import generate_subtitle

def main_loop():
    """
    Pass live chat msg and video to model and get response from model and speak it out.
    """
    try:
        while True:
            user_input = audio_handler.record_from_microphone()
            video_handler.stop_recording()
            if user_input:
                file = client.files.upload(path=video_handler.video_path)
                print("Uploading file...")
                while client.files.get(name=file.name).state != "ACTIVE":
                    time.sleep(1)  # Poll every 1 second
                print("Upload complete!")

                message = types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(user_input),
                        types.Part.from_uri(file_uri=file.uri, mime_type="video/mp4")
                    ],
                )
                response = chat.send_message(message)

            else:
                user_input = get_message("jfKfPfyJRdk")
                response = chat.send_message(user_input)

            response_text = re.sub(r'(</?speak>|pitch=".*?")', "", response.text)
            clean_text = re.sub(r'<[^>]+>', '', response_text)
            print(f"Melby-sama: {clean_text}") # TODO - Remove this line after testing
            generate_subtitle("output.txt", clean_text)

            audio_handler.speak(response_text)
            video_handler.start_recording()

    except KeyboardInterrupt:
        print("Exiting chat...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        video_handler.stop_recording()
        audio_handler.speak("Goodbye, everyone! I'm going to end the stream now. Thanks for coming guys.")

def get_message(video_id):
        live = pytchat.create(video_id=video_id)
        if live.is_alive():
            try:
                for c in live.get().sync_items():
                    # Remove emojis from the chat
                    chat_raw = re.sub(r':[^\s]+:', '', c.message)
                    # chat_author makes the chat look like this: "Nightbot: Hello". So the assistant can respond to the user's name
                    livechat_message = c.author.name + ": " + chat_raw
                    return livechat_message                        
            except Exception as e:
                print("Error receiving chat: {0}".format(e))


def main():
    # Init
    load_dotenv()
    global client, chat, audio_handler, video_handler
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model=MODEL_ID, config=BASE_CONFIG)
    audio_handler = AudioHandler()
    video_handler = VideoHandler()

    # Melby-sama starts the stream
    audio_handler.speak("Hello, this is Melby-sama. Welcome to the stream!")
    video_handler.start_recording()
    main_loop()
    print("Stream ended.")

if __name__ == "__main__":
    main()