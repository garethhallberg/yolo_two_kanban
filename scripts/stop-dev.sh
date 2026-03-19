#!/bin/bash
# Stop local development servers for Kanban application

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
    echo -e "${YELLOW}[WARNING]${NC} $1
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Stop process by PID file
stop_process() {
    local process_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_message "Stopping $process_name (PID: $pid)..."
            kill "$pid" 2>/dev/null
            # Wait for process to terminate
            local max_wait=10
            local wait_count=0
            while kill -0 "$pid" 2>/dev/null && [ $wait_count -lt $max_wait ]; do
                sleep 1
                ((wait_count++))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "$process_name did not stop gracefully, forcing..."
                kill -9 "$pid" 2>/dev/null
            fi
            
            rm -f "$pid_file"
            print_success "$process_name stopped"
        else
            print_warning "$process_name PID file exists but process is not running"
            rm -f "$pid_file"
        fi
    else
        print_message "$process_name is not running (PID file not found)"
    fi
}

# Stop process by port
stop_process_by_port() {
    local port=$1
    local process_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_message "Stopping $process_name on port $port..."
        for pid in $pids; do
            kill "$pid" 2>/dev/null && print_message "  Stopped process $pid" || true
        done
        
        # Wait for processes to terminate
        local max_wait=5
        local wait_count=0
        while [ -n "$(lsof -ti:$port 2>/dev/null || true)" ] && [ $wait_count -lt $max_wait ]; do
            sleep 1
            ((wait_count++))
        done
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            print_warning "Forcing stop of remaining processes on port $port..."
            for pid in $remaining_pids; do
                kill -9 "$pid" 2>/dev/null && print_message "  Force stopped process $pid" || true
            done
        fi
        
        print_success "$process_name stopped"
    else
        print_message "$process_name is not running on port $port"
    fi
}

# Clean up temporary files
cleanup_temp_files() {
    print_message "Cleaning up temporary files..."
    
    # Remove PID files
    rm -f /tmp/kanban-backend.pid
    rm -f /tmp/kanban-frontend.pid
    
    # Remove Python cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type f -name "*.pyd" -delete 2>/dev/null || true
    
    # Remove Node.js cache files
    find . -type d -name "node_modules" -prune -o -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Temporary files cleaned up"
}

# Display stopped information
show_stopped_info() {
    echo ""
    echo "========================================="
    echo "     Kanban Application Stopped"
    echo "========================================="
    echo ""
    echo "All development servers have been stopped."
    echo ""
    echo "Ports freed:"
    echo "  Port 8000: Backend API"
    echo "  Port 3000: Frontend"
    echo ""
    echo "To start again, run: ./scripts/start-dev.sh"
    echo "========================================="
    echo ""
}

# Main execution
main() {
    print_message "Stopping Kanban development servers..."
    
    # Stop processes by PID files first (more precise)
    stop_process "Backend server" "/tmp/kanban-backend.pid"
    stop_process "Frontend server" "/tmp/kanban-frontend.pid"
    
    # Also stop by ports (in case PID files are missing)
    stop_process_by_port 8000 "Backend server"
    stop_process_by_port 3000 "Frontend server"
    
    # Clean up
    cleanup_temp_files
    
    # Show information
    show_stopped_info
}

# Run main function
main "$@"