# 🏋️ Fitness Buddy AI

> **AI-powered personal fitness coach** built with **FastAPI** + **IBM Watsonx.ai Granite 3.3**

A production-ready, full-stack web application that acts as an intelligent virtual fitness coach. It provides personalised workout plans, nutrition guidance, habit tracking, progress monitoring, and motivational coaching — all powered by IBM's Granite large language models via Watsonx.ai.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **AI Chat** | Real-time conversation with Granite 3.3 — your virtual fitness coach |
| 📊 **Dashboard** | Stats, BMI meter, weekly activity chart, motivational quotes |
| 💪 **Workout Planner** | Personalised multi-day plans (home, HIIT, yoga, strength, calisthenics) |
| 🥗 **Nutrition** | Macro calculations, meal plans (Indian + international), hydration targets |
| 📅 **Habit Tracker** | Daily logging of water, sleep, steps, mood, and workouts |
| 👤 **Profile** | Full fitness profile with BMI & TDEE calculation |
| 🌙 **Dark/Light Mode** | Full theme toggle with glassmorphism UI |
| 📱 **Mobile-First** | Fully responsive Bootstrap 5 design |

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async Python web framework
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [Pydantic v2](https://docs.pydantic.dev/) — data validation
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — environment config
- [IBM Watsonx.ai SDK](https://ibm.github.io/watson-machine-learning-py-sdk/) — Granite LLM

**Frontend**
- Bootstrap 5.3
- Vanilla JavaScript (ES2020+)
- Glassmorphism CSS design system
- SVG-based charts (no external chart library)

---

## 📁 Project Structure

```
fitness-buddy/
│
├── app/
│   ├── main.py              # FastAPI app factory & routes
│   ├── config.py            # Settings + AGENT_INSTRUCTIONS
│   ├── dependencies.py      # DI helpers
│   ├── models.py            # In-memory data models
│   ├── schemas.py           # Pydantic request/response schemas
│   │
│   ├── routes/
│   │   ├── chat.py          # POST /api/chat
│   │   ├── profile.py       # GET/POST /api/profile
│   │   ├── workout.py       # POST /api/workout/plan
│   │   ├── nutrition.py     # POST /api/nutrition/plan
│   │   ├── dashboard.py     # GET /api/dashboard/stats
│   │   └── habits.py        # POST /api/habits/log
│   │
│   ├── services/
│   │   ├── watsonx_service.py   # IBM Watsonx.ai integration
│   │   ├── fitness_service.py   # Workout plan generation
│   │   ├── nutrition_service.py # Macro & meal plan calc
│   │   ├── motivation_service.py# Quotes & wellness scoring
│   │   └── bmi_service.py       # BMI / TDEE calculations
│   │
│   ├── templates/
│   │   └── index.html       # Single-page application
│   │
│   └── static/
│       ├── styles.css       # Glassmorphism stylesheet
│       └── app.js           # SPA JavaScript
│
├── .env.example             # Template for credentials
├── requirements.txt
├── run.py                   # Uvicorn launcher
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone or unzip the project

```bash
# If from zip:
cd fitness-buddy

# If cloning:
git clone <repo-url>
cd fitness-buddy
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure IBM Watsonx.ai credentials

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
IBM_CLOUD_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**How to get credentials:**
1. Log in to [IBM Cloud](https://cloud.ibm.com)
2. Go to **Manage → Access (IAM) → API Keys** → Create an API Key
3. Go to [IBM Watsonx.ai](https://dataplatform.cloud.ibm.com)
4. Open your project → **Manage** tab → copy the **Project ID**

### 5. Run the application

```bash
python run.py
```

Or with auto-reload in development:

```bash
python run.py --reload
```

Open your browser: **http://localhost:8000**

---

## 🌐 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web application (SPA) |
| GET | `/health` | Health check |
| GET | `/version` | Version info |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| POST | `/api/chat` | AI chat with Granite |
| GET | `/api/profile` | Get user profile |
| POST | `/api/profile` | Update user profile |
| POST | `/api/workout/plan` | Generate workout plan |
| GET | `/api/workout/quick/{type}` | Quick workout |
| POST | `/api/nutrition/plan` | Nutrition plan + macros |
| GET | `/api/nutrition/advice` | AI nutrition advice |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/motivation` | AI motivational message |
| POST | `/api/habits/log` | Log daily habits |
| GET | `/api/habits/today` | Today's habit log |
| GET | `/api/habits/history` | Last 30 days of logs |

---

## 🤖 Customising the AI Agent

Open [`app/config.py`](app/config.py) and edit the `AGENT_INSTRUCTIONS` constant at the top of the file. You can customise:

- **Personality & tone** — cheerful, strict, motivational
- **Fitness specialisation** — yoga, powerlifting, running, etc.
- **Workout style** — home, gym, outdoor
- **Nutrition guidance** — vegan, Ayurvedic, keto-friendly
- **Goal-setting behaviour** — SMART goals, milestones
- **Injury prevention rules**
- **Medical disclaimer text**
- **Language preferences** (English, Hindi, Hinglish)

```python
# app/config.py — edit this block:
AGENT_INSTRUCTIONS = """
You are Fitness Buddy, a warm, knowledgeable...
# Add your customisations here
"""
```

---

## ⚙️ Configuration Reference

All settings are in `.env`:

| Variable | Default | Description |
|---|---|---|
| `IBM_CLOUD_API_KEY` | — | IBM Cloud API key (required) |
| `WATSONX_PROJECT_ID` | — | Watsonx.ai project ID (required) |
| `WATSONX_URL` | `https://us-south.ml.cloud.ibm.com` | Regional endpoint |
| `WATSONX_MODEL_ID` | `ibm/granite-3-3-8b-instruct` | Granite model ID |
| `WATSONX_MAX_TOKENS` | `1024` | Max tokens per response |
| `WATSONX_TEMPERATURE` | `0.7` | Response creativity (0–1) |
| `APP_ENV` | `development` | `development` or `production` |
| `PORT` | `8000` | Server port |
| `DEBUG` | `true` | Enable auto-reload |

---

## 🔄 Available Granite Models

Change `WATSONX_MODEL_ID` in `.env` to switch models:

| Model ID | Best For |
|---|---|
| `ibm/granite-3-3-8b-instruct` | Balanced performance (default) |
| `ibm/granite-3-8b-instruct` | Fast responses |
| `ibm/granite-3-2b-instruct` | Lightweight/faster |
| `ibm/granite-20b-multilingual` | Multilingual support |

---

## 🏭 Production Deployment

### Using Uvicorn with multiple workers:

```bash
APP_ENV=production DEBUG=false python run.py --workers 4
```

### Using Gunicorn + Uvicorn workers:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "run.py"]
```

```bash
docker build -t fitness-buddy .
docker run -p 8000:8000 --env-file .env fitness-buddy
```

---

## 📝 Development Notes

- The app uses **in-memory storage** by default. All data resets on server restart.
- To persist data, replace `AppState` in [`app/models.py`](app/models.py) with a SQLAlchemy or SQLModel database backend.
- The `AGENT_INSTRUCTIONS` block in [`app/config.py`](app/config.py) is the single source of truth for AI personality.
- All AI logic is isolated in [`app/services/watsonx_service.py`](app/services/watsonx_service.py).

---

## 🙏 Credits

- **IBM Watsonx.ai** — Granite foundation models
- **FastAPI** — Modern Python web framework
- **Bootstrap 5** — UI framework
- Built with ❤️ for fitness enthusiasts everywhere
