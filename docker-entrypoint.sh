#!/bin/bash
set -e

# Function to wait for database to be ready
wait_for_db() {
    if [ -n "$DATABASE_URL" ]; then
        echo "Waiting for database to be ready..."
        # For SQLite, just check if the directory exists
        if [[ "$DATABASE_URL" == sqlite* ]]; then
            db_path=$(echo "$DATABASE_URL" | sed 's/sqlite:\/\/\///')
            db_dir=$(dirname "$db_path")
            mkdir -p "$db_dir"
            echo "SQLite database directory created: $db_dir"
        fi
    fi
}

# Function to initialize database
init_database() {
    echo "Initializing database..."
    python -c "
from src.config.database import init_db
init_db()
print('Database initialized successfully')
"
}

# Function to run database migrations
run_migrations() {
    if command -v alembic &> /dev/null; then
        echo "Running database migrations..."
        alembic upgrade head
    else
        echo "Alembic not found, skipping migrations"
    fi
}

# Function to start the application
start_app() {
    echo "Starting Kanban Backend API..."
    exec "$@"
}

# Main execution
main() {
    wait_for_db
    
    # Initialize database if it doesn't exist
    if [ "$INIT_DB" = "true" ] || [ "$ENVIRONMENT" = "development" ]; then
        init_database
    fi
    
    # Run migrations in production
    if [ "$ENVIRONMENT" = "production" ]; then
        run_migrations
    fi
    
    # Start the application
    start_app "$@"
}

# Run main function with all arguments
main "$@"