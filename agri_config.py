import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "agriculture_docs"
CHUNKS_DIR = BASE_DIR / "chunks" / "processed"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# MySQL Configuration (using environment variables for Render)
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'pavan'),
    'database': os.getenv('MYSQL_DATABASE', 'agriculture_llm'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

# Vector DB Configuration
VECTOR_DB_PATH = str(BASE_DIR / "chroma_db")

# Chunking Configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MIN_CHUNK_SIZE = 200

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Agriculture-specific categories
CROP_CATEGORIES = [
    'Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton',
    'Pulses', 'Vegetables', 'Fruits', 'Spices', 'Oilseeds'
]

SEASONS = ['Kharif', 'Rabi', 'Zayad', 'Perennial']

STATES = [
    'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala', 
    'Gujarat', 'Rajasthan', 'Punjab', 'Haryana', 
    'Uttar Pradesh', 'Madhya Pradesh', 'Andhra Pradesh'
]

# API Configuration for Render
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
