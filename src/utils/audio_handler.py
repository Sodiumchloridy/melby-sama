import azure.cognitiveservices.speech as speechsdk
import os

class AudioHandler:
    def __init__(self):
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
    
    def speak(self, text):
        self.speech_synthesizer.stop_speaking()

        text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="en-US-AshleyNeural">
                    <prosody pitch="+25.00%" volume="+100.00%">
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

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    audio = AudioHandler()
    audio.speak("Hello, this is Nero-sama.")