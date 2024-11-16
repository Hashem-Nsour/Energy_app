# app/__init__.py

from .database import SessionLocal, engine
from .models import Base
from .config import settings

# Optional: Initialize the database connection at the package level if needed
Base.metadata.create_all(bind=engine)

# You can also add common utilities or imports that you want accessible at the package level
