import os
import asyncio
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import MODEL_ID, BASE_CONFIG
from utils.livechat_retrieval import YouTubeLiveChat
from utils.audio_handler import AudioHandler
from utils.video_handler import VideoHandler
# from utils.vtube_studio_handler import VTubeStudioHandler

def handle_chat_and_vid(live_chat_choice, video_recording_choice, audio_recording_choice, live_chat_id=None):
    """
    Pass live chat msg or video audio and video to model and get response from model and speak it out.
    """

    # To keep track the last next_page_token
    next_page_token = None
    while True:
        if audio_recording_choice:
            user_input = audio_handler.record_from_microphone()
        elif live_chat_choice:
            user_input, next_page_token = live_chat_msgs(live_chat_id, next_page_token)
        elif audio_recording_choice and video_recording_choice:
            user_input = audio_handler.record_from_microphone()
            user_input = user_input + "\n" + live_chat_msgs(live_chat_id, next_page_token)
        else:
            user_input = input("Enter input for Nero: ")
        
        if video_recording_choice:
            video_handler.stop_recording()
            file = client.files.upload(path=video_handler.video_path)
            video_handler.start_recording()
        
            while client.files.get(name=file.name).state != "ACTIVE":
                print("Uploading file...")
                time.sleep(1)  # Poll every 1 seconds

            message = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(user_input),
                    types.Part.from_uri(file_uri=file.uri, mime_type="video/mp4")
                ]
            )
        else:
            message = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(user_input)
                ]
            )
        # keep api ws alive
        audio_handler.vtube_studio_handler.websocket.ping()
        response = chat.send_message(message)
        response_text = response.text
        print(f"tagged response: {response_text}")
        # Added regex to remove speak tag (MUST not remove or audio will gg) (e.g <speak>text</speak> -> text)
        # if want remove all tags use r"<.*?>"
        # tagless_res =   re.sub(r"<.*?>", "", response_text)
        response_text = re.sub(r"</?speak>", "", response_text)  
        # Added regex to remove prosody pitch tag cus it ruins nero voice (e.g <prosody pitch="x">text</prosody> -> <prosody >text</prosody>)
        response_text = re.sub(r'pitch=".*?"', "", response_text)
        # remove prosody rate="fast" tag with 1.1 as fast cause ditortion in nero voice
        # TODO add more variation to fast like >1.2 will change to 1.15
        response_text = re.sub(r'rate="fast"', 'rate="1.15"', response_text)


        print(f"Nero-sama: {response_text}")
        audio_handler.speak(response_text)
        time.sleep(1) # Delay to prevent hitting API rate limit (hopefully) 


def live_chat_msgs(live_chat_id, next_page_token):
    """
    Pass live_chat_id and next_page_token to fetch live chat messages and return the lastest live chat message.
    """
    
    # Get the lastest live chat message
    size, next_page_token, messages = yt_chat.fetch_live_chat_messages(live_chat_id, next_page_token)
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
        user_input = "Continue talking on your own" # self prompt if no live chat message
        print("Self prompted response")
    print(f"next_page_token: {next_page_token}")
    return (user_input, next_page_token)

def get_yes_no_input(prompt="Enter Y/N: "):
    """Prompt the user for a yes/no input and handle incorrect responses."""
    while True:
        user_input = input(prompt).strip().lower()  # Normalize input
        if user_input in ["y", "yes"]:
            return True  # User confirmed
        elif user_input in ["n", "no"]:
            return False  # User declined
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")  # Error message

def handle_livestream_options():
    """
    Allow user to select wanted options for livestream such as, live chat, video recording and audio recording.
    """
    global video_handler, yt_chat
    live_chat_choice = get_yes_no_input("Enable live chat? (y/n): ")
    video_recording_choice = get_yes_no_input("Enable video recording? (y/n): ")
    audio_recording_choice = get_yes_no_input("Enable audio recording? (y/n): ")

    if live_chat_choice:
        yt_chat = YouTubeLiveChat()
        channel_id = input("Enter the channel ID (leave empty and press enter if using default @LofiGirl): ")
        if channel_id:
            live_chat_id = yt_chat.obtain_livechat_id(channel_id)
        else:
            live_chat_id = yt_chat.obtain_livechat_id()
        print("Live chat enabled.")
    else:
        live_chat_id = None
        print("Live chat disabled.")
    
    if audio_recording_choice:
        print("Audio recording enabled.")
    else:
        print("Audio recording disabled.")

    if video_recording_choice:
        video_handler = VideoHandler()
        video_handler.start_recording()
        handle_chat_and_vid(live_chat_choice, video_recording_choice, audio_recording_choice, live_chat_id)
        video_handler.stop_recording()
    else:
        handle_chat_and_vid(live_chat_choice, video_recording_choice, audio_recording_choice, live_chat_id)

async def start_vtstudio_api_session():
    # create websocket session instance
    await audio_handler.vtube_studio_handler.websocket_session()

async def main_async():
    load_dotenv()
    global client, chat, audio_handler

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))    
    chat = client.chats.create(model=MODEL_ID, config=BASE_CONFIG)
    audio_handler = AudioHandler()
    await start_vtstudio_api_session()
    handle_livestream_options()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()