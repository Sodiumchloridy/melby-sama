from dotenv import load_dotenv, set_key
import time
import asyncio
import os
import websockets
import json

# Load environment variables


class VTubeStudioHandler:
    def __init__(self, server_uri="ws://localhost:8001", env_file=".env"):
        load_dotenv()
        self.server_uri = server_uri
        self.env_file = env_file
        # exp3.json file can be created in Vtube Studio App in settings -> hotkeys settings and expression -> expression editor, then create new hotkeys for the expression
        self.keyword_to_expression = {
            "blink": "left eye blink.exp3.json",
        }

    # Open a websocket connection that will be shared across all methods and the session will be authenticated to use more API options
    async def websocket_session(self):
        """Maintains a persistent WebSocket session and authenticates it."""
        self.websocket = await websockets.connect(self.server_uri)
        await self.auth_handler(self.websocket)
        print("Authenticated WebSocket session established.")
        return self.websocket  # Return the connection to be reused

    async def get_auth_token(self, websocket):
        """
        Requests a new authentication token and saves it to .env.
        """
        req_body = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "NeroSamaPlugin",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": "NeroSamaPlugin",
                "pluginDeveloper": "NeroSama",
            },
        }
        res = await self.send_message_to_websocket(websocket, req_body)

        if res:
            auth_token = res["data"].get(
                "authenticationToken"
            )  # Use dict get method to avoid KeyError since it returns None if key not found
            if auth_token:
                # Save the auth token to .env to be used in future sessions
                set_key(self.env_file, "VTUBE_STUDIO_AUTH_TOKEN", auth_token)
                # Set the environment variable directly
                os.environ["VTUBE_STUDIO_AUTH_TOKEN"] = auth_token
                print("Auth token acquired and saved to .env")
            return auth_token

    async def auth(self, websocket):
        """
        Authenticates using the saved auth token.
        """
        auth_token = os.getenv("VTUBE_STUDIO_AUTH_TOKEN")

        # if not auth_token:
        #     print("No auth token found. Requesting a new one.")
        #     auth_token = await self.get_auth_token(websocket)
        #     if not auth_token:
        #         print("Failed to acquire authentication token.")
        #         return None

        req_body = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "NeroSamaPlugin",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": "NeroSamaPlugin",
                "pluginDeveloper": "NeroSama",
                "authenticationToken": auth_token,
            },
        }
        res = await self.send_message_to_websocket(websocket, req_body)
        if res:
            print("Authenticated successfully.")
            return res
        else:
            print("Authentication failed.")
            return None

    async def check_api_status(self, websocket):
        """
        Checks the WebSocket API status.
        """
        req_body = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "APIStateRequest",
        }
        return await self.send_message_to_websocket(websocket, req_body)

    async def auth_handler(self, websocket):
        """
        Ensures the user is authenticated:
        - If first-time user, request an authentication token and authenticate.
        - If token exists, attempt authentication. If it fails, request a new token and retry authentication.
        """
        res = await self.check_api_status(websocket)

        # Check if session is already authenticated based on API status check
        if res and res["data"].get("currentSessionAuthenticated"):
            print("Session is already authenticated.")
            return

        auth_token = os.getenv("VTUBE_STUDIO_AUTH_TOKEN")

        if auth_token:
            print("Attempting authentication with saved token...")
            auth_response = await self.auth(websocket)

            if not auth_response:
                print("Authentication failed. Requesting a new token.")
                new_token = await self.get_auth_token(websocket)
                if new_token:
                    await self.auth(websocket)
        else:
            print("No authentication token found. Requesting auth token.")
            new_token = await self.get_auth_token(websocket)
            # Authenticate with the token
            if new_token:
                await self.auth(websocket)

    async def send_message_to_websocket(self, websocket, payload):
        """
        Sends a request to the Vtube Studio WebSocket server and returns a parsed response from it.
        """

        message = json.dumps(payload, indent=4)
        print(f"Sending message: {message}\n")
        await websocket.send(message)

        response = await websocket.recv()
        parsed_res = json.loads(response)
        print(f"Response from server: {json.dumps(parsed_res, indent=4)}\n")
        return parsed_res

    async def hotkey_execution(self, websocket, hotkey_name):
        """
        Trigger hotkey using hotkey name which is the name given to motion or expression under hotkey settings
        """
        req_body = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": hotkey_name,
            },
        }
        return await self.send_message_to_websocket(websocket, req_body)

    async def list_hotkeys(self, websocket):
        """
        List current loaded model's hotkeys
        """
        req_body = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "HotkeysInCurrentModelRequest",
        }
        return await self.send_message_to_websocket(websocket, req_body)


# Main execution
async def main():
    handler = VTubeStudioHandler()
    websocket = await handler.websocket_session()

    await handler.list_hotkeys(websocket)
    await handler.hotkey_execution(websocket, "left eye blink")


if __name__ == "__main__":
    asyncio.run(main())
