from dotenv import load_dotenv, set_key
import asyncio
import os
import websockets
import json

"""
NOTE: How the authentication persists is by using the same socket connection.therefore a global websocket connection is used.
"""
# Load environment variables
load_dotenv()

class VTubeStudioHandler:
    def __init__(self, server_uri="ws://localhost:8001", env_file=".env"):
        self.server_uri = server_uri
        self.env_file = env_file
        self.keyword_to_expression = {
            "blink": "left eye blink.exp3.json",
        }

    async def websocket_session(self):
        async with websockets.connect(self.server_uri) as websocket:
            await self.auth_handler(websocket)
            await self.check_api_status(websocket)
            
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
            auth_token = res['data'].get('authenticationToken')
            if auth_token:
                set_key(self.env_file, "VTUBE_STUDIO_AUTH_TOKEN", auth_token)
                os.environ["VTUBE_STUDIO_AUTH_TOKEN"] = auth_token
                print("Auth token acquired and saved to .env")
            return auth_token
        return None

    async def auth(self, websocket):
        """
        Authenticates using the saved auth token.
        """
        auth_token = os.getenv("VTUBE_STUDIO_AUTH_TOKEN")

        if not auth_token:
            print("No auth token found. Requesting a new one.")
            auth_token = await self.get_auth_token(websocket)
            if not auth_token:
                print("Failed to acquire authentication token.")
                return None

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

        if res and res['data'].get('currentSessionAuthenticated'):
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
            print("No authentication token found. Requesting new authentication.")
            new_token = await self.get_auth_token(websocket)
            if new_token:
                await self.auth(websocket)

    async def send_message_to_websocket(self, websocket, payload):
        """
        Sends a request to the WebSocket server and awaits a response.
        """
        try:
            message = json.dumps(payload, indent=4)
            print(f"Sending message: {message}\n")
            await websocket.send(message)

            response = await websocket.recv()
            parsed_res = json.loads(response)
            print(f"Response from server: {json.dumps(parsed_res, indent=4)}\n")
            return parsed_res
        except Exception as e:
            print(f"Error during WebSocket communication: {e}")
            return None

# Main execution
async def main():
    handler = VTubeStudioHandler()
    await handler.websocket_session()

if __name__ == "__main__":
    asyncio.run(main())
