#!/usr/bin/env python3
"""
Minimal test to check if Eel works in this environment
"""
import sys

print("Python version:", sys.version)

try:
    import eel
    print("Eel imported successfully")
except ImportError as e:
    print(f"Eel import failed: {e}")
    sys.exit(1)

try:
    import os
    www_dir = os.path.join(os.path.dirname(__file__), 'www')
    print(f"Www directory: {www_dir}")
    print(f"Www exists: {os.path.exists(www_dir)}")

    eel.init(www_dir)
    print("Eel initialized")

    @eel.expose
    def test_function():
        print("Test function called from frontend")
        return "Backend responding!"

    print("Starting Eel server...")
    eel.start('index.html', mode=None, host='localhost', port=8000, block=True)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
