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

| Python      | 3.10+   |
| Node.js     | 18+     |
| npm         | 9+      |

> [!NOTE]
> OpenClaw is now a project dependency. Running `npm install` in the `frontend/` directory will automatically install it.

### Step 1: Clone the Repository

```powershell
git clone https://github.com/Rajkumars777/AI-agent---LTID.git
cd AI-agent---LTID
```

### Step 2-4: Automated Setup (Windows)

Just run the following command in the root directory:

```powershell
.\setup.bat
```

This will:
- Create a virtual environment and install Python dependencies.
- Install Playwright browsers.
- Install Node.js dependencies.
- Create a template `.env` file in `src/`.

### Step 5: Configure Environment

Open `src/.env` and add your API keys. Refer to `.env.example` in the root for a template.

### Step 6: Build Tauri Desktop App (Optional)

If you want a native desktop window instead of a browser tab, run:

```powershell
.\build_tauri.bat
```

The resulting EXE will be in `frontend/src-tauri/target/release/bundle/msi/`.

### Step 7: Run the App

Run the following command to start both the backend and frontend:

```powershell
.\run.bat
```

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
