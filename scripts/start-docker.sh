#!/bin/bash
# Start Kanban application using Docker Compose

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

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_message "Please install Docker and try again."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        print_message "Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        # Check for Docker Compose plugin
        if ! docker compose version &> /dev/null; then
            print_error "Docker Compose is not installed"
            print_message "Please install Docker Compose and try again."
            exit 1
        fi
        DOCKER_COMPOSE_CMD="docker compose"
    else
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
    
    print_success "Docker Compose is available"
}

# Check if ports are available
check_ports() {
    local ports=("8000" "3000" "6379")
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -ti:$port > /dev/null 2>&1; then
            occupied_ports+=("$port")
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        print_warning "The following ports are already in use: ${occupied_ports[*]}"
        print_message "You may need to stop existing services or use different ports."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message "Aborting..."
            exit 1
        fi
    fi
}

# Load environment variables
load_env() {
    if [ -f .env ]; then
        print_message "Loading environment variables from .env file"
        # Export all variables from .env file
        set -a
        source .env
        set +a
    else
        print_warning ".env file not found, using default values"
    fi
    
    # Check for required environment variables
    if [ -z "$OPENROUTER_API_KEY" ]; then
        print_warning "OPENROUTER_API_KEY is not set. AI features will not work."
        print_message "You can set it in the .env file"
    fi
}

# Build and start Docker containers
start_containers() {
    print_message "Building and starting Docker containers..."
    
    # Build images
    print_message "Building Docker images..."
    $DOCKER_COMPOSE_CMD build
    
    # Start containers
    print_message "Starting containers..."
    $DOCKER_COMPOSE_CMD up -d
    
    # Wait for services to be healthy
    wait_for_services
}

# Wait for services to be ready
wait_for_services() {
    print_message "Waiting for services to be ready..."
    
    # Wait for backend
    local max_attempts=60
    local attempt=1
    
    print_message "Waiting for backend API..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            print_success "Backend API is ready"
            break
        fi
        print_message "  Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Backend API failed to start"
        show_logs
        exit 1
    fi
    
    # Wait for frontend
    attempt=1
    print_message "Waiting for frontend..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        print_message "  Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_warning "Frontend is taking longer than expected to start"
    fi
}

# Show container logs
show_logs() {
    print_message "Showing container logs (Ctrl+C to exit)..."
    $DOCKER_COMPOSE_CMD logs -f
}

# Display startup information
show_info() {
    echo ""
    echo "========================================="
    echo "     Kanban Application Started"
    echo "========================================="
    echo ""
    echo "Services:"
    echo "  Backend API:  http://localhost:8000"
    echo "  Frontend:     http://localhost:3000"
    echo "  Redis:        localhost:6379"
    echo ""
    echo "API Endpoints:"
    echo "  Health:       http://localhost:8000/api/health"
    echo "  Docs:         http://localhost:8000/api/docs"
    echo "  Hello:        http://localhost:8000/api/hello"
    echo ""
    echo "Container Status:"
    $DOCKER_COMPOSE_CMD ps
    echo ""
    echo "Commands:"
    echo "  View logs:    ./scripts/start-docker.sh --logs"
    echo "  Stop:         ./scripts/stop-docker.sh"
    echo "  Restart:      ./scripts/stop-docker.sh && ./scripts/start-docker.sh"
    echo ""
    echo "To view logs, run: $DOCKER_COMPOSE_CMD logs -f"
    echo "========================================="
    echo ""
}

# Main execution
main() {
    local show_logs_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --logs)
                show_logs_only=true
                shift
                ;;
            --help)
                print_message "Usage: ./scripts/start-docker.sh [--logs]"
                print_message "  --logs    Show logs after starting"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    print_message "Starting Kanban application with Docker..."
    
    # Check requirements
    check_docker
    check_docker_compose
    
    # Load environment
    load_env
    
    # Check ports
    check_ports
    
    # Start containers
    start_containers
    
    # Show information
    show_info
    
    # Show logs if requested
    if [ "$show_logs_only" = true ]; then
        show_logs
    fi
}

# Run main function
main "$@"