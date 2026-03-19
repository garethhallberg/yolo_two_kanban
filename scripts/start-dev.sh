#!/bin/bash
# Start local development servers for Kanban application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands are available
check_requirements() {
    local missing_commands=()
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        missing_commands+=("python3")
    fi
    
    # Check for Node.js
    if ! command -v node &> /dev/null; then
        missing_commands+=("node")
    fi
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        missing_commands+=("npm")
    fi
    
    if [ ${#missing_commands[@]} -gt 0 ]; then
        print_error "Missing required commands: ${missing_commands[*]}"
        print_message "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

# Start backend server
start_backend() {
    print_message "Starting backend server..."
    
    # Check if backend is already running
    if lsof -ti:8000 > /dev/null; then
        print_warning "Backend is already running on port 8000"
        return 0
    fi
    
    # Navigate to backend directory
    cd backend || {
        print_error "Backend directory not found"
        exit 1
    }
    
    # Install Python dependencies if needed
    if [ ! -d ".venv" ] && [ -f "pyproject.toml" ]; then
        print_message "Setting up Python virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install -e .
    else
        source .venv/bin/activate 2>/dev/null || true
    fi
    
    # Start backend server in background
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    # Wait for backend to start
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/api/health > /dev/null; then
            print_success "Backend server started successfully (PID: $BACKEND_PID)"
            echo $BACKEND_PID > /tmp/kanban-backend.pid
            return 0
        fi
        print_message "Waiting for backend to start... (attempt $attempt/$max_attempts)"
        sleep 1
        ((attempt++))
    done
    
    print_error "Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
}

# Start frontend server
start_frontend() {
    print_message "Starting frontend server..."
    
    # Check if frontend is already running
    if lsof -ti:3000 > /dev/null; then
        print_warning "Frontend is already running on port 3000"
        return 0
    fi
    
    # Navigate to frontend directory
    cd ../frontend || {
        print_error "Frontend directory not found"
        exit 1
    }
    
    # Install Node.js dependencies if needed
    if [ ! -d "node_modules" ] && [ -f "package.json" ]; then
        print_message "Installing Node.js dependencies..."
        npm install
    fi
    
    # Start frontend server in background
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:3000 > /dev/null; then
            print_success "Frontend server started successfully (PID: $FRONTEND_PID)"
            echo $FRONTEND_PID > /tmp/kanban-frontend.pid
            return 0
        fi
        print_message "Waiting for frontend to start... (attempt $attempt/$max_attempts)"
        sleep 1
        ((attempt++))
    done
    
    print_error "Frontend failed to start"
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
}

# Display startup information
show_info() {
    echo ""
    echo "========================================="
    echo "     Kanban Application Started"
    echo "========================================="
    echo ""
    echo "Backend API:"
    echo "  URL:      http://localhost:8000"
    echo "  Health:   http://localhost:8000/api/health"
    echo "  Docs:     http://localhost:8000/api/docs"
    echo ""
    echo "Frontend:"
    echo "  URL:      http://localhost:3000"
    echo ""
    echo "API Endpoints:"
    echo "  Hello:    http://localhost:8000/api/hello"
    echo "  Echo:     http://localhost:8000/api/hello/echo/{message}"
    echo ""
    echo "To stop the servers, run: ./scripts/stop-dev.sh"
    echo "========================================="
    echo ""
}

# Main execution
main() {
    print_message "Starting Kanban application in development mode..."
    
    # Check requirements
    check_requirements
    
    # Start servers
    start_backend
    cd ..
    start_frontend
    
    # Show information
    show_info
    
    # Keep script running
    print_message "Press Ctrl+C to stop all servers"
    
    # Trap Ctrl+C to clean up
    trap cleanup SIGINT
    
    # Wait for background processes
    wait
}

# Cleanup function
cleanup() {
    echo ""
    print_message "Shutting down servers..."
    
    # Kill backend if running
    if [ -f /tmp/kanban-backend.pid ]; then
        BACKEND_PID=$(cat /tmp/kanban-backend.pid)
        kill $BACKEND_PID 2>/dev/null && print_message "Backend server stopped" || true
        rm -f /tmp/kanban-backend.pid
    fi
    
    # Kill frontend if running
    if [ -f /tmp/kanban-frontend.pid ]; then
        FRONTEND_PID=$(cat /tmp/kanban-frontend.pid)
        kill $FRONTEND_PID 2>/dev/null && print_message "Frontend server stopped" || true
        rm -f /tmp/kanban-frontend.pid
    fi
    
    print_success "All servers stopped"
    exit 0
}

# Run main function
main "$@"