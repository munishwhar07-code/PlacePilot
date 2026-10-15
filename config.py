import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration loaded from environment variables."""
    SECRET_KEY = os.getenv("SECRET_KEY", "placepilot-secure-dev-secret-key-2026")
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "placepilot")
    
    # Neo4j Graph Database Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    # Default Administrator Account Seed
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@placepilot.edu")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@PlacePilot2026")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "System Administrator")
