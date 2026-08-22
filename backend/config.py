import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY        = os.getenv("GROQ_API_KEY", "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_STORE_PATH   = os.path.join(BASE_DIR, "vector_store")
CONTENT_PATH        = os.path.join(BASE_DIR, "content")

EMBEDDING_MODEL      = "all-MiniLM-L6-v2"
CONFIDENCE_THRESHOLD = 0.52
TOP_K                = 5

GROQ_MODEL = "openai/gpt-oss-120b"