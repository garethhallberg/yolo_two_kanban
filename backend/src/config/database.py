"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    echo=settings.debug,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database using Alembic migrations.
    """
    import subprocess
    import sys
    import os
    
    try:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.join(current_dir, "..", "..")
        
        # Run Alembic upgrade to apply all migrations
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Database initialized successfully with Alembic migrations")
            print(result.stdout)
        else:
            print("Error initializing database with Alembic:")
            print(result.stderr)
            # Fallback to create_all if Alembic fails
            from src.models import Base  # Import all models
            Base.metadata.create_all(bind=engine)
            print("Fallback: Database initialized with create_all()")
    except Exception as e:
        print(f"Error running Alembic: {e}")
        # Fallback to create_all if Alembic fails
        from src.models import Base  # Import all models
        Base.metadata.create_all(bind=engine)
        print("Fallback: Database initialized with create_all()")