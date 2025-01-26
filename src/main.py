import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import MODEL_ID, BASE_CONFIG
from utils.livechat_retrieval import YouTubeLiveChat
from utils.audio_handler import AudioHandler
from utils.video_handler import VideoHandler

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

def live_chat(identifier = '@LofiGirl'):
    # Replace with your channel identifier (e.g., @handle, username, or channel ID, e.g @LofiGirl)
    # identifier = input("Enter the YouTube identifier: ")
    live_chat_id = yt_chat.obtain_livechat_id(identifier)
    next_page_token = None
    try:
        while True:
            # Time the loop
            begin = time.time() 
            size, next_page_token, messages = yt_chat.fetch_live_chat_messages(live_chat_id, next_page_token)
            # Get the lastest live chat message
            print(f"size: {size}")
            
            user_input = ""
            if messages:
                for msg in messages:
                    author = msg['authorDetails']['displayName']
                    text = msg['snippet']['displayMessage']
                    live_chat = f"{author}: {text}"
                    user_input = user_input + live_chat + "\n"
                print(f"live chat: {user_input}")
            else:
                user_input = "continue talking on your own" # self prompt if no live chat message
                print("Self prompted response")

            response = chat.send_message(user_input)

            audio_handler.speak(response.text) # comment out if not testing/using audio to save API credit
            # Not rlly necessary when Nero talks alot with TTS since average is like 2 min per response for this whole loop
            time.sleep(3) # Delay to prevent hitting API rate limit (hopefully) 
            # Time the loop
            end = time.time() 
            print(f"Total runtime of the program is {end - begin}s") 
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    load_dotenv()
    global client, chat, audio_handler, video_handler, yt_chat

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1alpha'})
    
    # client = genai.Client(
    #     vertexai=True,
    #     project="gglxmlb-448010", 
    #     location="asia-southeast1", 
    #     api_key=os.getenv("GEMINI_API_KEY")
    # )
    
    chat = client.chats.create(model=MODEL_ID, config=BASE_CONFIG)
    audio_handler = AudioHandler()
    video_handler = VideoHandler()
    yt_chat = YouTubeLiveChat()

    video_handler.start_recording()
    handle_chat()
    video_handler.stop_recording()

    # live_chat()

if __name__ == "__main__":
    main()