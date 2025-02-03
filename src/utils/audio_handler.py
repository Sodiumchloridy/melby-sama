import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import asyncio
import os
from utils.vtube_studio_handler import VTubeStudioHandler
import concurrent.futures

class AudioHandler:
    def __init__(self):
        # For speech synthesis
        self.speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_output_config)
        # Attach event handler to trigger Vtube Studio expression
        self.speech_synthesizer.synthesis_word_boundary.connect(self.on_word_boundary)

        # For speech recognition
        self.speech_config.speech_recognition_language="en-US"
        audio_input_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_input_config)

        # Init Vtube Studio handler
        self.vtube_studio_handler = VTubeStudioHandler()
        self.pool = concurrent.futures.ThreadPoolExecutor()


    def speak(self, text):
        self.speech_synthesizer.stop_speaking()

        text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="en-US-AshleyNeural">
                    <prosody pitch="+25.00%" volume="loud" rate="1.1">
                        {text}
                    </prosody>
                </voice>
            </speak>"""
        
        speech_synthesis_result = self.speech_synthesizer.speak_ssml_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))

    def record_from_microphone(self, initial_silence_timeout=15, end_silence_timeout=5):
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, 
            str(initial_silence_timeout * 1000)
        )
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, 
            str(end_silence_timeout * 1000)
        )

        print("Speak into your microphone.")
        speech_recognition_result = self.speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
            return "Continue talking on your own." # self prompt if no live chat message
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    def on_word_boundary(self, evt):
        """Trigger expression in VTube Studio when a keyword is spoken."""
        word = evt.text.lower()
        keyword_to_expression = self.vtube_studio_handler.keyword_to_expression

        if word in keyword_to_expression:
            expression = keyword_to_expression[word]
            print(f"Triggering expression: {expression} for word: {word}")
            # Run the hotkey_execution in a separate thread (kinda scuff but works)

            self.pool.submit(asyncio.run, self.vtube_studio_handler.hotkey_execution(self.vtube_studio_handler.websocket, expression))


async def main():
    load_dotenv()
    audio = AudioHandler()
    # create websocket session instance
    await audio.vtube_studio_handler.websocket_session()
    while True:
        user_input = input("Enter text: ")
        audio.speak(user_input)


# For testing purposes
if __name__ == "__main__":
    asyncio.run(main())
