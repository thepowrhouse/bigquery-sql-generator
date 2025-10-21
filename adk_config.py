import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class ADKConfig:
    def __init__(self):
        # Google Cloud Configuration
        self.project_id = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        
        # Validate required configuration
        self.validate()

    def validate(self):
        """Validate that all required configuration is present."""
        if not self.project_id:
            raise ValueError("PROJECT_ID environment variable is required")
        return True


# Create a global config instance
config = ADKConfig()