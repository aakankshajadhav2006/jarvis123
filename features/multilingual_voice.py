"""
Multilingual Voice Module for Jarvis.
Provides text-to-speech and speech-to-text in multiple languages: English, Hindi, and Marathi.
"""
import os
import tempfile
import datetime
import pyttsx3
import speech_recognition as sr
import eel
from typing import Optional


# Language configurations
LANGUAGE_CONFIG = {
    'en': {
        'name': 'English',
        'tts_lang': 'en',
        'recognition_lang': 'en-US',
        'greetings': {
            'hello': 'Hello',
            'how_can_i_help': 'How can I help you?',
            'listening': 'Listening...',
            'processing': 'Processing...',
            'welcome': 'Welcome',
            'ready': 'Ready for your command'
        },
        'datetime_format': {
            'time': '%I:%M %p',
            'date': '%A, %B %d, %Y'
        }
    },
    'hi': {
        'name': 'Hindi',
        'tts_lang': 'hi',
        'recognition_lang': 'hi-IN',
        'greetings': {
            'hello': 'Namaste',
            'how_can_i_help': 'Aap kaise madad kar sakta hoon?',
            'listening': 'Sun raha hoon...',
            'processing': 'Process kar raha hoon...',
            'welcome': 'Swagat hai aapka',
            'ready': 'Aapka command ready hai'
        },
        'datetime_format': {
            'time': '%I:%M %p',
            'date': '%A, %d %B %Y'
        }
    },
    'mr': {
        'name': 'Marathi',
        'tts_lang': 'mr',
        'recognition_lang': 'mr-IN',
        'greetings': {
            'hello': 'Namaskar',
            'how_can_i_help': 'Mi tumhala kase madat karu shakto?',
            'listening': 'Aiktoy...',
            'processing': 'Process kar toy...',
            'welcome': 'Svagat aahe',
            'ready': 'Tumhala command ready aahe'
        },
        'datetime_format': {
            'time': '%I:%M %p',
            'date': '%A, %d %B %Y'
        }
    }
}


