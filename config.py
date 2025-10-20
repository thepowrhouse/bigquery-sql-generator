import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Google Cloud Project Configuration
    PROJECT_ID = os.getenv("PROJECT_ID")
    DATASET_ID = os.getenv("DATASET_ID")
    
    # AI Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0))
    
    # API Keys (from environment variables)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Cache Configuration
    SCHEMA_CACHE_TTL = int(os.getenv("SCHEMA_CACHE_TTL", 3600))  # 1 hour in seconds
    
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")  # Options: "google", "openai", etc.