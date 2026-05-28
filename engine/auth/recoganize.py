"""
Face recognition authentication module for Jarvis.
Uses OpenCV for face detection and recognition.
"""
import cv2
import os
import numpy as np
from pathlib import Path


class FaceAuthenticator:
    """Handles face authentication using OpenCV."""

    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_data_dir = Path(__file__).parent.parent.parent / 'training_data'

    def train_model(self, user_name='default'):
        """
        Train face recognition model with user's face.

        Args:
            user_name: Name of the user

        Returns:
            bool: Training success status
        """
        try:
            if not self.training_data_dir.exists():
                self.training_data_dir.mkdir()

            faces = []
            ids = []

            # Capture training images
            camera = cv2.VideoCapture(0)
            sample_count = 0

            print(f"Capturing face samples for {user_name}...")
            print("Look at the camera and move your face slightly...")
            eel.showFaceAuth()

            while sample_count < 50:
                ret, frame = camera.read()
                if not ret:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces_detected = self.face_classifier.detectMultiScale(
                    gray, 1.3, 5
                )

                for (x, y, w, h) in faces_detected:
                    sample_count += 1
                    face_roi = gray[y:y+h, x:x+w]
                    faces.append(face_roi)
                    ids.append(1)  # ID for the user

                    # Draw rectangle
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(
                        frame,
                        f'Sample {sample_count}/50',
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 0, 0),
                        2
                    )

                cv2.imshow('Face Training', frame)
                cv2.waitKey(100)

            camera.release()
            cv2.destroyAllWindows()

            # Train the recognizer
            self.recognizer.train(faces, np.array(ids))

            # Save the model
            model_path = self.training_data_dir / f'{user_name}_model.yml'
            self.recognizer.save(str(model_path))

            print(f"Training complete for {user_name}")
            return True

        except Exception as e:
            print(f"Training error: {e}")
            return False

    def AuthenticateFace():
        """
        Authenticate user by comparing face with trained model.

        Returns:
            int: 1 if authenticated, 0 if failed
        """
        try:
            # Load trained model
            model_path = Path(__file__).parent.parent.parent / 'training_data' / 'default_model.yml'

            if not model_path.exists():
                print("No trained model found. Please train the model first.")
                return 0

            self.recognizer.read(str(model_path))

            # Capture face for authentication
            camera = cv2.VideoCapture(0)

            print("Authenticating... Please look at the camera")

            auth_attempts = 0
            authenticated = False

            while auth_attempts < 30 and not authenticated:
                ret, frame = camera.read()
                if not ret:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]

                    # Predict
                    id_, confidence = self.recognizer.predict(face_roi)

                    # Confidence threshold (lower is better for LBPH)
                    if confidence < 70:
                        authenticated = True
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            f'Authenticated: {confidence:.1f}',
                            (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )
                    else:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(
                            frame,
                            f'Not recognized: {confidence:.1f}',
                            (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2
                        )

                cv2.imshow('Face Authentication', frame)
                cv2.waitKey(100)
                auth_attempts += 1

            camera.release()
            cv2.destroyAllWindows()

            if authenticated:
                print("Authentication successful!")
                return 1
            else:
                print("Authentication failed!")
                return 0

        except Exception as e:
            print(f"Authentication error: {e}")
            return 0


# Create global instance for import
_authenticator = FaceAuthenticator()


def AuthenticateFace():
    """Public function for face authentication."""
    return _authenticator.AuthenticateFace()
