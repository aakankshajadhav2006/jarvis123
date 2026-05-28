"""
Core features module for Jarvis Assistant.
Contains essential functions for voice interaction, audio playback, and hotword detection.
"""
import eel
import pyttsx3
import os

# Try importing optional dependencies
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("Warning: SpeechRecognition not available. Voice input disabled.")

try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    playsound = None
    print("Warning: playsound not available. Audio playback disabled.")

try:
    import pvporcupine
    PVPORCUPINE_AVAILABLE = True
except ImportError:
    PVPORCUPINE_AVAILABLE = False
    print("Warning: PvPorcupine not available. Hotword detection disabled.")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not available. Audio features may be limited.")

import threading
import struct

# Global TTS engine instance
_tts_engine = None
_current_language = 'en'

def _get_tts_engine():
    """Get or create TTS engine instance."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty('rate', 150)
        _tts_engine.setProperty('volume', 0.9)
    return _tts_engine


def speak(text, lang='en'):
    """
    Speak the given text using text-to-speech.

    Args:
        text: The text to speak
        lang: Language code (en, hi, mr)
    """
    try:
        engine = _get_tts_engine()

        # Set voice based on language if multilingual module is available
        if lang != 'en':
            try:
                from features.multilingual_voice import set_tts_language
                set_tts_language(engine, lang)
            except ImportError:
                pass

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak: {e}")


def playAssistantSound():
    """Play the assistant activation sound."""
    if not PLAYSOUND_AVAILABLE:
        print("Sound playback not available (playsound module missing)")
        return

    try:
        sound_path = os.path.join(os.path.dirname(__file__), '..', 'www', 'assets', 'activation_sound.mp3')
        sound_path = os.path.abspath(sound_path)

        if os.path.exists(sound_path):
            playsound(sound_path)
        else:
            print(f"Sound file not found at: {sound_path}")
    except Exception as e:
        print(f"Error playing assistant sound: {e}")


def listen(lang='en'):
    """
    Listen for voice input and convert to text.

    Args:
        lang: Language code (en, hi, mr)

    Returns:
        str: Recognized text or empty string if failed
    """
    if not SR_AVAILABLE:
        print("Speech recognition not available")
        return ""

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        print("Processing speech...")

        # Try to use multilingual voice module if available
        if lang != 'en':
            try:
                from features.multilingual_voice import listen_multilingual
                return listen_multilingual(recognizer, audio, lang)
            except ImportError:
                pass

        # Default: use Google Speech Recognition for English
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"Recognized: {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        print("Listening timeout")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return ""
    except Exception as e:
        print(f"Error in listen: {e}")
        return ""


def hotword():
    """
    Continuously listen for hotword activation.
    Runs in a separate process from the main UI.
    """
    if not PVPORCUPINE_AVAILABLE or not PYAUDIO_AVAILABLE:
        print("Hotword detection not available (missing dependencies)")
        return

    porcupine = None
    pa = None
    audio_stream = None

    try:
        # Initialize Porcupine for hotword detection
        porcupine = pvporcupine.create(
            access_key=os.getenv('PICOVOICE_ACCESS_KEY', 'YOUR_PICOVOICE_ACCESS_KEY'),
            keyword_paths=['path/to/jarvis.ppn']
        )

        # Initialize PyAudio
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Hotword listener started. Say 'Jarvis' to activate.")

        while True:
            # Read audio frame
            pcm = audio_stream.read(porcupine.frame_length)
            audio_frame = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # Process with Porcupine
            keyword_index = porcupine.process(audio_frame)

            if keyword_index >= 0:
                print("Hotword detected!")
                # Notify main process
                playAssistantSound()
                # Could use IPC or socket to communicate with main process

    except Exception as e:
        print(f"Error in hotword listener: {e}")
    finally:
        try:
            if audio_stream:
                audio_stream.close()
            if pa:
                pa.terminate()
            if porcupine:
                porcupine.delete()
        except:
            pass


def takeCommand(lang='en'):
    """
    Take voice command from user.

    Args:
        lang: Language code (en, hi, mr)

    Returns:
        str: Command text
    """
    return listen(lang)


# Expose functions to JavaScript frontend
@eel.expose
def test_speak(text):
    """Test function exposed to frontend for TTS."""
    speak(text)
    return f"Spoke: {text}"
