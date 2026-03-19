# Kanban Project Management MVP

A modern project management application with Kanban board and AI chat integration.

## Features

- **Kanban Board**: Drag-and-drop cards across customizable columns
- **AI Assistant**: Sidebar chat with AI that can understand and modify the Kanban board
- **User Authentication**: JWT-based authentication (hardcoded for MVP)
- **Real-time Updates**: WebSocket support for live updates
- **Persistent Storage**: SQLite database with proper relational schema
- **Docker Support**: Containerized deployment with hot-reload for development

## Technology Stack

### Backend

- **Framework**: FastAPI with Python 3.12+
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **AI Integration**: OpenRouter API with structured outputs
- **Package Manager**: uv
- **Testing**: pytest with 80% coverage target

### Frontend

- **Framework**: NextJS 15+ with TypeScript
- **Styling**: Tailwind CSS with custom color scheme
- **Drag & Drop**: @dnd-kit libraries
- **State Management**: React Context + custom hooks
- **Testing**: Jest + React Testing Library + Playwright

### DevOps

- **Containerization**: Docker with multi-stage builds
- **Orchestration**: docker-compose for development
- **Scripts**: Cross-platform start/stop scripts
- **CI/CD**: GitHub Actions (planned)

## Project Structure

```
yolo_two_kanban/
├── backend/                 # FastAPI backend
│   ├── src/                # Source code
│   │   ├── config/         # Configuration
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Test files
│   └── pyproject.toml      # Python dependencies
├── frontend/               # NextJS frontend
│   ├── app/                # NextJS App Router
│   ├── components/         # React components
│   ├── lib/                # Utilities and API client
│   └── styles/             # Tailwind configuration
├── scripts/                # Platform-specific scripts
├── docs/                   # Documentation
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Development environment
└── .env.example            # Environment variables template
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.12+ and uv

### Using Docker (Recommended)

```bash
# Start the application
./scripts/start-docker.sh

# Stop the application
./scripts/stop-docker.sh
```

### Local Development

```bash
# Start backend and frontend separately
./scripts/start-dev.sh

# Stop development servers
./scripts/stop-dev.sh
```

### Manual Setup

1. **Backend**:

   ```bash
   cd backend
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend** (to be implemented in Part 3):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## API Documentation

Once the backend is running:

- **OpenAPI Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

## Development Status

### ✅ Completed (Part 2: Scaffolding & Docker Infrastructure)

- [x] Project structure with proper separation
- [x] FastAPI backend with basic endpoints
- [x] Dockerfile with multi-stage build
- [x] docker-compose.yml with hot-reload
- [x] Cross-platform start/stop scripts
- [x] Python environment with uv
- [x] Basic logging and error handling
- [x] .gitignore and .dockerignore files
- [x] Backend serving API endpoints successfully tested

### 🔄 In Progress

- **Part 3**: Frontend Setup & Kanban Board
- **Part 4**: Authentication System
- **Part 5**: Database Modeling
- **Part 6**: Backend API Development
- **Part 7**: Frontend-Backend Integration
- **Part 8**: AI Connectivity Setup
- **Part 9**: AI-Powered Kanban Operations
- **Part 10**: AI Chat Interface & Real-time Updates

## Color Scheme

The application uses a consistent color scheme:

- **Accent Yellow**: `#ecad0a` - accent lines, highlights
- **Blue Primary**: `#209dd7` - links, key sections
- **Purple Secondary**: `#753991` - submit buttons, important actions
- **Dark Navy**: `#032147` - main headings
- **Gray Text**: `#888888` - supporting text, labels

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (to be implemented)
cd frontend
npm test
npm run test:e2e
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

Required variables:

- `OPENROUTER_API_KEY`: Your OpenRouter API key for AI features
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `DATABASE_URL`: Database connection string

## Contributing

1. Follow the coding standards in `AGENTS.md`
2. Maintain 80% test coverage
3. Keep implementations simple and focused
4. Document all changes

## License

MIT

A simple Kanban board application built with FastAPI and React. This project is designed to help you manage your tasks and projects efficiently using a visual board.
