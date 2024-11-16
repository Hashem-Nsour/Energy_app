from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from fastapi import Depends
import logging

# Logging configuration for debugging database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your actual database URL
DATABASE_URL = "sqlite:///./test.db"
# Example: For PostgreSQL: "postgresql://user:password@localhost/dbname"

# Configure SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},  # SQLite-specific settings
    echo=True,  # Enable SQLAlchemy query logging
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a Base class for models
Base = declarative_base()

# Dependency to provide a session for database operations
def get_db() -> Session:
    """
    Dependency that provides a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the database (for migrations or creating tables in SQLite)
def initialize_database():
    """
    Initialize the database by creating all tables defined in models.
    """
    logger.info("Initializing database...")
    import app.models  # Import models to register them with SQLAlchemy
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")

# Context manager for manual session management
@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of database operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error occurred during transaction: {e}")
        raise
    finally:
        session.close()

# Event listener to log connection errors
@event.listens_for(engine, "connect")
def connect_listener(dbapi_connection, connection_record):
    logger.info("Database connection established.")

@event.listens_for(engine, "close")
def close_listener(dbapi_connection, connection_record):
    logger.info("Database connection closed.")

# Example test function for ensuring DB connection works
def test_database_connection():
    """
    Test the database connection by executing a simple query.
    """
    logger.info("Testing database connection...")
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        assert result.scalar() == 1
    logger.info("Database connection test passed successfully.")
