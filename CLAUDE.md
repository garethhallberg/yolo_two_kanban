# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Kanban project management MVP with AI chat integration. FastAPI backend serves both API endpoints and the static NextJS build. MVP constraints: single hardcoded user (`user`/`password`), one board per user, runs locally in Docker.

## Commands

### Docker (primary)
```bash
./scripts/start-docker.sh   # start all services
./scripts/stop-docker.sh    # stop all services
```

### Local development
```bash
./scripts/start-dev.sh      # start backend + frontend
./scripts/stop-dev.sh       # stop
```

### Backend (manual)
```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
pytest                                        # run all tests
pytest tests/path/to/test_file.py::test_name  # run single test
pytest --cov=src --cov-report=html            # with coverage (target: 80%)
```

### Frontend (manual)
```bash
cd frontend
npm install
npm run dev    # dev server on port 3000
npm run build  # production build
npm test       # Jest tests
```

## Architecture

**Backend** (`backend/src/`):
- `main.py` — FastAPI app entry, mounts all routers, serves static frontend at `/`
- `api/routers/` — Route handlers: `auth`, `boards`, `columns`, `cards`, `ai`, `websocket`
- `services/` — Business logic layer (all db operations go through services)
- `models/` — SQLAlchemy ORM models (User, KanbanBoard, KanbanColumn, KanbanCard)
- `schemas/` — Pydantic request/response schemas
- `config/settings.py` — Pydantic settings loaded from environment variables
- `database/` — SQLAlchemy engine and session setup; SQLite at `./data/kanban.db`
- `migrations/` — Alembic migrations

**Frontend** (`frontend/`):
- `app/` — NextJS App Router pages and layout
- `components/kanban/` — Drag-and-drop board (@dnd-kit), columns, cards
- `components/chat/` — AI chat sidebar
- `components/auth/` — Login components
- `lib/context/` — React Context for global board/card state
- `lib/hooks/` — Custom hooks (useBoardState, useCardState, etc.)
- `lib/services/` — API client abstractions for each backend route group
- `lib/types/` — Centralized TypeScript interfaces

**Data flow**: Frontend context/hooks → `lib/services/` (REST calls) → FastAPI routers → services layer → SQLAlchemy → SQLite

**AI integration**: OpenRouter API with `openai/gpt-oss-120b` model. The AI chat sidebar sends board state as context and can return structured operations to create/move/edit cards. Config via `OPENROUTER_API_KEY` env var.

**WebSocket**: `/ws` endpoint for real-time board updates.

**Card positioning**: Uses float-based ordering (position field on KanbanCard) for drag-and-drop reordering.

## Environment

Copy `.env.example` to `.env`. Required variables:
- `OPENROUTER_API_KEY` — AI features
- `JWT_SECRET_KEY` — JWT token signing
- `DATABASE_URL` — defaults to `sqlite:///./data/kanban.db`

API docs available at `http://localhost:8000/api/docs` when running.

## Coding Standards (from AGENTS.md)

1. Use latest versions of libraries and idiomatic approaches
2. Keep it simple — never over-engineer, always simplify, no unnecessary defensive programming, no extra features
3. Be concise — no emojis ever
4. When hitting issues, identify root cause before trying a fix — prove with evidence, then fix the root cause

## Color Scheme

- Accent Yellow: `#ecad0a`
- Blue Primary: `#209dd7`
- Purple Secondary: `#753991`
- Dark Navy: `#032147`
- Gray Text: `#888888`

## Working Docs

Review `docs/PLAN.md` for the implementation plan context before working on features.
