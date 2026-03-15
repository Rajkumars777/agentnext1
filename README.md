# NEXUS - Next-Gen AI Agent

NEXUS is a powerful AI-powered desktop automation and Robotic Process Automation (RPA) agent. It serves to empower users by allowing them to control their computer, manage files, manipulate spreadsheets, extract textual data from documents, and automate web operations through natural language commands or voice dictation.

---

## Features

- 🗣️ **Natural Language Commands** - Just type or speak what you want to do
- 📁 **File Operations** - Open, move, rename, delete files with voice/text commands
- 📊 **Excel Manipulation** - Read, write, add rows, apply styles to spreadsheets
- 🖥️ **App Control** - Launch and close any application
- 🔍 **Smart File Search** - Fast cached search across your system
- 📄 **Document Processing** - Extract text from PDF/Word, convert formats
- 🌐 **AI Web Automation** - Agent can browse, search, and extract data from the web using Playwright

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.10+   |
| Node.js     | 18+     |
| npm         | 9+      |

### Step 1: Clone the Repository

```powershell
git clone https://github.com/Rajkumars777/AI-agent---LTID.git
cd AI-agent---LTID
```

### Step 2: Setup Backend

```powershell
# Navigate to src
cd src

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (for web automation)
playwright install
```

### Step 3: Configure Environment

Create a `.env` file in the `src/` folder:

```env
# Required: Choose ONE LLM provider

# Option 1: OpenRouter (Recommended - works with many models)
OPENROUTER_API_KEY=your_openrouter_api_key

# Option 2: Google Gemini
GEMINI_API_KEY=your_gemini_api_key
```

Get your API key:

- **OpenRouter**: https://openrouter.ai/keys (supports GPT-4, Claude, Llama, etc.)
- **Gemini**: https://makersuite.google.com/app/apikey

### Step 4: Run Backend

```powershell
cd src
python main.py
```

✅ Backend runs on: `http://localhost:8000`

### Step 5: Setup & Run Frontend

Open a **new terminal**:

```powershell
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend runs on: `http://localhost:3000`

### Step 6: Use the App

1. Open `http://localhost:3000` in your browser
2. Provide commands through:
   - **Text Field**: Typing instructions manually into the input console.
   - **Voice**: By clicking the microphone interface, speaking locally (up to 5 seconds), verifying the transcribed text, and committing the command for execution.
3. Example commands:
   - `"open notepad"`
   - `"delete sample.xlsx"`
   - `"rename old.txt to new.txt"`
   - `"add a row to budget.xlsx with name John and amount 500"`
4. The server asynchronously executes user intents and returns the operative output.

---

## 📦 Dependencies

### Backend (Python)

| Package            | Purpose                    |
| ------------------ | -------------------------- |
| `fastapi`        | Web framework for API      |
| `uvicorn`        | ASGI server                |
| `python-dotenv`  | Environment variables      |
| `pyautogui`      | Desktop automation         |
| `pygetwindow`    | Window management          |
| `openpyxl`       | Excel read/write           |
| `pandas`         | Data manipulation          |
| `polars`         | Fast data processing       |
| `pymupdf`        | PDF text extraction        |
| `python-docx`    | Word document handling     |
| `playwright`     | Browser automation         |
| `faster-whisper` | Local voice-to-text (free) |
| `send2trash`     | Safe file deletion         |
| `AppOpener`      | Application launching      |
| `langchain`      | LLM framework              |
| `langgraph`      | Agent workflows            |

### Frontend (Node.js)

| Package           | Purpose         |
| ----------------- | --------------- |
| `next`          | React framework |
| `react`         | UI library      |
| `tailwindcss`   | Styling         |
| `framer-motion` | Animations      |
| `lucide-react`  | Icons           |
| `axios`         | API calls       |

---

## 📂 Project Structure

```
AI-agent---LTID/
├── src/                             # Python FastAPI Backend
│   ├── main.py                      # 🚀 Entry point - FastAPI app
│   │
│   ├── api/                         # 🌐 API layer
│   │   └── routers/
│   │       ├── agent.py             # /agent/* endpoints
│   │       ├── events.py            # SSE event streaming
│   │       ├── openclaw.py          # OpenClaw integration endpoints
│   │       └── settings.py          # /settings/* endpoints
│   │
│   ├── core/                        # 🧠 AI brain
│   │   ├── agent.py                 # Main agent routing logic
│   │   ├── openclaw_client.py       # Client for OpenClaw process
│   │   ├── openclaw_process.py      # OpenClaw background process
│   │   └── security/                # Security & credential management
│   │       ├── manager.py           # Security manager
│   │       └── credential_handler.py# API key/credential handler
│   │
│   ├── requirements.txt             # Python dependencies
│   └── .env                         # API keys (create this)
│
├── frontend/                        # Next.js React Frontend
│   └── src/
│       ├── app/                     # Next.js App Router pages
│       │   ├── page.tsx             # Main dashboard page
│       │   └── layout.tsx           # Root layout
│       │
│       ├── components/              # React components
│       │   ├── AriaAssistant.tsx    # 🎙️ Voice assistant UI (Aria)
│       │   ├── InputConsole.tsx     # Command input + mic button
│       │   ├── TimelineFeed.tsx     # Live task event timeline
│       │   ├── RecentsHistory.tsx   # Recent commands history
│       │   ├── ResultCard.tsx       # Task result display card
│       │   ├── SettingsPanel.tsx    # App settings panel
│       │   ├── VoiceControlPanel.tsx# Voice control panel
│       │   └── ...                  # Other UI components
│       │
│       ├── hooks/                   # Custom React hooks
│       ├── lib/                     # Utility libraries
│       ├── styles/                  # Global and component styles
│       └── types/                   # TypeScript definitions
│
├── NEXUS_Documentation.md           # Comprehensive project details
├── requirements.txt                 # Project-level dependencies
└── README.md                        # This file
```
```

---

## 💡 Example Commands

| Command                                            | What it does                   |
| -------------------------------------------------- | ------------------------------ |
| `open notepad`                                   | Launches Notepad               |
| `open excel`                                     | Launches Microsoft Excel       |
| `close chrome`                                   | Closes Chrome browser          |
| `delete report.pdf`                              | Moves file to Recycle Bin      |
| `rename old.txt to new.txt`                      | Renames the file               |
| `move data.xlsx to Documents`                    | Moves file to Documents folder |
| `read sample.xlsx`                               | Shows Excel contents           |
| `add row to data.xlsx with name John and age 25` | Adds a new row                 |

---

## 🛠️ Troubleshooting

### Backend won't start

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend errors

```powershell
# Clear npm cache and reinstall
rm -rf node_modules
npm install
```

### "API key not found" error

- Make sure `.env` file exists in `src/` folder
- Check that API key is correctly set (no extra spaces)

### Port Conflict Errors

- Ensure ports `3000` (Frontend) or `8000` (Backend) are not currently in use by other applications.

### Voice Transcription Initial Delay

- Faster Whisper models are cached locally. The initial boot demands an active internet connection to securely fetch model weights locally.
- Permit microphone inputs inside the browser space.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Made with ❤️ by Rajkumar
