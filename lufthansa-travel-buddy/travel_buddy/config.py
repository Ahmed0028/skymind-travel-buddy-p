"""
Configuration Management
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(name: str, default: str = None, required: bool = False) -> str:
    """Get environment variable with optional default."""
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Required environment variable {name} is not set")
    return value


# ============================================
# Vertex AI / Gemini Configuration
# ============================================
USE_VERTEX_AI = get_env_var("GOOGLE_GENAI_USE_VERTEXAI", "0") == "1"

# Only require API key if NOT using Vertex AI
if USE_VERTEX_AI:
    GOOGLE_API_KEY = None
    GOOGLE_CLOUD_PROJECT = get_env_var("GOOGLE_CLOUD_PROJECT", required=True)
    GOOGLE_CLOUD_LOCATION = get_env_var("GOOGLE_CLOUD_LOCATION", "europe-west3")
else:
    GOOGLE_API_KEY = get_env_var("GOOGLE_API_KEY", required=True)
    GOOGLE_CLOUD_PROJECT = get_env_var("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = get_env_var("GOOGLE_CLOUD_LOCATION", "europe-west3")

# ============================================
# Lufthansa API
# ============================================
LUFTHANSA_CLIENT_ID = get_env_var("LUFTHANSA_CLIENT_ID", required=True)
LUFTHANSA_CLIENT_SECRET = get_env_var("LUFTHANSA_CLIENT_SECRET", required=True)

# ============================================
# Model Configuration
# ============================================
ROOT_AGENT_MODEL = get_env_var("ROOT_AGENT_MODEL", "gemini-3.1-pro-preview")
SUB_AGENT_MODEL = get_env_var("SUB_AGENT_MODEL", "gemini-3.1-pro-preview")

# ============================================
# Lufthansa API URLs
# ============================================
LUFTHANSA_API_BASE_URL = "https://api.lufthansa.com/v1"
LUFTHANSA_AUTH_URL = "https://api.lufthansa.com/v1/oauth/token"

# ============================================
# Fallback Aviation API
# ============================================
AVIATIONSTACK_API_KEY = get_env_var("AVIATIONSTACK_API_KEY")
AVIATIONSTACK_BASE_URL = "https://api.aviationstack.com/v1"

# ============================================
# Supported Airlines
# ============================================
LUFTHANSA_GROUP_AIRLINES = ["LH", "LX", "OS", "SN", "EW"]
