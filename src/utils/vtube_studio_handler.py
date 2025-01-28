import asyncio
import websockets
import json


class VTubeStudioHandler:
    def __init__(self, server_uri="ws://localhost:8001"):
        self.server_uri = server_uri
        self.keyword_to_expression = {
            "smile": "smileExpression.exp3.json",
            "angry": "angryExpression.exp3.json",
            "surprised": "surprisedExpression.exp3.json",
            "sad": "sadExpression.exp3.json"
        }

    def check_keywords(self, input_string):
        """
        Checks for keywords in the input string and returns a list of matches.
        """
        return [word for word in self.keyword_to_expression if word in input_string.lower()]

    def create_request_payload(self, expression_file, fade_time, active, request_id=None):
        """
        Constructs the payload for the WebSocket request.
        """
        return {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id or "DefaultID",
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": expression_file,
                "fadeTime": fade_time,
                "active": active
            }
        }

    async def send_message_to_websocket(self, payload):
        """
        Sends the given payload to the WebSocket server and waits for a response.
        """
        try:
            async with websockets.connect(self.server_uri) as websocket:
                message = json.dumps(payload)
                print(f"Sending message: {message}")
                await websocket.send(message)

                # Await response
                response = await websocket.recv()
                print(f"Response from server: {response}")
                return response
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")
            return None

    def handle_user_input(self):
        """
        Handles user input, processes keywords, and sends a request to the WebSocket server.
        """
        user_input = input("Enter a string: ")
        found_keywords = self.check_keywords(user_input)

        if found_keywords:
            print(f"Found keywords: {', '.join(found_keywords)}")

            # Use the first keyword found
            keyword = found_keywords[0]
            expression_file = None

            # Map keyword to expression file
            match keyword:
                case "smile":
                    expression_file = self.keyword_to_expression["smile"]
                case "angry":
                    expression_file = self.keyword_to_expression["angry"]
                case "surprised":
                    expression_file = self.keyword_to_expression["surprised"]
                case "sad":
                    expression_file = self.keyword_to_expression["sad"]

            if expression_file:
                fade_time = float(input("Enter the fade time (e.g., 0.5): "))
                active = input("Activate expression? (true/false): ").strip().lower() == "true"
                request_id = input("Enter request ID (optional, press Enter to skip): ").strip() or None

                # Create the request payload
                payload = self.create_request_payload(expression_file, fade_time, active, request_id)

                # Run the WebSocket communication
                asyncio.run(self.send_message_to_websocket(payload))
        else:
            print("No keywords found.")


# Main execution
if __name__ == "__main__":
    handler = VTubeStudioHandler()
    handler.handle_user_input()
