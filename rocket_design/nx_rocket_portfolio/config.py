"""
Configuration settings for NX Rocket Portfolio
Contains environment-specific settings and API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.2'))
OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '2000'))

# Flag to enable/disable AI features
AI_FEATURES_ENABLED = True

# Demo mode (use simulated responses instead of actual API calls)
DEMO_MODE = True

# Application settings
DEBUG = bool(os.environ.get('DEBUG', 'True').lower() == 'true')
USE_CACHE = bool(os.environ.get('USE_CACHE', 'True').lower() == 'true')
CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '3600'))  # 1 hour

# Rocket engineering constraints file
ENGINEERING_CONSTRAINTS_FILE = os.environ.get(
    'ENGINEERING_CONSTRAINTS_FILE', 
    os.path.join(os.path.dirname(__file__), 'data', 'engineering_constraints.json')
)
