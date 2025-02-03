import os
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

class YouTubeLiveChat:
    def __init__(self):
        """
        Initialize the YouTubeLiveChat class with the YouTube Data API key.
        """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        CLIENT_SECRET_FILEPATH = r"src\utils\client_secret.json"
        try:
            #  lemme know ur email so u can go through the OAuth process
            flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILEPATH,
                scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
            )
            credentials = flow.run_local_server(port=8080)

            self.youtube = build('youtube', 'v3', credentials=credentials)
            
        except KeyboardInterrupt:
            print("Exiting... YoutubeLiveChat")
            exit()
        except Exception as e:
            print(f"An error occurred in YoutubeLiveChat: {e}")

    def get_channel_id(self, identifier):
        """
        Get the channel ID for a specific YouTube identifier.
        This is a handle (@LofiGirl)
        """
        request = self.youtube.search().list(
            part="snippet",
            q=identifier,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['snippet']['channelId']
        else:
            raise ValueError("Channel not found for handle.")


    def get_live_broadcast_id(self, channel_id):
        """
        Fetch the live broadcast ID for a specific channel.
        """
        request = self.youtube.search().list(
            part="id,snippet",
            channelId=channel_id,  # Specify the channel ID
            eventType="live",      # Only live events
            type="video",          # Only videos
            maxResults=1           # Limit to one live broadcast
        )
        response = request.execute()

        if not response.get('items'):
            print(f"No live broadcasts found for channel ID: {channel_id}")
            return None
        # print(f"broadcast response: {response}")
        video_id = response['items'][0]['id']['videoId']
        title = response['items'][0]['snippet']['title']
        print(f"Vid Title: {title}")

        return video_id

    def get_live_chat_id(self, video_id):
        """
        Get the liveChatId for a specific live broadcast.
        """
        request = self.youtube.videos().list(
        part="liveStreamingDetails",
        id=video_id
    )
        response = request.execute()
        # print(f"response: {response}")
        if response['items']:
            return response['items'][0]['liveStreamingDetails']['activeLiveChatId']
        else:
            raise ValueError("Live broadcast not found or no live chat associated.")

    def fetch_live_chat_messages(self, live_chat_id, next_page_token=None):
        """
        Fetch live chat messages for a specific liveChatId.
        """
        request = self.youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails",
            maxResults=200,  # Limit to 200 messages per request (min)
            pageToken=next_page_token # Continue from the last page token (if any)
        )
        response = request.execute()
        # print(f"size: {len(response['items'])}")
        res_size = len(response['items'])
        # Get index limit based on res_size
        if res_size < 5:
            latest_messages_amount = res_size
        else:
            latest_messages_amount = 5

        return res_size, response.get('nextPageToken', None), response['items'][-latest_messages_amount:] # return tuple of msg amount, next_page_token and items
    
    def obtain_livechat_id(self, identifier="@LofiGirl"):
        """
        Get all IDs needed to fetch live chat messages using Youtube channel's handle, e.g. @LofiGirl.
        """
        # Step 1: Get the channel ID for the identifier
        channel_id = self.get_channel_id(identifier)
        # print(f"Channel ID: {channel_id}")

        # Step 2: Get the live video ID for the channel
        video_id = self.get_live_broadcast_id(channel_id)

        if not video_id:
            print("No active live broadcasts found.")
        else:
            # Step 3: Get the live chat ID for the broadcast
            live_chat_id = self.get_live_chat_id(video_id)
            # print(f"Live Chat ID: {live_chat_id}")

        return live_chat_id

   

if __name__ == "__main__":
    # Replace with your target identifier (e.g., @handle e.g @LofiGirl)
    IDENTIFIER = input("Enter the YouTube identifier: ")
    
    yt_chat = YouTubeLiveChat()

    try:
        # Step 1: Get the channel ID for the identifier
        channel_id = yt_chat.get_channel_id(IDENTIFIER)
        print(f"Channel ID: {channel_id}")

        # Step 2: Get the live video ID for the channel
        video_id = yt_chat.get_live_broadcast_id(channel_id)
        if not video_id:
            print("No active live broadcasts found.")
        else:
            # Step 3: Get the live chat ID for the broadcast
            live_chat_id = yt_chat.get_live_chat_id(video_id)
            print(f"Live Chat ID: {live_chat_id}")

            # Step 4: Fetch live chat messages continuously (next_page_token use to only get new messages instead of whole history after first run)
            next_page_token = None
            while True:
                next_page_token = yt_chat.fetch_live_chat_messages(live_chat_id, next_page_token)
                time.sleep(10)  # Wait for 10 seconds before the next request
        
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
