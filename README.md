# MindGuard Backend

FastAPI backend for the Mental Health Monitoring System. Provides REST APIs for user authentication, PHQ-9 assessments, mood ratings, and AI-powered feedback.

## Features

- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **PHQ-9 Assessments**: Standard depression screening questionnaire
- **Mood Ratings**: Daily mood tracking with trend analysis
- **Voice Emotion Detection**: AI-powered audio emotion analysis
- **AI Feedback**: Groq-powered personalized mental health insights
- **Risk Assessment**: Automatic risk level calculation based on responses

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT (python-jose) + bcrypt
- **AI/ML**: Groq API, HuggingFace Transformers
- **Audio Processing**: librosa, soundfile, pydub

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Groq API key ([get one here](https://console.groq.com/))

## Installation

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Using venv:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Using uv (recommended):**
```bash
uv venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

**Using pip:**
```bash
pip install -r requirements.txt
```

**Using uv:**
```bash
uv pip install -r requirements.txt
```

> **Note**: The ML dependencies (torch, transformers, librosa) are large (~4-5 GB). If you don't need voice emotion detection, you can skip them by creating a minimal requirements file.

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# Copy the example file
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux
```

Edit `.env` with your values:

```env
# Required
GROQ_API_KEY=your-groq-api-key-here

# Optional (for voice emotion detection)
HUGGINGFACE_TOKEN=your-huggingface-token

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./mental_health.db

# JWT Secret (generate a secure key for production)
JWT_SECRET=your-secure-random-key

# CORS Origins (frontend URL)
CORS_ORIGINS=http://localhost:5173
```

### 5. Run the Server

**Development mode:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Configuration and settings
│   ├── database.py       # Database connection setup
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   ├── assessment.py
│   │   ├── rating.py
│   │   └── feedback.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   ├── assessment.py
│   │   ├── rating.py
│   │   └── voice.py
│   ├── routers/          # API endpoints
│   │   ├── users.py
│   │   ├── assessments.py
│   │   ├── ratings.py
│   │   └── voice.py
│   ├── services/         # Business logic
│   │   ├── phq9_service.py
│   │   ├── risk_service.py
│   │   ├── trend_service.py
│   │   ├── voice_service.py
│   │   └── feedback_service.py
│   └── utils/            # Utilities
│       ├── constants.py
│       └── security.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register` | Register new user |
| POST | `/api/users/login` | Login and get JWT token |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile |
| PUT | `/api/users/me` | Update user profile |

### Assessments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/assessments/` | Submit PHQ-9 assessment |
| GET | `/api/assessments/` | Get user's assessments |
| GET | `/api/assessments/{id}` | Get specific assessment |
| GET | `/api/assessments/trends` | Get assessment trends |

### Ratings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ratings/` | Submit mood rating |
| GET | `/api/ratings/` | Get user's ratings |
| GET | `/api/ratings/trends` | Get rating trends |

### Voice

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/voice/analyze` | Analyze voice emotion |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for AI feedback |
| `DATABASE_URL` | No | Database URL (default: SQLite) |
| `JWT_SECRET` | No | JWT signing key (auto-generated if not set) |
| `CORS_ORIGINS` | No | Allowed CORS origins (comma-separated) |
| `HUGGINGFACE_TOKEN` | No | HuggingFace token for voice emotion |
| `DEBUG` | No | Enable debug mode (default: false) |

## Database

### Development (SQLite)

The default configuration uses SQLite, which requires no setup. The database file is created automatically at `./mental_health.db`.

### Production (PostgreSQL)

For production, use PostgreSQL:

1. Set the `DATABASE_URL` environment variable:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
   ```

2. Install asyncpg:
   ```bash
   pip install asyncpg
   ```

## Docker

### Build Image

```bash
docker build -t mindguard-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env mindguard-backend
```

### Using Docker Compose

From the project root:

```bash
docker-compose up backend
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Troubleshooting

### Port Already in Use

If port 8000 is in use, change the port:
```bash
uvicorn app.main:app --port 8001
```

### Import Errors

Make sure you're in the backend directory and the virtual environment is activated:
```bash
cd backend
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### Database Errors

Delete the SQLite database file and restart the server:
```bash
del mental_health.db  # Windows
rm mental_health.db    # macOS/Linux
```

### Memory Issues with Voice Feature

The voice emotion model requires ~2GB RAM. If you're getting memory errors:
- Use a machine with more RAM
- Or disable voice emotion by removing torch/transformers from requirements

## License

MIT License
