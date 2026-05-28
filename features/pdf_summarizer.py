"""
PDF Summarizer Module for Jarvis.
Extracts text from PDFs and generates AI-powered summaries, key points, and viva questions.
"""
import os
import tempfile
import eel
from typing import Dict, Optional
import google.generativeai as genai


class PDFSummarizer:
    """Handles PDF text extraction and AI-based summarization."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the PDF summarizer with optional API key."""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("Warning: No Google API key found. AI features will use fallback mode.")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            str: Extracted text content
        """
        try:
            import pdfplumber

            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"

            return text.strip()

        except ImportError:
            # Fallback to PyPDF2 if pdfplumber not available
            try:
                from PyPDF2 import PdfReader

                text = ""
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"

                return text.strip()

            except ImportError as e:
                raise ImportError(
                    "Neither pdfplumber nor PyPDF2 is installed. "
                    "Please install one: pip install pdfplumber or pip install PyPDF2"
                )

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")

    def summarize_with_ai(self, text: str) -> Dict[str, str]:
        """
        Generate summary, key points, and viva questions using AI.

        Args:
            text: Text content to summarize

        Returns:
            Dict containing summary, key_points, and viva_questions
        """
        if not text or len(text.strip()) < 50:
            return {
                'summary': 'Text is too short to summarize.',
                'key_points': 'Insufficient content for key points.',
                'viva_questions': 'Not enough content to generate questions.'
            }

        # Truncate text if too long (Gemini has token limits)
        max_chars = 20000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        # Use AI if available
        if self.model:
            return self._summarize_with_gemini(text)
        else:
            return self._summarize_fallback(text)

    def _summarize_with_gemini(self, text: str) -> Dict[str, str]:
        """Use Google Gemini for summarization."""
        try:
            prompt = f"""Analyze the following text and provide:

1. A concise summary (3-4 sentences)
2. Key points (5-7 bullet points)
3. Viva/exam questions (5-7 questions)

Format your response exactly as:

SUMMARY:
[Your summary here]

KEY_POINTS:
- Point 1
- Point 2
- Point 3
...

VIVA_QUESTIONS:
Q1: [Question]
Q2: [Question]
...

Text to analyze:
{text}"""

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Parse the response
            return self._parse_ai_response(response_text)

        except Exception as e:
            print(f"AI summarization error: {e}")
            return self._summarize_fallback(text)

    def _parse_ai_response(self, response_text: str) -> Dict[str, str]:
        """Parse AI response into structured format."""
        result = {
            'summary': '',
            'key_points': '',
            'viva_questions': ''
        }

        sections = ['SUMMARY:', 'KEY_POINTS:', 'VIVA_QUESTIONS:']
        current_section = None
        current_content = []

        for line in response_text.split('\n'):
            line = line.strip()

            if not line:
                continue

            # Check if we're entering a new section
            found_section = False
            for section in sections:
                if section in line.upper():
                    # Save previous section
                    if current_section:
                        result[current_section] = '\n'.join(current_content).strip()

                    current_section = section.replace(':', '').lower()
                    current_content = []
                    found_section = True
                    break

            if not found_section and current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            result[current_section] = '\n'.join(current_content).strip()

        return result

    def _summarize_fallback(self, text: str) -> Dict[str, str]:
        """Fallback summarization without AI (basic extractive)."""
        # Simple extractive summary - take first few sentences
        sentences = text.split('. ')
        summary_sentences = sentences[:min(5, len(sentences))]
        summary = '. '.join(summary_sentences) + '.' if sentences else text

        # Extract key points (simple keyword-based)
        words = text.split()
        word_freq = {}
        for word in words:
            word_lower = word.lower().strip('.,!?')
            if len(word_lower) > 4:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1

        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:7]
        key_points = '\n'.join([f"- {word}" for word, count in top_keywords])

        # Generate basic questions (without NLP, just templates)
        viva_questions = """Q1: What is the main topic discussed in this text?
Q2: Can you explain the key concepts mentioned?
Q3: What are the important points to remember?
Q4: How would you apply this knowledge?
Q5: What are the practical implications?"""

        return {
            'summary': summary,
            'key_points': key_points,
            'viva_questions': viva_questions
        }


# Global instance
_summarizer = None


def get_summarizer():
    """Get or create PDF summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = PDFSummarizer()
    return _summarizer


# Eel-exposed functions
@eel.expose
def summarize_pdf(file_path: str) -> Dict[str, str]:
    """
    Summarize a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Dict with summary, key_points, and viva_questions
    """
    try:
        summarizer = get_summarizer()

        # Extract text
        text = summarizer.extract_text_from_pdf(file_path)

        # Generate summary
        result = summarizer.summarize_with_ai(text)

        return {
            'success': True,
            'summary': result.get('summary', ''),
            'key_points': result.get('key_points', ''),
            'viva_questions': result.get('viva_questions', ''),
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'summary': '',
            'key_points': '',
            'viva_questions': '',
            'error': str(e)
        }


@eel.expose
def save_uploaded_pdf(file_data: str, filename: str) -> Dict[str, str]:
    """
    Save uploaded PDF to temporary location.

    Args:
        file_data: Base64 encoded file data
        filename: Original filename

    Returns:
        Dict with file_path and success status
    """
    try:
        import base64
        import uuid

        # Create temp directory for uploads
        upload_dir = os.path.join(tempfile.gettempdir(), 'jarvis_pdfs')
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Decode and save
        with open(file_path, 'wb') as f:
            if file_data.startswith('data:application/pdf;base64,'):
                file_data = file_data.replace('data:application/pdf;base64,', '')
            f.write(base64.b64decode(file_data))

        return {
            'success': True,
            'file_path': file_path,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'file_path': None,
            'error': str(e)
        }
