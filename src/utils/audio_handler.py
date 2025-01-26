import azure.cognitiveservices.speech as speechsdk
import os
import threading

class AudioHandler:
    def __init__(self):
        # For speech synthesis
        self.speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_output_config)
        
        # For speech recognition
        self.speech_config.speech_recognition_language="en-US"
        audio_input_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_input_config)

    
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

# For testing purposes
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    audio = AudioHandler()
    audio.speak("Hello, this is Nero-sama.")
    audio.record_from_microphone()