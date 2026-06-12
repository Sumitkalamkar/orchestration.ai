# OrchestrAI — Flutter UI for LangGraph Report Generator

A Flutter frontend for your LangGraph orchestrator-worker report generation notebook.

---

## Project Structure

```
report_gen_app/
├── lib/
│   ├── main.dart                  # App entry, theme
│   ├── models/
│   │   └── report_model.dart      # Data models & enums
│   ├── services/
│   │   └── report_service.dart    # HTTP calls to backend
│   └── screens/
│       ├── home_screen.dart       # Topic input + suggestions
│       └── report_screen.dart     # Live progress + report viewer
├── backend.py                     # FastAPI wrapper for your LangGraph code
└── pubspec.yaml
```

---

## Setup

### 1. Backend (FastAPI wrapper)

Install dependencies:
```bash
pip install fastapi uvicorn langchain-groq langgraph python-dotenv
```

Add your `.env` file in the project root:
```
GROQ_API_KEY=your_groq_key_here
```

Run the backend:
```bash
uvicorn backend:app --reload --port 8000
```

Test it:
```bash
curl http://localhost:8000/health
```

---

### 2. Flutter App

Install Flutter dependencies:
```bash
flutter pub get
```

Run on your device/emulator:
```bash
flutter run
```

> **Note:** For Android emulator, change `baseUrl` in `lib/services/report_service.dart`  
> from `http://localhost:8000` → `http://10.0.2.2:8000`

---

## API Endpoints Used

| Endpoint | Purpose |
|---|---|
| `POST /plan-sections` | Returns section names + descriptions (used for live progress UI) |
| `POST /generate-report` | Runs full LangGraph graph, returns complete report |

---

## Features

- **Live progress view** — shows section planning, parallel writing status, synthesis
- **Markdown renderer** — full styled markdown report with code blocks, headers, lists
- **Copy to clipboard** — one-tap copy of the full markdown report
- **Topic suggestions** — pre-filled example topics
- **Dark theme** — designed for readability during long reading sessions
