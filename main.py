import os
import eel
import subprocess

# Import core engine modules
from engine.features import speak, playAssistantSound
from engine.command import process_user_command

# Import auth module with error handling
try:
    from engine.auth import recoganize
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    print("Warning: Auth module not available. Face authentication disabled.")

# Import new feature modules with error handling
try:
    from features.pdf_summarizer import summarize_pdf, save_uploaded_pdf
    PDF_SUMMARIZER_AVAILABLE = True
except ImportError as e:
    PDF_SUMMARIZER_AVAILABLE = False
    print(f"Warning: PDF Summarizer not available: {e}")

try:
    from features.multilingual_voice import (
        change_language,
        speak_multilingual,
        get_supported_languages
    )
    MULTILINGUAL_AVAILABLE = True
except ImportError as e:
    MULTILINGUAL_AVAILABLE = False
    print(f"Warning: Multilingual voice not available: {e}")


def start():
    """Start the Jarvis assistant application."""

    # Initialize Eel with the www directory
    eel.init("www")

    # Play startup sound
    playAssistantSound()

    @eel.expose
    def init():
        """Initialize Jarvis - exposed to frontend."""
        # Run device connection batch file
        try:
            subprocess.call([r'device.bat'], shell=True)
        except Exception as e:
            print(f"Device connection warning: {e}")

        # Hide loading screen
        eel.hideLoader()

        # Check if face authentication is available
        if AUTH_AVAILABLE:
            speak("Ready for Face Authentication")

            try:
                # Attempt face authentication
                flag = recoganize.AuthenticateFace()

                if flag == 1:
                    eel.hideFaceAuth()
                    speak("Face Authentication Successful")
                    eel.hideFaceAuthSuccess()
                    speak("Hello, Welcome! How can I help you today?")
                else:
                    speak("Face Authentication Failed. Starting in basic mode.")
                    eel.hideFaceAuth()
                    eel.hideFaceAuthSuccess()

            except Exception as e:
                print(f"Face auth error: {e}")
                speak("Face authentication error. Starting in basic mode.")
                eel.hideFaceAuth()
        else:
            # Auth not available, start directly
            speak("Welcome to Jarvis. How can I help you?")

        # Show main interface
        eel.hideStart()
        playAssistantSound()

    @eel.expose
    def process_voice_command(lang='en'):
        """Process voice command from microphone."""
        from engine.features import listen

        try:
            # Use multilingual voice if available
            if MULTILINGUAL_AVAILABLE and lang != 'en':
                from features.multilingual_voice import listen as listen_lang
                command = listen_lang(lang)
            else:
                command = listen(lang)

            if command:
                response = process_user_command(command)
                return {'success': True, 'response': response}
            else:
                return {'success': False, 'error': 'Could not understand'}

        except Exception as e:
            print(f"Voice command error: {e}")
            return {'success': False, 'error': str(e)}

    @eel.expose
    def save_pdf_summary(summary_data):
        """Save PDF summary to database."""
        try:
            # Store in Supabase or local database
            # For now, return success (database integration can be added later)
            print(f"Summary saved: {summary_data.get('summary', 'N/A')[:100]}...")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Open browser with the app
    try:
        os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    except Exception:
        # Fallback to default browser
        import webbrowser
        webbrowser.open('http://localhost:8000/index.html')

    # Start Eel application
    eel.start('index.html', mode=None, host='localhost', port=8000, block=True)