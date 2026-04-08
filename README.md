# 🍽️ TableVision AI

> Real-time restaurant floor intelligence powered by GPT-4o Vision

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red) ![GPT-4o](https://img.shields.io/badge/GPT--4o-Vision-purple)

---

## What It Does

TableVision AI uses an overhead camera (or uploaded video/image) to:
- Detect which tables are occupied and how many seats are taken
- Maintain a live color-coded floor map
- Suggest the best table for any party size
- Estimate time remaining for occupied tables
- Analyze recorded video frame-by-frame

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit |
| Backend API | FastAPI + Uvicorn |
| AI Vision | GPT-4o via OpenRouter |
| Image/Video | OpenCV |
| Config | JSON |

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Pavan-Bontha/tablevision.git
cd tablevision
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openrouter_key_here
```
Get your key from [OpenRouter](https://openrouter.ai)

### 5. Run the backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 6. Run the frontend (new terminal)
```bash
streamlit run frontend/app.py
```

Open: **http://localhost:8501**

---

## Project Structure

```
tablevision/
├── backend/
│   ├── main.py              # FastAPI endpoints
│   ├── vision_analyzer.py   # GPT-4o vision integration
│   ├── table_state.py       # Floor state engine
│   └── __init__.py
├── config/
│   └── restaurant_config.json  # Table layout
├── frontend/
│   └── app.py               # Streamlit dashboard
├── requirements.txt
├── .env                     # NOT committed — add your key here
└── .gitignore
```

---

## How It Works

1. Upload a camera frame or video via the Streamlit UI
2. FastAPI crops each table region using OpenCV
3. Each crop is sent to GPT-4o Vision with a structured prompt
4. GPT-4o returns JSON: `{ occupied_seats, has_people, confidence }`
5. Floor state updates and the live map refreshes

---

## Built at AI-Nexus 24Hr Hackathon
