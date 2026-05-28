"""
Command processing module for Jarvis Assistant.
Parses and executes user commands from voice or text input.
"""
import webbrowser
import os
import subprocess
import datetime
import requests


class CommandProcessor:
    """Processes and executes user commands."""

    def __init__(self):
        self.commands = {
            'time': self.get_time,
            'date': self.get_date,
            'open': self.open_url,
            'launch': self.launch_app,
            'search': self.web_search,
            'weather': self.get_weather,
            'wikipedia': self.search_wikipedia,
        }

    def process(self, query):
        """
        Process a user query and execute appropriate command.

        Args:
            query: User's voice/text input

        Returns:
            str: Response message
        """
        query = query.lower().strip()

        # Try to match command
        for keyword, handler in self.commands.items():
            if keyword in query:
                return handler(query)

        # Default response
        return "I didn't understand that command. Can you please repeat?"

    def get_time(self, query):
        """Get current time."""
        from features.multilingual_voice import get_localized_time
        try:
            return get_localized_time()
        except ImportError:
            str_time = datetime.datetime.now().strftime("%H:%M:%S")
            return f"The time is {str_time}"

    def get_date(self, query):
        """Get current date."""
        from features.multilingual_voice import get_localized_date
        try:
            return get_localized_date()
        except ImportError:
            str_date = datetime.datetime.now().strftime("%Y-%m-%d")
            return f"Today's date is {str_date}"

    def open_url(self, query):
        """Open a URL in browser."""
        websites = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'github': 'https://www.github.com',
            'linkedin': 'https://www.linkedin.com',
        }

        for site, url in websites.items():
            if site in query:
                webbrowser.open(url)
                return f"Opening {site}"

        return "Please specify which website to open"

    def launch_app(self, query):
        """Launch a desktop application."""
        apps = {
            'chrome': 'chrome',
            'firefox': 'firefox',
            'notepad': 'notepad',
            'calculator': 'calc',
            'vscode': 'code',
        }

        for app_name, command in apps.items():
            if app_name in query:
                try:
                    subprocess.Popen(command)
                    return f"Launching {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {e}"

        return "Application not found"

    def web_search(self, query):
        """Perform web search."""
        search_query = query.replace('search', '').strip()
        if search_query:
            url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(url)
            return f"Searching for {search_query}"
        return "What would you like to search for?"

    def get_weather(self, query):
        """Get weather information."""
        # Implement weather API integration
        return "Weather feature coming soon"

    def search_wikipedia(self, query):
        """Search Wikipedia."""
        import wikipedia
        try:
            topic = query.replace('wikipedia', '').strip()
            result = wikipedia.summary(topic, sentences=2)
            return result
        except Exception as e:
            return f"Could not find Wikipedia article: {e}"


# Global command processor instance
_processor = CommandProcessor()


def process_command(query):
    """
    Process a user command.

    Args:
        query: User's voice or text input

    Returns:
        str: Response message
    """
    return _processor.process(query)


# Expose to frontend
import eel

@eel.expose
def process_user_command(query):
    """Process command from frontend."""
    response = process_command(query)
    from engine.features import speak
    speak(response)
    return response
