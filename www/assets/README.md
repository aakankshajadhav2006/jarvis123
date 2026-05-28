# Asset Files

This directory should contain the following asset files for Jarvis:

## Required Files

1. **activation_sound.mp3** - Sound played when Jarvis activates
   - This is loaded in engine/features.py: `playAssistantSound()`
   - Recommended duration: 1-2 seconds
   - You can use free sound effects from:
     - Freesound.org
     - Zapsplat.com
     - Or generate your own with a text-to-speech tool

## How to Add Assets

1. Download or create your audio file
2. Rename it to `activation_sound.mp3`
3. Place it in this directory: `www/assets/`
4. The application will automatically load it on startup

## Note

If the sound file is not found, Jarvis will still function but will skip the startup sound.
The error will be printed to the console but won't affect functionality.
