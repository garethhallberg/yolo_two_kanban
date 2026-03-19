# Scripts Documentation

## Overview

This directory contains platform-specific scripts for starting, stopping, and managing the Project Management MVP application. Scripts support both Docker-based deployment and local development.

## Script Categories

### 1. Development Scripts

Scripts for local development without Docker.

### 2. Docker Scripts

Scripts for running the application in Docker containers.

### 3. Utility Scripts

Helper scripts for database management, testing, etc.

## Script Files

### For macOS/Linux (`*.sh` files)

#### `start-dev.sh` - Start local development

```bash
#!/bin/bash
# Start backend and frontend in development mode
```

#### `stop-dev.sh` - Stop local development

```bash
#!/bin/bash
# Stop all development processes
```

#### `start-docker.sh` - Start with Docker

```bash
#!/bin/bash
# Start application using docker-compose
```

#### `stop-docker.sh` - Stop Docker containers

```bash
#!/bin/bash
# Stop and remove Docker containers
```

#### `clean.sh` - Clean development environment

```bash
#!/bin/bash
# Remove node_modules, __pycache__, etc.
```

### For Windows (`*.ps1` files)

#### `start-dev.ps1` - Start local development

```powershell
# Start backend and frontend in development mode
```

#### `stop-dev.ps1` - Stop local development

```powershell
# Stop all development processes
```

#### `start-docker.ps1` - Start with Docker

```powershell
# Start application using docker-compose
```

#### `stop-docker.ps1` - Stop Docker containers

```powershell
# Stop and remove Docker containers
```

#### `clean.ps1` - Clean development environment

```powershell
# Remove node_modules, __pycache__, etc.
```

### Cross-platform Scripts

#### `init-db.sh` / `init-db.ps1`

Initialize the database with schema and seed data.

#### `run-tests.sh` / `run-tests.ps1`

Run all tests (backend, frontend, e2e).

#### `build-prod.sh` / `build-prod.ps1`

Build production Docker image.

#### `deploy-local.sh` / `deploy-local.ps1`

Deploy to local Docker environment.

## Script Implementation Details

### Development Scripts

#### Backend Development Server

- **Command**: `uv run fastapi dev src/main.py`
- **Port**: 8000
- **Hot reload**: Enabled
- **Environment**: Development (.env.development)

#### Frontend Development Server

- **Command**: `npm run dev` (in frontend directory)
- **Port**: 3000
- **Hot reload**: Enabled
- **Proxy**: To backend on port 8000

### Docker Scripts

#### Docker Compose Configuration

- **Services**:
  - `backend`: FastAPI application
  - `frontend`: NextJS build served by backend
  - `redis` (optional): For caching
- **Networks**: Internal network for service communication
- **Volumes**: Database persistence

#### Production Build

- **Multi-stage**: Python + NodeJS in single image
- **Optimization**: Minimized layers, alpine base
- **Security**: Non-root user, minimal permissions

## Usage Examples

### Local Development (macOS/Linux)

```bash
# Start development servers
./scripts/start-dev.sh

# Stop development servers
./scripts/stop-dev.sh

# Run tests
./scripts/run-tests.sh
```

### Docker Development (macOS/Linux)

```bash
# Start with Docker
./scripts/start-docker.sh

# View logs
docker-compose logs -f

# Stop Docker
./scripts/stop-docker.sh
```

### Windows PowerShell

```powershell
# Start development servers
.\scripts\start-dev.ps1

# Start with Docker
.\scripts\start-docker.ps1
```

## Environment Variables

Scripts use environment variables from:

- `.env` - Base environment
- `.env.development` - Development overrides
- `.env.production` - Production overrides

## Error Handling

### Graceful Shutdown

- Catch SIGINT/SIGTERM signals
- Clean up processes and resources
- Provide clear error messages

### Dependency Checks

- Verify Docker is installed and running
- Check for required ports availability
- Validate environment variables

### Logging

- Script execution logs
- Process output capture
- Error reporting to user

## Platform Compatibility

### macOS/Linux

- Bash shell scripts
- POSIX-compliant commands
- Systemd-style service management

### Windows

- PowerShell scripts
- Windows Service integration
- WSL2 compatibility considerations

### Cross-platform Considerations

- Path separators (`/` vs `\`)
- Line endings (LF vs CRLF)
- Command availability

## Security Considerations

### Script Permissions

- Executable flag set appropriately
- No sensitive data in scripts
- Input validation for script arguments

### Docker Security

- Non-root user in containers
- Read-only filesystem where possible
- Resource limits on containers

### Environment Security

- `.env` files excluded from version control
- Secrets management for production
- Secure credential handling

## Maintenance

### Script Updates

- Keep scripts synchronized across platforms
- Document changes in script headers
- Test on all target platforms

### Dependency Management

- Check for updated Docker images
- Verify compatibility with new versions
- Update package references

### Testing

- Test scripts in clean environments
- Verify cross-platform compatibility
- Validate error handling scenarios
