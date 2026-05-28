# 🤖 Jarvis - Your Personal Desktop Voice Assistant

Jarvis is a smart and customizable desktop assistant built using **Python**, **Eel**, **HTML/CSS**, and **JavaScript**. It helps you control your PC and mobile with simple **voice** or **typed commands**.

From launching apps to making calls and chatting, Jarvis brings AI and automation to your fingertips.

---

## ✨ Features

### Core Features
- 🎙️ Control via **Voice & Typing**
- 📞 Make Phone Calls via Mobile (Android)
- 📲 Pickup & Disconnect Calls
- 💻 Launch Desktop Applications
- 🌐 Open Your Favorite URLs
- 📔 Built-in Phone Book
- 🙋 Store and Use Your Personal Details
- 🤖 Chat Interaction
- 🎵 Play Videos/Songs on YouTube & Spotify
- 🌤️ Check Weather Updates

### 🆕 NEW FEATURES

#### 📄 AI Notes Summarizer (PDF)
- Upload PDF documents directly from UI
- Extract text using pdfplumber/PyPDF2
- AI-powered summarization using Google Gemini
- Generate structured output:
  - Short summary
  - Key points (bullet format)
  - Viva/exam questions
- Save summaries to Supabase database
- Text-to-speech for summaries

#### 🌍 Multilingual Voice Mode
- Support for 3 languages:
  - English (en)
  - Hindi (hi)
  - Marathi (mr)
- Switch languages via UI or voice command
- Text-to-speech in selected language (gTTS)
- Speech-to-text recognition in multiple languages
- Automatic fallback to English if language fails
- Voice mode toggle for hands-free operation

---

## 🖼️ Demo

### 🔐 Face Authentication  
![Face Authentication](https://github.com/digambar2002/image-hosting/blob/main/How_to_make_Jarvis_in_Python__voice_assistant__jarvis_iron_m.gif)

### 🎤 Speech to Text Recognition  
![Speech to Text](https://github.com/digambar2002/image-hosting/blob/main/e.gif)

### 🎵 Play Music on Spotify  
![Play Music in Spotify](https://github.com/digambar2002/image-hosting/blob/main/2.gif)

---

## 🛠️ Tech Stack

- **Python** - Core logic
- **Eel** - Web-Python integration
- **HTML/CSS/JS** - Interactive frontend
- **Supabase** - Database for storing summaries and preferences
- **Google Gemini AI** - PDF summarization
- **gTTS** - Multilingual text-to-speech
- **pdfplumber/PyPDF2** - PDF text extraction

---

## 📁 Project Structure

```
jarvis/
├── engine/                    # Core engine modules
│   ├── __init__.py
│   ├── features.py           # Voice interaction, TTS, hotword
│   ├── command.py            # Command processing
│   └── auth/
│       ├── __init__.py
│       └── recoganize.py     # Face authentication
│
├── features/                  # NEW: Independent feature modules
│   ├── __init__.py
│   ├── pdf_summarizer.py     # PDF summarization module
│   └── multilingual_voice.py # Multilingual TTS/STT module
│
├── www/                       # Web UI
│   ├── index.html            # Main interface
│   ├── css/
│   │   └── style.css         # Modern, responsive styles
│   └── js/
│       └── app.js            # Frontend logic
│
├── main.py                    # Main entry point
├── run.py                     # Multi-process runner
├── device.bat                 # ADB device connection
├── jarvis.db                  # Local SQLite database
├── .env                       # Environment variables
└── requirements.txt           # Python dependencies
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/jarvis-python-assistant.git
cd jarvis-python-assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Supabase Configuration (Database)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Google AI for PDF Summarization (Optional)
GOOGLE_API_KEY=your_google_api_key

# Picovoice for Hotword Detection (Optional)
PICOVOICE_ACCESS_KEY=your_picovoice_key
```

### 4. Run the Application

```bash
python run.py
```

Or run the main module directly:

```bash
python main.py
```

---

## 🎯 Usage

### Voice Commands

Click the microphone button or use the text input to interact with Jarvis:

- **"What time is it?"** - Get current time
- **"What's the date today?"** - Get current date
- **"Open YouTube"** - Launch YouTube in browser
- **"Search for [query]"** - Perform Google search
- **"Open [application]"** - Launch desktop applications

### PDF Summarizer

1. Navigate to the **Features** tab
2. Click or drag-and-drop a PDF file
3. Click **"Generate Summary"**
4. View the AI-generated:
   - Summary of content
   - Key points
   - Viva/exam questions
5. Save or listen to the summary

### Multilingual Mode

1. Select language from dropdown: **English**, **Hindi**, or **Marathi**
2. Click the microphone button to speak in your selected language
3. Jarvis will respond in the same language
4. Use the **Voice Mode Toggle** for continuous voice interaction

---

## 🔒 Security Features

- Face authentication using OpenCV
- Row Level Security (RLS) on Supabase database
- Encrypted storage of user preferences
- Secure API key management via .env

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License.

---

## 🔧 Troubleshooting

### Common Issues

1. **"Module not found" error**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **Face authentication not working**
   - Ensure OpenCV is installed
   - Check camera permissions
   - Train the model first by running: `python -m engine.auth.recoganize`

3. **No audio output**
   - Check system volume
   - Verify pyttsx3 is working: `python -c "import pyttsx3; e=pyttsx3.init(); e.say('test'); e.runAndWait()"`

4. **PDF summarization fails**
   - Add `GOOGLE_API_KEY` to `.env file`
   - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Ensure internet connection is available
