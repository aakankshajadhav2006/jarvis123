"""
Mobile Notification Module for Jarvis.
Handles sending notifications to mobile devices connected via ADB.
"""
import subprocess
import os


class MobileNotifier:
    """Handles mobile device notifications."""

    def __init__(self):
        self.device_connected = False

    def check_device_connection(self):
        """Check if mobile device is connected via ADB."""
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Check if any device is listed (besides the header)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                self.device_connected = True
                return True
            return False

        except Exception as e:
            print(f"ADB check failed: {e}")
            return False

    def send_notification(self, title, message):
        """
        Send notification to connected mobile device.

        Args:
            title: Notification title
            message: Notification message

        Returns:
            bool: Success status
        """
        if not self.check_device_connection():
            print("No mobile device connected")
            return False

        try:
            # Use ADB to send notification
            cmd = [
                'adb', 'shell', 'am', 'broadcast',
                '-a', 'com.jarvis.NOTIFICATION',
                '--es', 'title', title,
                '--es', 'message', message
            ]

            subprocess.run(cmd, capture_output=True, timeout=10)
            print(f"Notification sent: {title}")
            return True

        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def make_call(self, phone_number):
        """
        Make a phone call via connected device.

        Args:
            phone_number: Phone number to call

        Returns:
            bool: Success status
        """
        if not self.check_device_connection():
            print("No mobile device connected")
            return False

        try:
            cmd = ['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}']
            subprocess.run(cmd, capture_output=True, timeout=10)
            print(f"Initiating call to: {phone_number}")
            return True

        except Exception as e:
            print(f"Failed to make call: {e}")
            return False

    def end_call(self):
        """End the current call."""
        try:
            cmd = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ENDCALL']
            subprocess.run(cmd, capture_output=True, timeout=5)
            return True

        except Exception as e:
            print(f"Failed to end call: {e}")
            return False


# Global instance
_notifier = MobileNotifier()


def send_mobile_notification(title, message):
    """Send notification to mobile device."""
    return _notifier.send_notification(title, message)


def make_phone_call(phone_number):
    """Make phone call via mobile device."""
    return _notifier.make_call(phone_number)


def end_phone_call():
    """End current phone call."""
    return _notifier.end_call()
