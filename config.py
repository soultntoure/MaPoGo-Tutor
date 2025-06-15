# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SEMANTIC_CHUNKER_BREAKPOINT_THRESHOLD = 80