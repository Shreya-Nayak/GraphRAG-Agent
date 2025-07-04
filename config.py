import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

assert GEMINI_API_KEY, "Missing GEMINI_API_KEY environment variable!"
