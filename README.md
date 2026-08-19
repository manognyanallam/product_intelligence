# AI Product Intelligence Platform

> **UniHack by Unilog** — Turn minimal product data into rich, commerce-ready product intelligence.

## Overview

The AI Product Intelligence Platform transforms minimal manufacturer product information — Manufacturer Part Number (MPN), Brand, and Short Description — into structured, validated, commerce-ready product intelligence using a multi-agent AI pipeline powered by Google Gemini, LangChain, and ChromaDB.

## Architecture

```
Frontend (React + MUI) → FastAPI Backend → Multi-Agent Pipeline
    → Retrieval Agent → Product Intelligence Agent → Validation & Confidence Agent
    → ChromaDB Vector Store → JSON/PDF Export
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Material UI, Axios, React Router |
| Backend | Python 3.11, FastAPI, Pydantic |
| AI | Google Gemini API, LangChain |
| Vector DB | ChromaDB |
| Deployment | Frontend: Vercel, Backend: Render |

## Project Structure

```
├── frontend/          # React application
├── backend/           # FastAPI application
├── docs/              # Documentation
├── assets/            # Images, diagrams, etc.
├── README.md
├── .gitignore
└── .env.example
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env  # Add your GEMINI_API_KEY
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## License

MIT — Built for UniHack by Unilog 2025
