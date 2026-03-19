# Kanban Backend

FastAPI backend for the Kanban project management application.

## Features

- RESTful API for Kanban board management
- JWT-based authentication
- SQLite database with SQLAlchemy ORM
- AI integration via OpenRouter
- Real-time updates via WebSocket
- Comprehensive testing suite

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy
- **Authentication**: JWT with python-jose
- **AI Integration**: OpenRouter API
- **Package Manager**: uv
- **Testing**: pytest

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI application
│   ├── config/              # Configuration
│   ├── api/                 # API routes
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── database/            # Database utilities
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

## Installation

1. Install uv (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

## Development

Start the development server:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:

- **OpenAPI Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./kanban.db
JWT_SECRET_KEY=your-secret-key
OPENROUTER_API_KEY=your-api-key
```

## License

MIT
