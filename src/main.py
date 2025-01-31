import os
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import MODEL_ID, BASE_CONFIG
from utils.livechat_retrieval import YouTubeLiveChat
from utils.audio_handler import AudioHandler
from utils.video_handler import VideoHandler

def main_loop(live_chat_id):
    """
    Pass live chat msg and video to model and get response from model and speak it out.
    """
    try:
        next_page_token = None # Keep track of the previous next_page_token
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
                user_input, next_page_token = live_chat_msgs(live_chat_id, next_page_token)
                response = chat.send_message(user_input)

            response_text = re.sub(r'(</?speak>|pitch=".*?")', "", response.text)
            clean_text = re.sub(r'<[^>]+>', '', response_text)
            print(f"Melby-sama: {clean_text}")

            audio_handler.speak(response_text)
            video_handler.start_recording()

    except KeyboardInterrupt:
        print("Exiting chat...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        video_handler.stop_recording()
        audio_handler.speak("Goodbye, everyone! I'm going to end the stream now. Thanks for coming guys.")
        chat.delete()
        print("Stream ended.")

def live_chat_msgs(live_chat_id, next_page_token):
    """
    Pass live_chat_id and next_page_token to fetch live chat messages and return the lastest live chat message.
    """
    try:
        # Get the lastest live chat message
        size, next_page_token, messages = yt_chat.fetch_live_chat_messages(live_chat_id, next_page_token)
        print(f"size: {size}")
        
        if messages:
            for msg in messages:
                author = msg['authorDetails']['displayName']
                text = msg['snippet']['displayMessage']
                live_chat = f"{author}: {text}"
                user_input = live_chat + "\n"
            print(f"live chat: {user_input}")
        else:
            user_input = "Continue talking on your own" # Self prompt if no live chat message
            print("Self prompted response")
        return (user_input, next_page_token)
    
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
        return ("", None)


def main():
    # Init
    load_dotenv()
    global client, chat, audio_handler, video_handler, yt_chat
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model=MODEL_ID, config=BASE_CONFIG)
    audio_handler = AudioHandler()
    video_handler = VideoHandler()
    yt_chat = YouTubeLiveChat()

    # Melby-sama starts the stream
    audio_handler.speak("Hello, this is Melby-sama.")
    live_chat_id = yt_chat.obtain_livechat_id()
    video_handler.start_recording()
    main_loop(live_chat_id)

if __name__ == "__main__":
    main()