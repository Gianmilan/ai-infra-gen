import os
from pathlib import Path


class Config:
    """Application configuration"""

    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))

    # AI Provider settings
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama')  # 'anthropic' or 'ollama'
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL')
    OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', 600))  # Timeout in seconds

    # Caching
    ENABLE_CACHE = os.environ.get('ENABLE_CACHE', 'True') == 'True'
    CACHE_DIR = Path('data')
    CACHE_FILE = CACHE_DIR / 'cache.json'

    # Statistics
    STATS_FILE = CACHE_DIR / 'stats.json'

    # Validation
    ENABLE_VALIDATION = os.environ.get('ENABLE_VALIDATION', 'True') == 'True'

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if cls.AI_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set")

        # Create data directory if it doesn't exist
        cls.CACHE_DIR.mkdir(exist_ok=True)