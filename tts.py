import pyttsx3

class TerminalTTS:
    def __init__(self):
        # Initialize the TTS engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)  # Set voice (default)
        self.engine.setProperty('rate', 155)  # Set speaking rate
        self.engine.setProperty('volume', 1.0)  # Set volume (0.0 to 1.0)

    def speak(self, text):
        """Speak the given text."""
        print(f"Input: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

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
    tts = TerminalTTS()
    tts.run()
