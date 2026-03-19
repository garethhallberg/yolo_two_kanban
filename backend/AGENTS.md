# Backend Architecture Documentation

## Overview

The backend is a FastAPI application with SQLite database, implementing a RESTful API for the Kanban project management application with AI integration via OpenRouter.

## Technology Stack

### Core Frameworks

- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **Python 3.11+**: Latest stable Python version
- **SQLAlchemy 2.0**: ORM for database operations
- **Alembic**: Database migrations
- **Pydantic 2.0**: Data validation and serialization
- **uv**: Fast Python package manager

### Key Libraries

- **python-jose**: JWT token handling
- **passlib[bcrypt]**: Password hashing
- **httpx**: Async HTTP client for OpenRouter API
- **structlog**: Structured logging
- **python-multipart**: File upload support
- **websockets**: WebSocket support for real-time updates
- **redis** (optional): For caching and WebSocket pub/sub

### Testing

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **httpx**: Test client
- **factory-boy**: Test data factories

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py      # Pydantic settings
│   │   └── database.py      # Database configuration
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   ├── middleware.py    # Custom middleware
│   │   ├── routers/         # Route modules
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # Authentication routes
│   │   │   ├── boards.py    # Board management
│   │   │   ├── columns.py   # Column operations
│   │   │   ├── cards.py     # Card operations
│   │   │   └── ai.py        # AI chat endpoints
│   │   └── websocket.py     # WebSocket handlers
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model class
│   │   ├── user.py          # User model
│   │   ├── board.py         # Board model
│   │   ├── column.py        # Column model
│   │   ├── card.py          # Card model
│   │   └── conversation.py  # AI conversation history
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication schemas
│   │   ├── board.py         # Board schemas
│   │   ├── column.py        # Column schemas
│   │   ├── card.py          # Card schemas
│   │   ├── ai.py            # AI request/response schemas
│   │   └── websocket.py     # WebSocket message schemas
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication service
│   │   ├── board.py         # Board service
│   │   ├── ai.py            # AI service (OpenRouter integration)
│   │   └── websocket.py     # WebSocket service
│   ├── database/            # Database utilities
│   │   ├── __init__.py
│   │   ├── session.py       # Database session management
│   │   └── init_db.py       # Database initialization
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py      # Security utilities
│   │   ├── validation.py    # Custom validators
│   │   └── logging.py       # Logging configuration
│   └── static/              # Static files (NextJS build)
├── alembic/                 # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── tests/                   # Test files
│   ├── unit/
│   ├── integration/
│   ├── conftest.py
│   └── factories.py
├── scripts/                 # Utility scripts
│   ├── init_db.py
│   └── seed_data.py
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
└── .env.example            # Environment variables template
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Boards Table

```sql
CREATE TABLE boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT DEFAULT 'My Kanban Board',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

### Columns Table

```sql
CREATE TABLE columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards (id) ON DELETE CASCADE,
    UNIQUE(board_id, position)
);
```

### Cards Table

```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (column_id) REFERENCES columns (id) ON DELETE CASCADE,
    UNIQUE(column_id, position)
);
```

### Conversations Table

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    board_snapshot JSON,  # Kanban state at time of conversation
    ai_updates JSON,      # AI-generated updates (if any)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

## API Endpoints

### Authentication

- `POST /api/auth/login` - Login with credentials
- `POST /api/auth/logout` - Logout (invalidate token)
- `POST /api/auth/refresh` - Refresh JWT token

### Boards

- `GET /api/boards` - Get user's board
- `PUT /api/boards` - Update board title
- `GET /api/boards/{board_id}` - Get specific board

### Columns

- `POST /api/columns` - Create new column
- `PUT /api/columns/{column_id}` - Update column (rename)
- `DELETE /api/columns/{column_id}` - Delete column
- `PUT /api/columns/{column_id}/reorder` - Update column position

### Cards

- `POST /api/cards` - Create new card
- `GET /api/cards/{card_id}` - Get card details
- `PUT /api/cards/{card_id}` - Update card
- `DELETE /api/cards/{card_id}` - Delete card
- `PUT /api/cards/{card_id}/move` - Move card to different column/position

### AI Chat

- `POST /api/ai/chat` - Send message to AI
- `GET /api/ai/conversations` - Get conversation history
- `DELETE /api/ai/conversations/{conversation_id}` - Delete conversation

### WebSocket

- `WS /ws` - WebSocket connection for real-time updates

## Authentication Flow

### JWT Implementation

1. **Login**: Validate credentials, return JWT with user ID
2. **Token Storage**: HTTP-only cookie for security
3. **Validation**: Middleware validates JWT on protected routes
4. **Refresh**: Short-lived access tokens with refresh capability
5. **Logout**: Clear cookie, add token to blacklist (if implemented)

### Hardcoded Credentials (MVP)

```python
HARDCODED_USER = {
    "username": "user",
    "hashed_password": "$2b$12$..."  # bcrypt hash of "password"
}
```

## AI Integration

### OpenRouter Client

- **Async HTTP client**: httpx for non-blocking API calls
- **Retry logic**: Exponential backoff for failed requests
- **Rate limiting**: Prevent excessive API usage
- **Cost tracking**: Monitor AI usage costs

### Structured Outputs

```python
class AIResponse(BaseModel):
    message: str  # Response to show user
    updates: Optional[KanbanUpdates]  # Optional board updates

