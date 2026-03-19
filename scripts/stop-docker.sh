#!/bin/bash
# Stop Kanban application Docker containers

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

# Check if Docker Compose is installed
get_docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null; then
        echo "docker compose"
    else
        print_error "Docker Compose is not available"
        exit 1
    fi
}

# Stop Docker containers
stop_containers() {
    local docker_compose_cmd=$(get_docker_compose_cmd)
    
    print_message "Stopping Docker containers..."
    
    # Stop containers
    $docker_compose_cmd down
    
    print_success "Docker containers stopped"
}

# Remove volumes (optional)
remove_volumes() {
    local docker_compose_cmd=$(get_docker_compose_cmd)
    
    read -p "Remove all volumes? This will delete all data. (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "Removing volumes..."
        $docker_compose_cmd down -v
        print_success "Volumes removed"
    else
        print_message "Volumes preserved"
    fi
}

# Remove images (optional)
remove_images() {
    local docker_compose_cmd=$(get_docker_compose_cmd)
    
    read -p "Remove Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "Removing images..."
        $docker_compose_cmd down --rmi all
        print_success "Images removed"
    else
        print_message "Images preserved"
    fi
}

# Clean up Docker resources
cleanup_docker() {
    print_message "Cleaning up Docker resources..."
    
    # Remove dangling images
    local dangling_images=$(docker images -f "dangling=true" -q 2>/dev/null || true)
    if [ -n "$dangling_images" ]; then
        print_message "Removing dangling images..."
        docker rmi $dangling_images 2>/dev/null || true
    fi
    
    # Remove unused volumes
    local unused_volumes=$(docker volume ls -q -f "dangling=true" 2>/dev/null || true)
    if [ -n "$unused_volumes" ]; then
        print_message "Removing unused volumes..."
        docker volume rm $unused_volumes 2>/dev/null || true
    fi
    
    # Remove unused networks
    local unused_networks=$(docker network ls -q -f "dangling=true" 2>/dev/null || true)
    if [ -n "$unused_networks" ]; then
        print_message "Removing unused networks..."
        docker network rm $unused_networks 2>/dev/null || true
    fi
    
    print_success "Docker resources cleaned up"
}

# Check if containers are running
check_containers_running() {
    local docker_compose_cmd=$(get_docker_compose_cmd)
    
    local running_containers=$($docker_compose_cmd ps -q 2>/dev/null || true)
    
    if [ -n "$running_containers" ]; then
        return 0  # Containers are running
    else
        return 1  # No containers running
    fi
}

# Display stopped information
show_stopped_info() {
    echo ""
    echo "========================================="
    echo "     Kanban Application Stopped"
    echo "========================================="
    echo ""
    echo "All Docker containers have been stopped."
    echo ""
    echo "Ports freed:"
    echo "  Port 8000: Backend API"
    echo "  Port 3000: Frontend"
    echo "  Port 6379: Redis"
    echo ""
    echo "Data:"
    echo "  Database data is preserved in Docker volumes"
    echo "  To remove data, run with --clean option"
    echo ""
    echo "To start again, run: ./scripts/start-docker.sh"
    echo "========================================="
    echo ""
}

# Main execution
main() {
    local clean_mode=false
    local remove_all=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                clean_mode=true
                shift
                ;;
            --remove-all)
                remove_all=true
                shift
                ;;
            --help)
                print_message "Usage: ./scripts/stop-docker.sh [--clean] [--remove-all]"
                print_message "  --clean       Clean up Docker resources"
                print_message "  --remove-all  Remove containers, volumes, and images"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    print_message "Stopping Kanban Docker containers..."
    
    # Check if containers are running
    if ! check_containers_running; then
        print_warning "No Docker containers are currently running"
    fi
    
    # Stop containers
    stop_containers
    
    # Handle cleanup options
    if [ "$clean_mode" = true ]; then
        cleanup_docker
    fi
    
    if [ "$remove_all" = true ]; then
        remove_volumes
        remove_images
    fi
    
    # Show information
    show_stopped_info
}

# Run main function
main "$@"