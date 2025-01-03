##########################

# from gtts import gTTS
# import os

# class TTS:
#     def __init__(self):
#         self.audio_file = "tts_output.mp3"  # Temporary file for audio playback

#     def speak(self, text):
#         """Speak the given text using Google TTS."""
#         print(f"Input: {text}")
#         try:
#             # Generate speech
#             tts = gTTS(text=text, lang='en')
#             tts.save(self.audio_file)
#             # Play the audio
#             os.system(f"mpg321 {self.audio_file} > /dev/null 2>&1")
#         except Exception as e:
#             print(f"Error: {e}")

#     def run(self):
#         """Continuously read input from the terminal and convert to speech."""
#         print("Terminal TTS is ready. Type your text below (type 'exit' to quit):")
#         while True:
#             user_input = input("You: ").strip()  # Get user input
#             if user_input.lower() == "exit":
#                 print("Goodbye!")
#                 self.speak("Goodbye!")
#                 break
#             elif user_input:
#                 self.speak(user_input)

# if __name__ == "__main__":
#     tts = TTS()
#     tts.run()



# import os

# class TTS:
#     def speak(self, text):
#         """Speak the given text using espeak with a male, bold voice."""
#         print(f"Input: {text}")
#         try:
#             # Adjust voice settings: "-ven+m3" selects a male voice; adjust pitch and speed as needed.
#             os.system(f"espeak -ven+m3 -s140 -p70 \"{text}\" > /dev/null 2>&1")
#         except Exception as e:
#             print(f"Error: {e}")

#     def run(self):
#         """Continuously read input from the terminal and convert to speech."""
#         print("Terminal TTS is ready. Type your text below (type 'exit' to quit):")
#         while True:
#             user_input = input("You: ").strip()  # Get user input
#             if user_input.lower() == "exit":
#                 print("Goodbye!")
#                 self.speak("Goodbye!")
#                 break
#             elif user_input:
#                 self.speak(user_input)

# if __name__ == "__main__":
#     tts = TTS()
#     tts.run()
import pyttsx3

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init(driverName='espeak')  # Initialize the TTS engine
        self.engine.setProperty('voice', 'english+m4')  # Set male voice (espeak's m3 voice)
        self.engine.setProperty('rate', 140)  # Set speaking rate
        self.engine.setProperty('volume', 1.0)  # Set volume (0.0 to 1.0)

    def speak(self, text):
        """Speak the given text."""
        print(f"Input: {text}")

        # Attempt to stop any ongoing speech and reset the engine
        self._stop_speech()

        # Start the speech
        self.engine.say(text)
        self.engine.runAndWait()

    def _stop_speech(self):
        """Stops the speech if it's running and resets the engine."""
        if self.engine._inLoop:
            self.engine.endLoop()  # Stop the current speech loop if running
            self.engine = pyttsx3.init(driverName='espeak')  # Reinitialize the engine
            self.engine.setProperty('voice', 'english+m4')
            self.engine.setProperty('rate', 140)
            self.engine.setProperty('volume', 1.0)


    def run(self):
        """Continuously read input from the terminal and convert to speech."""
        print("Terminal TTS is ready. Type your text below (type 'exit' to quit):")
        while True:
            user_input = input("You: ").strip()  # Get user input
            if user_input.lower() == "exit":
                print("Goodbye!")
                self.speak("Goodbye!")
                break
            elif user_input:
                self.speak(user_input)

if __name__ == "__main__":
    tts = TTS()
    tts.run()
