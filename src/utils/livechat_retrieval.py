import pytchat

class YouTubeLiveChat:
    __instance = None
    __current_video_id = None

    @staticmethod
    def get_live_instance(video_id: str):
        if (YouTubeLiveChat.__instance is None 
        or YouTubeLiveChat.__current_video_id != video_id):
            YouTubeLiveChat.__instance = pytchat.create(video_id)
            YouTubeLiveChat.__current_video_id = video_id
        return YouTubeLiveChat.__instance
    
    @staticmethod
    def get_message(video_id):
        live = YouTubeLiveChat.get_live_instance(video_id)
        if live.is_alive():
            try:
                for c in live.get().sync_items():
                    # chat_author makes the chat look like this: "Nightbot: Hello". So the assistant can respond to the user's name
                    livechat_message = c.author.name + ": " + c.message
                    return livechat_message                        
            except Exception as e:
                print("Error receiving chat: {0}".format(e))