class MultilingualVoice:
    """Handles multilingual voice operations."""

    def __init__(self):
        self.current_language = 'en'
        self.tts_engine = None

    def set_language(self, lang: str) -> bool:
        """
        Set the current language for voice operations.

        Args:
            lang: Language code ('en', 'hi', 'mr')

        Returns:
            bool: Success status
        """
        if lang not in LANGUAGE_CONFIG:
            print(f"Language {lang} not supported. Falling back to English.")
            lang = 'en'

        self.current_language = lang
        print(f"Language set to: {LANGUAGE_CONFIG[lang]['name']}")
        return True

    def get_tts_engine(self):
        """Get or initialize TTS engine."""
        if self.tts_engine is None:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
        return self.tts_engine

    def speak(self, text: str, lang: Optional[str] = None) -> bool:
        """
        Speak text in the specified language using gTTS (Google Text-to-Speech).

        Args:
            text: Text to speak
            lang: Language code (uses current language if not specified)

        Returns:
            bool: Success status
        """
        lang = lang or self.current_language

        if lang not in LANGUAGE_CONFIG:
            lang = 'en'

        try:
            # Try using gTTS for better multilingual support
            return self._speak_with_gtts(text, lang)
        except Exception as e:
            print(f"gTTS failed: {e}. Falling back to pyttsx3.")
            # Fallback to pyttsx3
            return self._speak_with_pyttsx3(text, lang)

    def _speak_with_gtts(self, text: str, lang: str) -> bool:
        """Speak using Google Text-to-Speech (gTTS)."""
        try:
            from gtts import gTTS
            import playsound

            # Map language codes to gTTS format
            tts_lang_map = {
                'en': 'en',
                'hi': 'hi',
                'mr': 'mr'
            }

            tts_lang = tts_lang_map.get(lang, 'en')

            # Create speech
            tts = gTTS(text=text, lang=tts_lang, slow=False)

            # Save to temporary file
            temp_file = os.path.join(tempfile.gettempdir(), f'jarvis_speech_{lang}.mp3')
            tts.save(temp_file)

            # Play the audio
            playsound.playsound(temp_file, True)

            # Clean up
            try:
                os.remove(temp_file)
            except:
                pass

            return True

        except Exception as e:
            print(f"gTTS error: {e}")
            raise e

    def _speak_with_pyttsx3(self, text: str, lang: str) -> bool:
        """Speak using pyttsx3 (fallback)."""
        try:
            engine = self.get_tts_engine()

            # Try to set voice for language
            voices = engine.getProperty('voices')

            # Simple matching of voice to language
            for voice in voices:
                if lang in voice.id.lower() or lang in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break

            engine.say(text)
            engine.runAndWait()
            return True

        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return False

    def listen(self, lang: Optional[str] = None) -> str:
        """
        Listen for voice input in the specified language.

        Args:
            lang: Language code (uses current language if not specified)

        Returns:
            str: Recognized text
        """
        lang = lang or self.current_language

        if lang not in LANGUAGE_CONFIG:
            lang = 'en'

        return self._listen_multilingual(lang)

    def _listen_multilingual(self, lang: str) -> str:
        """Listen and recognize speech in specified language."""
        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                print(f"Listening in {LANGUAGE_CONFIG[lang]['name']}...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            print("Processing speech...")

            # Get recognition language code
            recognition_lang = LANGUAGE_CONFIG[lang]['recognition_lang']

            # Use Google Speech Recognition
            text = recognizer.recognize_google(audio, language=recognition_lang)
            print(f"Recognized: {text}")

            return text

        except sr.WaitTimeoutError:
            print("Listening timeout")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition request error: {e}")
            return ""
        except Exception as e:
            print(f"Listening error: {e}")
            return ""

    def get_greeting(self, greeting_type: str) -> str:
        """Get greeting in current language."""
        lang = self.current_language
        if lang not in LANGUAGE_CONFIG:
            lang = 'en'

        greeting = LANGUAGE_CONFIG[lang]['greetings'].get(greeting_type, '')
        return greeting

    def get_localized_time(self) -> str:
        """Get current time in current language format."""
        lang = self.current_language
        if lang not in LANGUAGE_CONFIG:
            lang = 'en'

        time_format = LANGUAGE_CONFIG[lang]['datetime_format']['time']
        time_str = datetime.datetime.now().strftime(time_format)

        # Prepend localized message based on language
        time_messages = {
            'en': f"The time is {time_str}",
            'hi': f"Samay {time_str} hai",
            'mr': f"Vel {time_str} aahe"
        }

        return time_messages.get(lang, time_messages['en'])

    def get_localized_date(self) -> str:
        """Get current date in current language format."""
        lang = self.current_language
        if lang not in LANGUAGE_CONFIG:
            lang = 'en'

        date_format = LANGUAGE_CONFIG[lang]['datetime_format']['date']
        date_str = datetime.datetime.now().strftime(date_format)

        # Prepend localized message based on language
        date_messages = {
            'en': f"Today is {date_str}",
            'hi': f"Aaj {date_str} hai",
            'mr': f"Aaj {date_str} aahe"
        }

        return date_messages.get(lang, date_messages['en'])


# Global instance
_multilingual_voice = MultilingualVoice()


def set_language(lang: str) -> bool:
    """Set current language."""
    return _multilingual_voice.set_language(lang)


def speak(text: str, lang: Optional[str] = None) -> bool:
    """Speak text in specified language."""
    return _multilingual_voice.speak(text, lang)


def listen(lang: Optional[str] = None) -> str:
    """Listen for speech in specified language."""
    return _multilingual_voice.listen(lang)


def get_localized_time() -> str:
    """Get current time in current language."""
    return _multilingual_voice.get_localized_time()


def get_localized_date() -> str:
    """Get current date in current language."""
    return _multilingual_voice.get_localized_date()


def set_tts_language(engine, lang: str) -> None:
    """
    Set TTS engine language (helper for engine.features module).

    Args:
        engine: pyttsx3 engine instance
        lang: Language code
    """
    try:
        voices = engine.getProperty('voices')

        for voice in voices:
            if lang in voice.id.lower() or lang in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

    except Exception as e:
        print(f"Error setting TTS language: {e}")


def listen_multilingual(recognizer, audio, lang: str) -> str:
    """
    Process audio with specified language (helper for engine.features module).

    Args:
        recognizer: Speech recognizer instance
        audio: Audio data
        lang: Language code

    Returns:
        str: Recognized text
    """
    try:
        recognition_lang = LANGUAGE_CONFIG.get(lang, {}).get('recognition_lang', 'en-US')
        text = recognizer.recognize_google(audio, language=recognition_lang)
        print(f"Recognized: {text}")
        return text.lower()

    except Exception as e:
        print(f"Language-specific recognition failed: {e}")
        # Fallback to English
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"Recognized (English fallback): {text}")
        return text.lower()


# Eel-exposed functions
@eel.expose
def change_language(lang: str) -> dict:
    """
    Change Jarvis language from frontend.

    Args:
        lang: Language code ('en', 'hi', 'mr')

    Returns:
        dict with success status and language name
    """
    try:
        success = set_language(lang)

        if success:
            lang_name = LANGUAGE_CONFIG[lang]['name']
            return {
                'success': True,
                'language': lang_name,
                'code': lang
            }
        else:
            return {
                'success': False,
                'error': 'Failed to set language'
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@eel.expose
def speak_multilingual(text: str, lang: str) -> dict:
    """
    Speak text in specified language.

    Args:
        text: Text to speak
        lang: Language code

    Returns:
        dict with success status
    """
    try:
        success = speak(text, lang)
        return {
            'success': success,
            'error': None if success else 'Speech failed'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@eel.expose
def get_supported_languages() -> list:
    """Get list of supported languages."""
    return [
        {'code': code, 'name': config['name']}
        for code, config in LANGUAGE_CONFIG.items()
    ]