class KanbanUpdates(BaseModel):
    actions: List[KanbanAction]

class KanbanAction(BaseModel):
    type: Literal["create", "update", "move", "delete"]
    target: Literal["card", "column"]
    data: Dict[str, Any]
```

### Prompt Engineering

```python
SYSTEM_PROMPT = """
You are a helpful project management assistant. You can help users manage their Kanban boards.
You receive the current board state as JSON and can suggest updates.

Respond with:
1. A helpful message to the user
2. Optional: Specific updates to make to the Kanban board

Format your response as valid JSON matching the AIResponse schema.
"""
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server error

### Custom Exceptions

```python
class AppException(Exception):
    """Base application exception"""

class NotFoundException(AppException):
    """Resource not found"""

class ValidationException(AppException):
    """Request validation failed"""

class AuthenticationException(AppException):
    """Authentication failed"""
```

## Logging

### Structured Logging with structlog

- **JSON format**: For production logging
- **Context**: Request ID, user ID, endpoint
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Correlation**: Track requests across services

### Log Categories

- **Access logs**: HTTP requests/responses
- **Application logs**: Business logic events
- **Error logs**: Exceptions and failures
- **Performance logs**: Slow operations

## Testing Strategy

### Unit Tests

- **Services**: Business logic testing
- **Models**: Database operations
- **Utils**: Utility functions

### Integration Tests

- **API endpoints**: HTTP request/response
- **Database**: Real database operations
- **Authentication**: Login/logout flows

### E2E Tests

- **Full workflows**: User registration to board management
- **AI integration**: Chat to board updates
- **WebSocket**: Real-time updates

### Test Coverage

- **Target**: 80% code coverage
- **Critical paths**: 100% coverage
- **Integration**: All API endpoints

## Performance Considerations

### Database Optimization

- **Indexes**: Proper indexing on foreign keys and search fields
- **Connection pooling**: SQLAlchemy connection management
- **Query optimization**: N+1 query prevention

### Caching Strategy

- **Redis**: For frequently accessed data
- **Response caching**: Cache API responses where appropriate
- **Invalidation**: Clear cache on data updates

### Async Operations

- **FastAPI async**: Non-blocking request handling
- **Background tasks**: For non-critical operations
- **WebSocket**: Real-time communication

## Security Measures

### Input Validation

- **Pydantic schemas**: Request/response validation
- **SQL injection**: SQLAlchemy parameterized queries
- **XSS prevention**: Output encoding

### Authentication Security

- **JWT best practices**: Short-lived tokens, secure storage
- **Password hashing**: bcrypt with appropriate work factor
- **Rate limiting**: Prevent brute force attacks

### API Security

- **CORS**: Configured for frontend origin only
- **HTTPS**: Required in production
- **Headers**: Security headers (HSTS, CSP)

## Deployment

### Docker Configuration

```dockerfile
# Multi-stage build for Python + NodeJS
FROM python:3.11-slim as python-base
# ... Python dependencies and build

FROM node:18-alpine as node-base
# ... NodeJS dependencies and NextJS build

FROM python:3.11-slim as production
# Combine Python backend with static frontend
```

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./kanban.db

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Integration
OPENROUTER_API_KEY=your-api-key
OPENROUTER_MODEL=openai/gpt-oss-120b

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Health Checks

- **/health**: Application health endpoint
- **/ready**: Readiness check (database, AI service)
- **/metrics**: Prometheus metrics endpoint

## Monitoring & Observability

### Metrics

- **Request rate**: API calls per second
- **Error rate**: Failed requests percentage
- **Latency**: Response time percentiles
- **AI usage**: Token count, cost tracking

### Alerting

- **Error spikes**: Sudden increase in errors
- **High latency**: Slow response times
- **Service down**: Health check failures

### Tracing

- **Request tracing**: End-to-end request tracking
- **Performance profiling**: Identify bottlenecks
- **Dependency tracking**: External service calls
