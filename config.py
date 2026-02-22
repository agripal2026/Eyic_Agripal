"""
AgriPal - Configuration File
(No Gemini | KisanAI Chatbot + RAG enabled)
"""

import os
from pathlib import Path

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

BASE_DIR       = Path(__file__).parent
DATA_DIR       = BASE_DIR / "data" / "agricultural_docs"
CHUNKS_DIR     = BASE_DIR / "chunks" / "processed"
VECTOR_DB_PATH = str(BASE_DIR / "chroma_db")   # must match app.py _AgriConfig

DATA_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# FLASK / SERVER
# ============================================================================

PORT  = int(os.environ.get('PORT', 5000))
HOST  = os.environ.get('HOST', '0.0.0.0')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ============================================================================
# MYSQL CONFIGURATION
# ============================================================================

MYSQL_CONFIG = {
    'host':     os.environ.get('MYSQL_HOST',     'localhost'),
    'user':     os.environ.get('MYSQL_USER',     'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'pavan'),
    'database': os.environ.get('MYSQL_DATABASE', 'agripal_llm'),
    'port':     int(os.environ.get('MYSQL_PORT', 3306)),
}

# ============================================================================
# VECTOR DB / EMBEDDING  (KisanAI RAG chatbot)
# ============================================================================

EMBEDDING_MODEL      = "all-MiniLM-L6-v2"
CHUNK_SIZE           = 800
CHUNK_OVERLAP        = 100
MIN_CHUNK_SIZE       = 200
TOP_K_DOCUMENTS      = 5
SIMILARITY_THRESHOLD = 0.3
MAX_CONTEXT_TOKENS   = 8000

# ============================================================================
# AGRICULTURAL DOMAIN
# ============================================================================

SUPPORTED_CROPS = [
    # Cereals & grains
    'Rice', 'Wheat', 'Maize', 'Corn', 'Barley', 'Jowar', 'Bajra', 'Ragi',
    # Cash crops
    'Cotton', 'Sugarcane', 'Tobacco', 'Jute',
    # Vegetables
    'Tomato', 'Potato', 'Onion', 'Chilli', 'Brinjal',
    # Fruits
    'Mango', 'Banana', 'Coconut',
    # Plantation
    'Tea', 'Coffee', 'Rubber',
    # Oilseeds & pulses
    'Groundnut', 'Soybean', 'Sunflower', 'Mustard',
    'Chickpea', 'Lentil', 'Pigeon Pea', 'Green Gram',
    # Spices
    'Turmeric', 'Ginger',
    # Broad categories (used by KisanAI query classifier)
    'Pulses', 'Vegetables', 'Fruits', 'Spices', 'Oilseeds',
]

# Alias used by app.py _AgriConfig
CROP_CATEGORIES = SUPPORTED_CROPS

INDIAN_STATES = [
    'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala', 'Gujarat',
    'Rajasthan', 'Punjab', 'Haryana', 'Uttar Pradesh', 'Bihar',
    'West Bengal', 'Madhya Pradesh', 'Andhra Pradesh', 'Telangana',
    'Odisha', 'Chhattisgarh', 'Jharkhand', 'Assam', 'Himachal Pradesh',
    'Uttarakhand', 'Goa', 'Delhi',
]

# Alias used by app.py _AgriConfig
STATES = INDIAN_STATES

SEASONS = ['Kharif', 'Rabi', 'Zaid', 'Zayad', 'Summer', 'Winter', 'Monsoon', 'Perennial', 'Annual']

# Intent keywords — used by KisanAI chatbot query classifier
INTENT_KEYWORDS = {
    'scheme':       ['scheme', 'subsidy', 'yojana', 'benefit', 'government', 'pm-kisan', 'pmfby'],
    'market_price': ['price', 'mandi', 'market', 'rate', 'sell', 'buy', 'cost'],
    'disease':      ['disease', 'pest', 'infection', 'treatment', 'cure', 'control', 'fungus'],
    'crop_guide':   ['cultivation', 'farming', 'planting', 'sowing', 'harvest', 'grow'],
    'fertilizer':   ['fertilizer', 'nutrient', 'soil', 'compost', 'npk', 'organic'],
    'weather':      ['weather', 'rainfall', 'temperature', 'climate', 'forecast'],
}

# Chatbot behaviour
MAX_CONVERSATION_HISTORY  = 10
ENABLE_CHAT_HISTORY_DB    = True
ENABLE_FALLBACK_RESPONSES = True

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL       = "INFO"
LOG_FORMAT      = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
VERBOSE_LOGGING = True

# ============================================================================
# VALIDATION HELPER
# ============================================================================

def validate_config():
    errors   = []
    warnings = []

    print("\n" + "=" * 65)
    print("🔍 AGRIPAL CONFIGURATION VALIDATION")
    print("=" * 65)

    print(f"\n📁 Directories:")
    print(f"   Base:     {BASE_DIR}")
    print(f"   Data:     {DATA_DIR}   {'✅' if DATA_DIR.exists() else '⚠️ (will be created)'}")
    print(f"   Chunks:   {CHUNKS_DIR} {'✅' if CHUNKS_DIR.exists() else '⚠️ (will be created)'}")
    print(f"   VectorDB: {VECTOR_DB_PATH}")

    print(f"\n🗄️  MySQL:")
    print(f"   Host:     {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
    print(f"   User:     {MYSQL_CONFIG['user']}")
    print(f"   Database: {MYSQL_CONFIG['database']}")
    if MYSQL_CONFIG['password'] in ('pavan', 'password', ''):
        warnings.append("Weak/default MySQL password — change before production deploy")
        print("   Password: ⚠️  DEFAULT")
    else:
        print("   Password: ✅ Custom")

    print(f"\n🤖 KisanAI Chatbot / RAG:")
    print(f"   Embedding Model: {EMBEDDING_MODEL}")
    print(f"   Chunk Size:      {CHUNK_SIZE}")
    print(f"   Chunk Overlap:   {CHUNK_OVERLAP}")
    print(f"   Top-K Docs:      {TOP_K_DOCUMENTS}")

    print(f"\n🌾 Domain:")
    print(f"   Crops:   {len(SUPPORTED_CROPS)}")
    print(f"   States:  {len(INDIAN_STATES)}")
    print(f"   Seasons: {len(SEASONS)}")

    if warnings:
        print(f"\n⚠️  Warnings:")
        for w in warnings:
            print(f"   - {w}")
    if errors:
        print(f"\n❌ Errors:")
        for e in errors:
            print(f"   - {e}")
        print("=" * 65)
        return False

    print("\n✅ Configuration OK!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    validate_config()