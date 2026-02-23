from flask import Flask, request, render_template, jsonify, url_for, redirect, flash
from flask_cors import CORS
from PIL import Image
import numpy as np
import os
import io
import uuid
import json
import logging

import cv2
import shutil
import traceback
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote_plus
from datetime import datetime
import random
from segment2 import segment_analyze_plant

# ===== KISANAI CHATBOT IMPORTS =====
import time as _time
import re as _re
try:
    import mysql.connector as _mysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import chromadb as _chromadb
    from chromadb.config import Settings as _ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer as _SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# ✅ POST-HARVEST BLUEPRINT IMPORTS
from routes.post_harvest import post_harvest_bp
from routes.schemes import schemes_bp
import signal
import sys
import socket
from datetime import datetime, timedelta
from flask import session

# ✅ LOGIN & DATABASE IMPORTS
from flask_login import LoginManager, login_required, current_user, logout_user
from model import db, User, LoginHistory, DiseaseDetection, WeeklyAssessment
from routes.auth import auth_bp

from nutrition_analyzer import (
    analyze_nutrition_deficiency,
    calculate_fertilizer_dosage,
    load_nutrition_deficiency_data
)
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

nutrition_deficiency_data = load_nutrition_deficiency_data()
logger.info(f"Loaded {len(nutrition_deficiency_data)} nutrition deficiency types")

SERVER_START_TIME = datetime.now()


def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ===== SESSION & DATABASE CONFIGURATION =====
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SESSION_COOKIE_NAME'] = 'agripal_session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
_sk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.secret_key')
if os.path.exists(_sk_path):
    with open(_sk_path, 'rb') as _f:
        app.config['SECRET_KEY'] = _f.read()
else:
    _sk = os.urandom(32)
    with open(_sk_path, 'wb') as _f:
        _f.write(_sk)
    app.config['SECRET_KEY'] = _sk

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agripal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SERVER_START_TIME'] = SERVER_START_TIME.isoformat()

# ===== OTHER CONFIGURATIONS =====
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['DEBUG'] = True

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logger.info(f"Upload folder configured at: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")

# ===== INITIALIZE EXTENSIONS =====
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def preprocess_image(image):
    try:
        image = image.resize((128, 128))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise


# ===== MODEL: DISABLED FOR RENDER CLOUD DEPLOYMENT =====
# TensorFlow removed to stay within Render free-tier memory limits (512 MB).
# The model variable is set to None so all model-dependent code gracefully
# falls through to the cloud-mode placeholder response in /predict.
model = None
logger.warning("⚠️  TensorFlow disabled — running in Cloud/Maintenance mode.")


def load_disease_treatments():
    try:
        treatment_path = 'disease_treatments.json'
        if os.path.exists(treatment_path):
            with open(treatment_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Successfully loaded disease treatments from {treatment_path}")
                return data
        else:
            logger.error(f"Disease treatments file not found at: {os.path.abspath(treatment_path)}")
            return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading disease treatments: {e}")
        return {}


class_names = [
    "Apple_Apple_scab", "Apple_Black_rot", "Apple_Cedar_apple_rust", "Apple_healthy",
    "Blueberry_healthy", "Cherry_(including_sour)Powdery_mildew", "Cherry(including_sour)_healthy",
    "Corn_(maize)Cercospora_leaf_spot_Gray_leaf_spot", "Corn(maize)_Common_rust",
    "Corn_(maize)Northern_Leaf_Blight", "Corn(maize)_healthy", "Grape_Black_rot",
    "Grape_Esca_(Black_Measles)", "Grape_Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape_healthy",
    "Orange_Haunglongbing_(Citrus_greening)", "Peach_Bacterial_spot", "Peach_healthy",
    "Pepper_bell_Bacterial_spot", "Pepper_bell_healthy", "Potato_Early_blight",
    "Potato_Late_blight", "Potato_healthy", "Raspberry_healthy", "Soybean_healthy",
    "Squash_Powdery_mildew", "Strawberry_Leaf_scorch", "Strawberry_healthy",
    "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_Late_blight", "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot", "Tomato_Spider_mites_Two-spotted_spider_mite", "Tomato_Target_Spot",
    "Tomato_Tomato_Yellow_Leaf_Curl_Virus", "Tomato_Tomato_mosaic_virus", "Tomato_healthy"
]

CONFIDENCE_THRESHOLD = 50.0
SUPPORTED_PLANTS = {
    'Apple': ['Apple_Apple_scab', 'Apple_Black_rot', 'Apple_Cedar_apple_rust', 'Apple_healthy'],
    'Blueberry': ['Blueberry_healthy'],
    'Cherry': ['Cherry_(including_sour)Powdery_mildew', 'Cherry(including_sour)_healthy'],
    'Corn (Maize)': ['Corn_(maize)Cercospora_leaf_spot_Gray_leaf_spot', 'Corn(maize)_Common_rust',
                     'Corn_(maize)Northern_Leaf_Blight', 'Corn(maize)_healthy'],
    'Grape': ['Grape_Black_rot', 'Grape_Esca_(Black_Measles)', 'Grape_Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape_healthy'],
    'Orange': ['Orange_Haunglongbing_(Citrus_greening)'],
    'Peach': ['Peach_Bacterial_spot', 'Peach_healthy'],
    'Pepper (Bell)': ['Pepper_bell_Bacterial_spot', 'Pepper_bell_healthy'],
    'Potato': ['Potato_Early_blight', 'Potato_Late_blight', 'Potato_healthy'],
    'Raspberry': ['Raspberry_healthy'],
    'Soybean': ['Soybean_healthy'],
    'Squash': ['Squash_Powdery_mildew'],
    'Strawberry': ['Strawberry_Leaf_scorch', 'Strawberry_healthy'],
    'Tomato': ['Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_Leaf_Mold',
               'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites_Two-spotted_spider_mite', 'Tomato_Target_Spot',
               'Tomato_Tomato_Yellow_Leaf_Curl_Virus', 'Tomato_Tomato_mosaic_virus', 'Tomato_healthy']
}

COMMON_QUESTIONS = {
    "plant_diseases": [
        "What are the most common tomato diseases?",
        "How do I identify powdery mildew?",
        "What causes yellow leaves on plants?",
        "How to prevent fungal diseases in plants?",
        "What are the signs of bacterial infection in crops?",
        "How to identify viral diseases in plants?",
        "What causes leaf spots on vegetables?",
        "How to detect early blight in tomatoes?"
    ],
    "treatment_methods": [
        "What are organic pest control methods?",
        "How to make homemade fungicide?",
        "What is integrated pest management?",
        "How to use neem oil for plant diseases?",
        "What are the best copper-based fungicides?",
        "How to apply systemic pesticides safely?",
        "What is the difference between preventive and curative treatments?",
        "How to rotate pesticides to prevent resistance?"
    ],
    "crop_management": [
        "When is the best time to plant tomatoes?",
        "How much water do vegetables need daily?",
        "What is crop rotation and why is it important?",
        "How to improve soil fertility naturally?",
        "What are companion plants for tomatoes?",
        "How to prepare soil for planting?",
        "What are the signs of nutrient deficiency?",
        "How to manage weeds organically?"
    ],
    "seasonal_advice": [
        "What crops to plant in monsoon season?",
        "How to protect plants from extreme heat?",
        "What are winter crop management tips?",
        "How to prepare garden for rainy season?",
        "What vegetables grow best in summer?",
        "How to manage greenhouse in different seasons?",
        "What are post-harvest handling best practices?",
        "How to store seeds for next season?"
    ],
    "technology_agriculture": [
        "How can AI help in agriculture?",
        "What are smart farming techniques?",
        "How to use drones in agriculture?",
        "What are precision agriculture tools?",
        "How does satellite imagery help farmers?",
        "What are IoT applications in farming?",
        "How to use weather data for crop planning?",
        "What are digital farming platforms?"
    ]
}

disease_treatments = load_disease_treatments()
logger.info(f"Loaded {len(disease_treatments)} disease treatments")


def normalize_disease_info(disease_info):
    if not disease_info or 'pesticide' not in disease_info:
        return disease_info

    import copy
    normalized = copy.deepcopy(disease_info)

    logger.info("=" * 80)
    logger.info("📄 NORMALIZING DISEASE INFO FIELDS")
    logger.info("=" * 80)

    for treatment_type in ['chemical', 'organic']:
        if treatment_type not in normalized['pesticide']:
            logger.warning(f"⚠️ No {treatment_type} treatment found")
            continue

        treatment = normalized['pesticide'][treatment_type]
        logger.info(f"📦 Processing {treatment_type.upper()} treatment...")

        if 'application_frequency' in treatment and 'frequency' not in treatment:
            treatment['frequency'] = treatment['application_frequency']
            logger.info(f"  ✅ Mapped application_frequency -> frequency")
        elif 'frequency' not in treatment or not treatment.get('frequency'):
            treatment['frequency'] = "Apply according to product label recommendations and disease pressure."
            logger.warning(f"  ⚠️ No frequency field found, added fallback")

        if 'precautions' in treatment and 'safety' not in treatment:
            treatment['safety'] = treatment['precautions']
            logger.info(f"  ✅ Mapped precautions -> safety")
        elif 'safety' not in treatment or not treatment.get('safety'):
            if treatment_type == 'chemical':
                treatment['safety'] = "Wear protective equipment. Follow all label precautions. Keep away from water sources."
            else:
                treatment['safety'] = "Safe for beneficial insects when used as directed. Apply during cooler parts of day."
            logger.warning(f"  ⚠️ No safety field found, added fallback")

        if 'usage' not in treatment or not treatment.get('usage') or len(treatment.get('usage', '').strip()) < 10:
            treatment['usage'] = "Apply as directed on product label. Ensure thorough coverage of all affected plant surfaces. Repeat applications as needed based on disease pressure."
            logger.warning(f"  ⚠️ Missing or short usage, added fallback")

        required_fields = {
            'name': f"{treatment_type.title()} Treatment",
            'dosage_per_hectare': 0.0,
            'unit': 'L',
            'usage': 'Apply as directed',
            'frequency': 'As needed',
            'safety': 'Follow product label instructions'
        }

        for field, default_value in required_fields.items():
            if field not in treatment or not treatment.get(field):
                treatment[field] = default_value
                logger.warning(f"  ⚠️ Missing {field}, added default: {default_value}")

    logger.info("=" * 80)
    logger.info("✅ NORMALIZATION COMPLETE")
    logger.info("=" * 80)

    return normalized


def get_disease_info(disease_name):
    try:
        logger.info("=" * 80)
        logger.info(f"🔍 DISEASE LOOKUP: {disease_name}")
        logger.info("=" * 80)
        logger.info(f"📚 Database has {len(disease_treatments)} diseases")

        disease_info = disease_treatments.get(disease_name, None)

        if not disease_info:
            logger.info(f"⚠️ No exact match, trying variations...")
            cleaned_name = disease_name.replace('_', ' ').replace('(', '').replace(')', '').strip()

            for key, value in disease_treatments.items():
                if cleaned_name.lower() in key.lower() or key.lower() in cleaned_name.lower():
                    disease_info = value
                    logger.info(f"✅ Found match with key: {key}")
                    break

        if not disease_info:
            logger.error(f"❌ NO DISEASE INFO FOUND for: {disease_name}")
            available = list(disease_treatments.keys())[:5]
            logger.info(f"📝 Available diseases (first 5): {available}")
            return None

        logger.info(f"✅ Raw disease info found")
        logger.info(f"📋 Raw keys: {list(disease_info.keys())}")

        disease_info = normalize_disease_info(disease_info)

        logger.info("=" * 80)
        logger.info("📊 FINAL VALIDATION")
        logger.info("=" * 80)
        logger.info(f"✅ Disease Name: {disease_info.get('name')}")
        logger.info(f"✅ Description: {len(disease_info.get('description', ''))} chars")
        logger.info(f"✅ Treatment Steps: {len(disease_info.get('treatment', []))}")
        logger.info(f"✅ Severity: {disease_info.get('severity')}")

        if 'pesticide' in disease_info:
            for treatment_type in ['chemical', 'organic']:
                if treatment_type in disease_info['pesticide']:
                    t = disease_info['pesticide'][treatment_type]
                    logger.info(f"")
                    logger.info(f"📦 {treatment_type.upper()}:")
                    logger.info(f"  Name: {t.get('name')}")
                    logger.info(f"  Usage: {len(t.get('usage', ''))} chars - {bool(t.get('usage'))}")
                    logger.info(f"  Frequency: {len(t.get('frequency', ''))} chars - {bool(t.get('frequency'))}")
                    logger.info(f"  Safety: {len(t.get('safety', ''))} chars - {bool(t.get('safety'))}")
                    logger.info(f"  Dosage: {t.get('dosage_per_hectare')} {t.get('unit')}/hectare")

        if 'pesticide' in disease_info:
            for treatment_type in ['chemical', 'organic']:
                if treatment_type not in disease_info['pesticide']:
                    continue

                treatment = disease_info['pesticide'][treatment_type]

                if 'video_sources' in treatment:
                    video_sources = treatment['video_sources']

                    if 'search_terms' in video_sources:
                        search_urls = []
                        for term in video_sources['search_terms']:
                            search_urls.append({
                                'term': term,
                                'url': f"https://www.youtube.com/results?search_query={quote_plus(term)}"
                            })
                        video_sources['search_urls'] = search_urls
                        logger.info(f"✅ Added {len(search_urls)} YouTube URLs for {treatment_type}")

                    if 'reliable_channels' in video_sources:
                        channel_urls = []
                        for channel in video_sources['reliable_channels']:
                            channel_urls.append({
                                'name': channel,
                                'url': f"https://www.youtube.com/results?search_query={quote_plus(channel + ' ' + disease_name.replace('_', ' '))}"
                            })
                        video_sources['channel_urls'] = channel_urls
                        logger.info(f"✅ Added {len(channel_urls)} channel URLs for {treatment_type}")

        logger.info("=" * 80)
        logger.info("✅ DISEASE INFO PROCESSING COMPLETE")
        logger.info("=" * 80)

        return disease_info

    except Exception as e:
        logger.error(f"❌ ERROR in get_disease_info: {e}")
        logger.error(traceback.format_exc())
        return None


def combine_disease_treatments(unique_diseases):
    logger.info("=" * 80)
    logger.info("🔀 COMBINING TREATMENTS FROM MULTIPLE DISEASES")
    logger.info("=" * 80)

    combined = {
        'diseases': [],
        'description': '',
        'treatment': [],
        'severity': 'Unknown',
        'pesticide': {
            'chemical': {
                'name': 'Combined Chemical Treatment',
                'usage': [],
                'frequency': [],
                'safety': [],
                'dosage_per_hectare': 0,
                'unit': 'L',
                'video_sources': {
                    'search_terms': [],
                    'reliable_channels': []
                }
            },
            'organic': {
                'name': 'Combined Organic Treatment',
                'usage': [],
                'frequency': [],
                'safety': [],
                'dosage_per_hectare': 0,
                'unit': 'L',
                'video_sources': {
                    'search_terms': [],
                    'reliable_channels': []
                }
            }
        },
        'additional_resources': {
            'step_by_step_guide': [],
            'extension_guides': []
        }
    }

    severity_levels = {'Low': 1, 'Moderate': 2, 'Medium': 2, 'High': 3, 'Severe': 4}
    max_severity_score = 0

    unique_chemical_names = set()
    unique_organic_names = set()
    unique_treatments = set()
    unique_guides = set()

    logger.info(f"📊 Processing {len(unique_diseases)} diseases...")

    for disease, data in unique_diseases.items():
        disease_info = data['disease_info']
        if not disease_info:
            logger.warning(f"⚠️ No disease info for {disease}")
            continue

        logger.info(f"   Processing: {disease}")

        combined['diseases'].append({
            'name': disease,
            'display_name': disease.replace('_', ' '),
            'count': data['count'],
            'avg_confidence': data['total_confidence'] / data['count']
        })

        if disease_info.get('description'):
            combined['description'] += f"**{disease.replace('_', ' ')}**: {disease_info['description']}\n\n"

        if disease_info.get('treatment'):
            header = f"=== Treatment for {disease.replace('_', ' ')} ==="
            if header not in unique_treatments:
                combined['treatment'].append(header)
                unique_treatments.add(header)

                for step in disease_info['treatment']:
                    if step and step not in unique_treatments:
                        combined['treatment'].append(step)
                        unique_treatments.add(step)

                combined['treatment'].append("")

        disease_severity = disease_info.get('severity', 'Unknown')
        severity_score = severity_levels.get(disease_severity, 0)
        if severity_score > max_severity_score:
            max_severity_score = severity_score
            combined['severity'] = disease_severity
            logger.info(f"   Updated max severity: {disease_severity}")

        if 'pesticide' in disease_info:
            for treatment_type in ['chemical', 'organic']:
                if treatment_type not in disease_info['pesticide']:
                    continue

                treatment = disease_info['pesticide'][treatment_type]
                unique_set = unique_chemical_names if treatment_type == 'chemical' else unique_organic_names

                treatment_name = treatment.get('name', '')
                if treatment_name and treatment_name not in unique_set:
                    unique_set.add(treatment_name)
                    usage_text = f"**{treatment_name}** ({disease.replace('_', ' ')}): {treatment.get('usage', 'Apply as directed')}"
                    combined['pesticide'][treatment_type]['usage'].append(usage_text)
                    logger.info(f"      Added {treatment_type}: {treatment_name}")

                if treatment.get('frequency'):
                    freq = treatment['frequency'].strip()
                    if freq not in combined['pesticide'][treatment_type]['frequency']:
                        combined['pesticide'][treatment_type]['frequency'].append(freq)

                if treatment.get('safety'):
                    safety = treatment['safety'].strip()
                    if safety not in combined['pesticide'][treatment_type]['safety']:
                        combined['pesticide'][treatment_type]['safety'].append(safety)

                dosage = treatment.get('dosage_per_hectare', 0)
                combined['pesticide'][treatment_type]['dosage_per_hectare'] += dosage

                if treatment.get('video_sources'):
                    video_sources = treatment['video_sources']

                    if 'search_terms' in video_sources:
                        for term in video_sources['search_terms']:
                            if term not in combined['pesticide'][treatment_type]['video_sources']['search_terms']:
                                combined['pesticide'][treatment_type]['video_sources']['search_terms'].append(term)

                    if 'reliable_channels' in video_sources:
                        for channel in video_sources['reliable_channels']:
                            if channel not in combined['pesticide'][treatment_type]['video_sources']['reliable_channels']:
                                combined['pesticide'][treatment_type]['video_sources']['reliable_channels'].append(channel)

        if 'additional_resources' in disease_info:
            resources = disease_info['additional_resources']

            if 'step_by_step_guide' in resources:
                for step in resources['step_by_step_guide']:
                    if step not in combined['additional_resources']['step_by_step_guide']:
                        combined['additional_resources']['step_by_step_guide'].append(step)

            if 'extension_guides' in resources:
                for guide in resources['extension_guides']:
                    if guide not in unique_guides:
                        combined['additional_resources']['extension_guides'].append(guide)
                        unique_guides.add(guide)

    logger.info("📝 Formatting combined treatment data...")

    for treatment_type in ['chemical', 'organic']:
        if combined['pesticide'][treatment_type]['usage']:
            combined['pesticide'][treatment_type]['usage'] = "\n\n".join(
                combined['pesticide'][treatment_type]['usage']
            )
        else:
            combined['pesticide'][treatment_type]['usage'] = "Apply treatments according to product labels for each specific disease."

        if combined['pesticide'][treatment_type]['frequency']:
            unique_freq = list(set(combined['pesticide'][treatment_type]['frequency']))
            if len(unique_freq) == 1:
                combined['pesticide'][treatment_type]['frequency'] = unique_freq[0]
            else:
                combined['pesticide'][treatment_type]['frequency'] = " OR ".join(unique_freq)
        else:
            combined['pesticide'][treatment_type]['frequency'] = "Follow individual disease treatment schedules"

        if combined['pesticide'][treatment_type]['safety']:
            combined['pesticide'][treatment_type]['safety'] = " • ".join(
                list(set(combined['pesticide'][treatment_type]['safety']))
            )
        else:
            combined['pesticide'][treatment_type]['safety'] = "Follow all safety guidelines on product labels. Wear protective equipment."

        num_diseases = len(unique_diseases)
        if num_diseases > 0 and combined['pesticide'][treatment_type]['dosage_per_hectare'] > 0:
            combined['pesticide'][treatment_type]['dosage_per_hectare'] /= num_diseases
            logger.info(f"   {treatment_type.title()} avg dosage: {combined['pesticide'][treatment_type]['dosage_per_hectare']:.2f}")

        video_sources = combined['pesticide'][treatment_type]['video_sources']
        if video_sources['search_terms']:
            search_urls = []
            for term in video_sources['search_terms']:
                search_urls.append({
                    'term': term,
                    'url': f"https://www.youtube.com/results?search_query={quote_plus(term)}"
                })
            video_sources['search_urls'] = search_urls

        if video_sources['reliable_channels']:
            channel_urls = []
            for channel in video_sources['reliable_channels']:
                channel_urls.append({
                    'name': channel,
                    'url': f"https://www.youtube.com/results?search_query={quote_plus(channel + ' multiple plant diseases')}"
                })
            video_sources['channel_urls'] = channel_urls

    logger.info("=" * 80)
    logger.info("✅ COMBINED TREATMENT PLAN READY")
    logger.info(f"   Diseases: {len(combined['diseases'])}")
    logger.info(f"   Treatment steps: {len(combined['treatment'])}")
    logger.info(f"   Overall severity: {combined['severity']}")
    logger.info("=" * 80)

    return combined


def calculate_dosage(area, area_unit, pesticide_info, infection_pct=100.0):
    """
    Calculate pesticide dosage based on area, unit, and infection percentage.
    infection_pct: max(AI-detected plant_severity, farmer-slider infection_percent)
    """
    logger.info("=" * 60)
    logger.info("🧮 INFECTION-AWARE DOSAGE CALCULATION STARTED")
    logger.info("=" * 60)
    logger.info(f"📏 Input area: {area} {area_unit}")
    logger.info(f"🦠 Infection %: {infection_pct}")
    logger.info(f"📋 Pesticide info exists: {pesticide_info is not None}")

    try:
        chemical_dosage = None
        organic_dosage = None
        hectare_conversion = 0

        infection_pct = max(1.0, min(100.0, float(infection_pct)))

        chemical_info = pesticide_info.get("chemical", {}) if pesticide_info else {}
        organic_info = pesticide_info.get("organic", {}) if pesticide_info else {}

        logger.info(f"💊 Chemical info available: {bool(chemical_info)}")
        logger.info(f"🌿 Organic  info available: {bool(organic_info)}")

        try:
            chemical_dosage_per_hectare = float(chemical_info.get("dosage_per_hectare", 0) or 0)
        except (ValueError, TypeError):
            logger.warning("Chemical dosage_per_hectare is not numeric — defaulting to 0")
            chemical_dosage_per_hectare = 0.0

        try:
            organic_dosage_per_hectare = float(organic_info.get("dosage_per_hectare", 0) or 0)
        except (ValueError, TypeError):
            logger.warning("Organic dosage_per_hectare is not numeric — defaulting to 0")
            organic_dosage_per_hectare = 0.0

        logger.info(f"💊 Chemical base dosage/ha: {chemical_dosage_per_hectare}")
        logger.info(f"🌿 Organic  base dosage/ha: {organic_dosage_per_hectare}")

        try:
            area_float = float(area) if area else 0
            if area_float <= 0:
                logger.warning(f"⚠️ Invalid/zero area ({area}) — defaulting to 1 ha for display")
                area_float = 1.0

            conversion_factors = {
                'hectare': 1.0,
                'acre': 0.404686,
                'square_meter': 0.0001,
                'square_feet': 0.0000092903
            }
            hectare_conversion = area_float * conversion_factors.get(area_unit, 1.0)
            logger.info(f"📐 Total area: {area_float} {area_unit} = {hectare_conversion:.4f} ha")

        except (ValueError, TypeError) as e:
            logger.error(f"❌ Area conversion error: {e} — defaulting to 1 ha")
            hectare_conversion = 1.0

        effective_hectares = hectare_conversion * (infection_pct / 100.0)

        if infection_pct >= 75:
            severity_multiplier = 1.25
        elif infection_pct >= 50:
            severity_multiplier = 1.10
        elif infection_pct >= 25:
            severity_multiplier = 1.00
        else:
            severity_multiplier = 0.85

        logger.info(f"📊 Effective area (infected): {effective_hectares:.4f} ha")
        logger.info(f"📊 Severity multiplier: x{severity_multiplier}")

        if chemical_dosage_per_hectare > 0:
            chemical_dosage = chemical_dosage_per_hectare * effective_hectares * severity_multiplier
            logger.info(f"✅ Chemical dosage: {chemical_dosage_per_hectare} × {effective_hectares:.4f} × {severity_multiplier} = {chemical_dosage:.4f}")
        else:
            logger.warning("⚠️ Chemical dosage_per_hectare is 0 or missing")

        if organic_dosage_per_hectare > 0:
            organic_dosage = organic_dosage_per_hectare * effective_hectares * severity_multiplier
            logger.info(f"✅ Organic dosage: {organic_dosage_per_hectare} × {effective_hectares:.4f} × {severity_multiplier} = {organic_dosage:.4f}")
        else:
            logger.warning("⚠️ Organic dosage_per_hectare is 0 or missing")

        logger.info("=" * 60)
        logger.info("🎯 FINAL RESULTS (infection-aware):")
        logger.info(f"   Total area:        {hectare_conversion:.4f} ha")
        logger.info(f"   Infection %:        {infection_pct}%")
        logger.info(f"   Effective area:    {effective_hectares:.4f} ha")
        logger.info(f"   Severity mult:     x{severity_multiplier}")
        logger.info(f"   Chemical dosage:   {chemical_dosage}")
        logger.info(f"   Organic  dosage:   {organic_dosage}")
        logger.info("=" * 60)

        return chemical_dosage, organic_dosage, hectare_conversion

    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR IN DOSAGE CALCULATION")
        logger.error(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        return None, None, 0


# ===== PLANT IMAGE VALIDATION (kept for segmentation pre-checks) =====

def is_plant_image(image_path):
    """
    Check if the uploaded image is likely a plant image using multiple validation techniques.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.warning("Could not read image file")
            return False

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        green_ranges = [
            ([35, 50, 50], [85, 255, 255]),
            ([25, 30, 30], [75, 255, 200]),
            ([15, 40, 40], [35, 255, 255])
        ]

        total_green_pixels = 0
        for lower, upper in green_ranges:
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            total_green_pixels += cv2.countNonZero(mask)

        total_pixels = img.shape[0] * img.shape[1]
        green_ratio = total_green_pixels / total_pixels

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        texture_variance = np.var(gray)

        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = cv2.countNonZero(edges)
        edge_ratio = edge_pixels / total_pixels

        color_std = np.std(rgb, axis=(0, 1))
        color_mean = np.mean(color_std)

        brightness = np.mean(gray)
        contrast = np.std(gray)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        organic_shapes = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if 0.1 < circularity < 0.8:
                        organic_shapes += 1

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)
        straight_lines = len(lines) if lines is not None else 0

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        text_like_pixels = cv2.countNonZero(horizontal_lines)
        text_ratio = text_like_pixels / total_pixels

        height, width = img.shape[:2]

        is_reasonable_size = height > 100 and width > 100
        has_significant_green = green_ratio > 0.12
        has_organic_texture = texture_variance > 500
        has_natural_edges = 0.02 < edge_ratio < 0.25
        has_natural_colors = color_mean > 15
        reasonable_brightness = 30 < brightness < 220
        good_contrast = contrast > 20
        has_organic_shapes = organic_shapes > 0
        not_too_geometric = straight_lines < 10
        not_text_heavy = text_ratio < 0.05

        score = 0
        criteria_met = []

        if has_significant_green:
            score += 3
            criteria_met.append("green_content")
        if has_organic_texture:
            score += 2
            criteria_met.append("organic_texture")
        if has_natural_edges:
            score += 2
            criteria_met.append("natural_edges")
        if has_natural_colors:
            score += 1
            criteria_met.append("natural_colors")
        if reasonable_brightness:
            score += 1
            criteria_met.append("good_brightness")
        if good_contrast:
            score += 1
            criteria_met.append("good_contrast")
        if has_organic_shapes:
            score += 2
            criteria_met.append("organic_shapes")
        if not_too_geometric:
            score += 1
            criteria_met.append("not_geometric")
        if not_text_heavy:
            score += 1
            criteria_met.append("not_text_heavy")

        logger.info(f"Plant image analysis for {image_path}:")
        logger.info(f"  - Green ratio: {green_ratio:.3f} (threshold: 0.12)")
        logger.info(f"  - Texture variance: {texture_variance:.1f} (threshold: 500)")
        logger.info(f"  - Edge ratio: {edge_ratio:.3f} (range: 0.02-0.25)")
        logger.info(f"  - Color variation: {color_mean:.1f} (threshold: 15)")
        logger.info(f"  - Brightness: {brightness:.1f} (range: 30-220)")
        logger.info(f"  - Contrast: {contrast:.1f} (threshold: 20)")
        logger.info(f"  - Organic shapes: {organic_shapes}")
        logger.info(f"  - Straight lines: {straight_lines} (threshold: <10)")
        logger.info(f"  - Text ratio: {text_ratio:.3f} (threshold: <0.05)")
        logger.info(f"  - Total score: {score}/14")
        logger.info(f"  - Criteria met: {criteria_met}")

        is_plant = (score >= 7 and has_significant_green and is_reasonable_size)
        logger.info(f"  - Final decision: {'PLANT' if is_plant else 'NOT PLANT'}")

        return is_plant

    except Exception as e:
        logger.error(f"Error in enhanced plant image validation: {e}")
        return False


def validate_plant_type(predicted_class, confidence):
    try:
        if predicted_class not in class_names:
            logger.warning(f"Predicted class {predicted_class} not in supported classes")
            return False, "Predicted class not recognized"

        if confidence < CONFIDENCE_THRESHOLD:
            logger.warning(f"Confidence {confidence:.2f}% below threshold {CONFIDENCE_THRESHOLD}%")
            return False, f"Low confidence prediction ({confidence:.1f}%)"

        return True, None

    except Exception as e:
        logger.error(f"Error in plant type validation: {e}")
        return False, str(e)


def preprocess_image_with_validation(image, image_path):
    try:
        logger.info(f"Starting image validation for: {image_path}")

        if not is_plant_image(image_path):
            logger.warning("Image failed plant validation - not a plant image")
            return None, False

        logger.info("Image passed plant validation")

        try:
            image_test = Image.open(image_path)
            image_test.verify()
        except Exception as e:
            logger.error(f"Image file validation failed: {e}")
            return None, False

        image = image.resize((128, 128))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        logger.info("Image preprocessing completed successfully")
        return img_array, True

    except Exception as e:
        logger.error(f"Error in enhanced image preprocessing: {e}")
        return None, False


def get_detailed_error_message(error_type, image_analysis=None):
    if error_type == "not_plant":
        return {
            "title": "Not a Plant Image",
            "message": "The uploaded image doesn't appear to be a plant photograph.",
            "suggestions": [
                "Upload a clear photo of plant leaves",
                "Ensure the image shows actual plant matter (not drawings or posters)",
                "Make sure leaves are visible with any disease symptoms",
                "Use good lighting and focus on the affected plant parts"
            ],
            "technical_details": image_analysis
        }
    elif error_type == "low_confidence":
        return {
            "title": "Unable to Identify Plant Disease",
            "message": "The image quality or plant type may not be suitable for accurate analysis.",
            "suggestions": [
                "Try uploading a clearer, higher quality image",
                "Ensure the plant is one of our supported types",
                "Focus on leaves showing clear disease symptoms",
                "Check if lighting is adequate"
            ]
        }
    elif error_type == "unsupported_plant":
        return {
            "title": "Unsupported Plant Type",
            "message": "This plant type may not be in our current database.",
            "suggestions": [
                "Check our supported plants list",
                "Try with Apple, Tomato, Potato, Corn, Grape, Peach, Pepper, or Strawberry plants",
                "Ensure the image clearly shows the plant type"
            ]
        }
    else:
        return {
            "title": "Analysis Error",
            "message": "An error occurred during image analysis.",
            "suggestions": [
                "Try uploading the image again",
                "Ensure the image file is not corrupted",
                "Use a different image format (JPG, PNG)"
            ]
        }


def initialize_enhanced_gemini():
    """AI removed - chatbot runs in rule-based mode only"""
    return False, "AI not configured"


def get_enhanced_chatbot_response(message, detected_disease=None, conversation_history=None):
    """Enhanced chatbot with improved AI integration and common questions"""

    original_message = message
    message = message.lower().strip()

    logger.info(f"Enhanced chatbot processing: {original_message}")

    if message in ["help", "/help", "commands", "/commands"]:
        return generate_help_response()

    elif message in ["questions", "/questions", "common questions", "examples"]:
        return generate_common_questions_response()

    elif message.startswith("/category "):
        category = message.replace("/category ", "").strip()
        return generate_category_questions(category)

    elif any(keyword in message for keyword in ["date", "time", "today", "current date", "current time"]):
        current_datetime = datetime.now()
        if "time" in message:
            return f"🕐 Current time: {current_datetime.strftime('%H:%M:%S')} IST"
        elif "date" in message:
            return f"📅 Today's date: {current_datetime.strftime('%B %d, %Y (%A)')}"
        else:
            return f"📅🕐 Current date and time: {current_datetime.strftime('%B %d, %Y %H:%M:%S (%A)')}"

    elif any(greeting in message for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "namaste", "start"]):
        greeting_response = """🌱 **Namaste! Welcome to AgriPal AI!** 

I'm your intelligent agricultural assistant powered by advanced AI. I can help you with:

🔍 **Disease Detection** - Upload images for instant plant disease identification
💊 **Treatment Plans** - Get specific, science-based treatment recommendations  
🧮 **Dosage Calculator** - Calculate exact pesticide amounts for your farm size
🌿 **Organic Solutions** - Eco-friendly pest and disease management
📊 **Crop Management** - Seasonal advice and farming best practices
🤖 **AI-Powered Q&A** - Ask any agricultural question, get expert answers

**Quick Start Commands:**
- Type `questions` to see common agricultural questions
- Type `help` to see available commands
- Ask specific questions like "How to treat tomato blight?"

What would you like to explore today? 🚀"""
        return greeting_response

    elif any(farewell in message for farewell in ["bye", "goodbye", "see you", "thanks", "thank you", "dhanyawad"]):
        return """🙏 **Thank you for using AgriPal AI!** 

**Remember these key farming tips:**
- Monitor your crops regularly for early disease detection
- Maintain good field hygiene and crop rotation
- Keep learning about sustainable farming practices

Happy farming! 🌾🚜✨"""

    else:
        return get_fallback_response(original_message, detected_disease)


def get_common_questions_by_category(category=None, limit=5):
    if category and category in COMMON_QUESTIONS:
        questions = COMMON_QUESTIONS[category]
        return random.sample(questions, min(limit, len(questions)))
    else:
        all_questions = []
        for cat_questions in COMMON_QUESTIONS.values():
            all_questions.extend(cat_questions)
        return random.sample(all_questions, min(limit, len(all_questions)))


def generate_help_response():
    return """🆘 **AgriPal AI Help Center**

**Available Commands:**
- `help` - Show this help menu
- `questions` - View common agricultural questions
- `/category [name]` - Get questions by category

**Categories:**
- `plant_diseases` - Disease identification
- `treatment_methods` - Treatment options
- `crop_management` - Farming practices
- `seasonal_advice` - Season-specific guidance
- `technology_agriculture` - Modern farming tech

**Example Questions:**
- "What causes yellow leaves in tomatoes?"
- "How to make organic pesticide?"
- "Best time to plant vegetables?"

Just type your question naturally! 🌱"""


def generate_common_questions_response():
    questions = get_common_questions_by_category(limit=8)

    response = "❓ **Popular Agricultural Questions**\n\n"

    for i, question in enumerate(questions, 1):
        response += f"**{i}.** {question}\n"

    response += "\n**More Help:** Type `/category plant_diseases` for specific topics!"
    return response


def generate_category_questions(category):
    if category not in COMMON_QUESTIONS:
        available_categories = ", ".join(COMMON_QUESTIONS.keys())
        return f"❓ Category '{category}' not found.\n\n**Available:** {available_categories}"

    questions = COMMON_QUESTIONS[category]
    category_title = category.replace('_', ' ').title()

    response = f"📚 **{category_title} - Questions**\n\n"

    for i, question in enumerate(questions, 1):
        response += f"**{i}.** {question}\n"

    return response


def get_fallback_response(original_message, detected_disease=None, error_msg=None):
    fallback = f"""🤖 **AgriPal AI Assistant** *(Offline Mode)*

**Your question:** "{original_message}"

"""

    if detected_disease:
        fallback += f"**Detected disease:** {detected_disease}\n\n"

    message_lower = original_message.lower()

    if any(word in message_lower for word in ["disease", "fungus", "infection"]):
        fallback += """**For plant diseases:**
🔍 Take clear photos of affected areas
✂️ Remove diseased plant parts
🌿 Apply appropriate treatment
📞 Consult agricultural extension officer"""

    elif any(word in message_lower for word in ["treatment", "pesticide", "spray"]):
        fallback += """**Treatment guidelines:**
🧪 Use registered pesticides as per label
🌱 Try organic options (neem oil, copper sulfate)
⏰ Apply during cool hours
⚠️ Always wear protective equipment"""

    fallback += "\n\n**Try:** `questions` for common topics or `help` for commands"

    return fallback


# ===== WEEKLY ASSESSMENT FUNCTIONS =====

def analyze_weekly_progress(user_id, plant_type, current_detection, detection_mode='continue'):
    logger.info("=" * 80)
    logger.info("📊 WEEKLY ASSESSMENT ANALYSIS")
    logger.info(f"🔁 Mode: {detection_mode}")
    logger.info("=" * 80)

    if detection_mode == 'new':
        logger.info("🆕 NEW detection mode - starting fresh weekly tracking")
        return {
            'is_first_assessment': True,
            'week_number': 1,
            'recommendation': 'New plant tracking started. Baseline recorded. Upload again next week to track progress.',
            'dosage_recommendation': 'maintain',
            'next_assessment_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }

    _all_recs = WeeklyAssessment.query.filter_by(
        user_id=user_id, plant_type=plant_type
    ).order_by(WeeklyAssessment.assessment_date.desc()).all()
    previous_assessments = []
    for _ar in _all_recs:
        previous_assessments.append(_ar)
        if _ar.week_number == 1:
            break

    if not previous_assessments:
        logger.info("🆕 First assessment for this plant")
        return {
            'is_first_assessment': True,
            'week_number': 1,
            'recommendation': 'Start treatment as recommended. Take photos weekly to track progress.',
            'dosage_recommendation': 'maintain',
            'next_assessment_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }

    last_week = previous_assessments[0]
    week_number = last_week.week_number + 1

    logger.info(f"📅 Week {week_number} Assessment")
    logger.info(f"📈 Previous Week {last_week.week_number}: {last_week.severity_level}")

    severity_map = {'Low': 1, 'Moderate': 2, 'High': 3, 'Severe': 4}

    current_severity_score = severity_map.get(current_detection['severity'], 0)
    previous_severity_score = last_week.severity_score

    severity_change = current_severity_score - previous_severity_score

    current_affected = current_detection.get('color_severity', 0)
    previous_affected = last_week.color_severity_percent or 0
    area_change_percent = current_affected - previous_affected

    is_improving = severity_change < 0 or area_change_percent < -5
    is_worsening = severity_change > 0 or area_change_percent > 5
    is_stable = abs(severity_change) == 0 and abs(area_change_percent) <= 5
    is_cured = current_detection.get('disease', '').lower().endswith('healthy')

    logger.info(f"📊 Progress Analysis:")
    logger.info(f"   - Severity change: {severity_change}")
    logger.info(f"   - Area change: {area_change_percent:+.1f}%")
    logger.info(f"   - Improving: {is_improving}")
    logger.info(f"   - Worsening: {is_worsening}")
    logger.info(f"   - Cured: {is_cured}")

    recommendation, dosage_change, switch_treatment = generate_treatment_recommendation(
        is_improving, is_worsening, is_stable, is_cured,
        week_number, last_week, current_detection
    )

    assessment_result = {
        'is_first_assessment': False,
        'week_number': week_number,
        'previous_week_severity': last_week.severity_level,
        'current_severity': current_detection['severity'],
        'severity_change': severity_change,
        'area_change_percent': area_change_percent,
        'is_improving': is_improving,
        'is_worsening': is_worsening,
        'is_stable': is_stable,
        'is_cured': is_cured,
        'recommendation': recommendation,
        'dosage_recommendation': dosage_change,
        'treatment_switch': switch_treatment,
        'previous_treatment': last_week.pesticide_used,
        'previous_dosage': last_week.dosage_applied,
        'next_assessment_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'assessment_history': [
            {
                'week': a.week_number,
                'date': a.assessment_date.strftime('%Y-%m-%d'),
                'severity': a.severity_level,
                'affected_area': a.affected_area_percent,
                'treatment': a.pesticide_used
            } for a in reversed(previous_assessments)
        ]
    }

    logger.info("=" * 80)
    logger.info(f"✅ Assessment Complete: {recommendation[:100]}...")
    logger.info("=" * 80)

    return assessment_result


def generate_treatment_recommendation(is_improving, is_worsening, is_stable,
                                      is_cured, week_number, last_assessment,
                                      current_detection):
    if is_cured:
        return (
            "🎉 Excellent! Your plant has fully recovered! "
            "Continue with preventive care: maintain good hygiene, proper watering, "
            "and monitor weekly. No pesticides needed unless symptoms reappear.",
            "stop",
            None
        )

    if is_improving:
        if week_number <= 2:
            recommendation = (
                "✅ Great progress! Disease severity is decreasing. "
                "Continue with current treatment plan. "
                "Keep dosage the same for one more week to ensure effectiveness."
            )
            dosage_change = "maintain"
            switch = None
        else:
            recommendation = (
                f"✅ Continued improvement over {week_number} weeks! "
                f"You can now REDUCE pesticide dosage by 25-30% as the plant is responding well. "
                f"Previous dosage: {last_assessment.dosage_applied:.2f}L - "
                f"Reduce to: {last_assessment.dosage_applied * 0.70:.2f}L. "
                f"This reduces chemical load while maintaining effectiveness."
            )
            dosage_change = "decrease_25"
            switch = None

        return recommendation, dosage_change, switch

    if is_stable:
        if week_number >= 3:
            current_type = last_assessment.pesticide_type
            switch_to = "organic" if current_type == "chemical" else "stronger chemical"

            recommendation = (
                f"⚠️ Disease is stable but not improving after {week_number} weeks. "
                f"Current treatment ({last_assessment.pesticide_used}) may not be fully effective. "
                f"RECOMMENDATION: Switch to {switch_to} treatment alternative. "
                f"Also increase application frequency."
            )
            dosage_change = "maintain_or_increase"
            switch = switch_to
        else:
            recommendation = (
                "📊 Disease severity is stable. Continue current treatment "
                "but monitor closely. If no improvement by next week, "
                "we'll recommend switching treatments."
            )
            dosage_change = "maintain"
            switch = None

        return recommendation, dosage_change, switch

    if is_worsening:
        if week_number <= 2:
            recommendation = (
                "⚠️ WARNING: Disease is progressing despite treatment! "
                f"IMMEDIATE ACTION NEEDED: "
                f"1. INCREASE dosage by 30-40% "
                f"(from {last_assessment.dosage_applied:.2f}L to "
                f"{last_assessment.dosage_applied * 1.35:.2f}L). "
                f"2. Increase application frequency. "
                f"3. Remove and destroy heavily infected plant parts. "
                f"4. Improve field sanitation."
            )
            dosage_change = "increase_35"
            switch = None
        else:
            current_type = last_assessment.pesticide_type

            if current_type == "organic":
                recommendation = (
                    f"🚨 CRITICAL: Disease worsening after {week_number} weeks of organic treatment. "
                    f"URGENT RECOMMENDATION: Switch to CHEMICAL pesticides immediately. "
                    f"Organic methods are not controlling the infection. "
                    f"Suggested: Use systemic fungicide/pesticide for this disease. "
                    f"Consider consulting agricultural extension officer."
                )
                switch = "chemical_systemic"
            else:
                recommendation = (
                    f"🚨 CRITICAL: Disease worsening despite chemical treatment for {week_number} weeks. "
                    f"URGENT ACTIONS: "
                    f"1. Switch to DIFFERENT chemical class (avoid resistance) "
                    f"2. Increase dosage by 40% "
                    f"3. Apply every 5 days instead of weekly "
                    f"4. Consider professional consultation "
                    f"5. Test if disease strain is pesticide-resistant"
                )
                switch = "different_chemical_class"

            dosage_change = "increase_40"

        return recommendation, dosage_change, switch

    return (
        "Continue monitoring. Take clear photos weekly for accurate tracking.",
        "maintain",
        None
    )


def save_weekly_assessment(user_id, plant_type, detection_data, assessment_result):
    try:
        severity_map = {'Low': 1, 'Moderate': 2, 'High': 3, 'Severe': 4}

        assessment = WeeklyAssessment(
            user_id=user_id,
            plant_type=plant_type,
            disease_name=detection_data.get('disease', 'Unknown'),
            week_number=assessment_result['week_number'],
            assessment_date=datetime.now(),
            severity_level=detection_data.get('severity', 'Unknown'),
            severity_score=severity_map.get(detection_data.get('severity', 'Unknown'), 0),
            color_severity_percent=detection_data.get('color_severity', 0),
            affected_area_percent=detection_data.get('affected_percentage', 0),
            pesticide_used=detection_data.get('pesticide_used', 'Not specified'),
            pesticide_type=detection_data.get('pesticide_type', 'chemical'),
            dosage_applied=detection_data.get('dosage_applied', 0),
            application_method=detection_data.get('application_method', 'Spray'),
            is_improving=assessment_result.get('is_improving', False),
            is_worsening=assessment_result.get('is_worsening', False),
            is_stable=assessment_result.get('is_stable', False),
            is_cured=assessment_result.get('is_cured', False),
            recommendation=assessment_result.get('recommendation', ''),
            recommended_dosage_change=assessment_result.get('dosage_recommendation', 'maintain'),
            recommended_switch=assessment_result.get('treatment_switch'),
            image_filename=detection_data.get('image_filename'),
            farmer_notes=detection_data.get('farmer_notes', '')
        )

        db.session.add(assessment)
        db.session.commit()

        logger.info(f"✅ Weekly assessment saved: Week {assessment_result['week_number']}")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving weekly assessment: {e}")
        db.session.rollback()
        return False


def startup_gemini_check():
    logger.info("🚀 Initializing Enhanced AgriPal Chatbot...")
    success, message = initialize_enhanced_gemini()
    if success:
        logger.info(f"✅ Chatbot Ready: {message}")
    else:
        logger.warning(f"⚠️ AI Limited Mode: {message}")
    return success


# ===== REGISTER BLUEPRINTS =====
app.register_blueprint(auth_bp)
app.register_blueprint(post_harvest_bp)
app.register_blueprint(schemes_bp)


# ===== SESSION MANAGEMENT =====
def clear_sessions_on_startup():
    session_dir = './.flask_session/'
    if os.path.exists(session_dir):
        try:
            shutil.rmtree(session_dir)
            logger.info("🗑️ Cleared all previous sessions")
        except Exception as e:
            logger.error(f"❌ Error clearing sessions: {e}")
    os.makedirs(session_dir, exist_ok=True)


def init_database():
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created successfully")
        try:
            import sqlite3 as _mig_sq3
            _db_paths = ["agripal.db", "instance/agripal.db", "database.db"]
            for _dp in _db_paths:
                if os.path.exists(_dp):
                    _mc = _mig_sq3.connect(_dp)
                    _cur = _mc.cursor()
                    _cur.execute("PRAGMA table_info(weekly_assessments)")
                    _existing = {r[1] for r in _cur.fetchall()}
                    _new_cols = [
                        ("field_name", "VARCHAR(100) DEFAULT 'Field 1'"),
                        ("field_location", "VARCHAR(200) DEFAULT ''"),
                        ("session_id", "VARCHAR(64)  DEFAULT ''"),
                    ]
                    for _col, _def in _new_cols:
                        if _col not in _existing and _existing:
                            _mc.execute(f"ALTER TABLE weekly_assessments ADD COLUMN {_col} {_def}")
                            logger.info(f"✅ Auto-migrated: added column {_col} to weekly_assessments")
                    _mc.commit()
                    _mc.close()
        except Exception as _me:
            logger.warning(f"⚠️ Auto-migration warning: {_me}")


@app.before_request
def validate_session():
    if request.endpoint and (
        request.endpoint.startswith('static') or
        request.endpoint.startswith('auth.') or
        request.endpoint == 'index' or
        request.endpoint == 'health_check' or
        request.endpoint == 'api_info'
    ):
        return

    if current_user.is_authenticated:
        if 'session_start' not in session:
            logout_user()
            session.clear()
            flash('Your session has expired. Please login again.', 'warning')
            return redirect(url_for('auth.login'))

        session_server_start = session.get('server_start')
        current_server_start = app.config['SERVER_START_TIME']

        if session_server_start != current_server_start:
            logout_user()
            session.clear()
            flash('Server was restarted. Please login again.', 'info')
            return redirect(url_for('auth.login'))


def check_previous_detection(user_id, plant_type):
    try:
        one_month_ago = datetime.now() - timedelta(days=30)

        previous = DiseaseDetection.query.filter(
            DiseaseDetection.user_id == user_id,
            DiseaseDetection.plant_type == plant_type,
            DiseaseDetection.detection_time >= one_month_ago
        ).order_by(DiseaseDetection.detection_time.desc()).first()

        if previous:
            days_ago = (datetime.now() - previous.detection_time).days
            logger.info(f"📊 Found previous {plant_type} detection from {days_ago} days ago")
            return True, previous, days_ago

        return False, None, 0

    except Exception as e:
        logger.error(f"Error checking previous detection: {e}")
        return False, None, 0


def compare_disease_progress(previous_detection, current_severity, current_disease):
    severity_map = {'Low': 1, 'Moderate': 2, 'High': 3, 'Severe': 4}

    prev_severity_score = severity_map.get(previous_detection.severity, 0)
    curr_severity_score = severity_map.get(current_severity, 0)

    comparison = {
        'previous_disease': previous_detection.detected_disease,
        'previous_severity': previous_detection.severity,
        'current_disease': current_disease,
        'current_severity': current_severity,
        'days_since_last': (datetime.now() - previous_detection.detection_time).days,
        'improved': False,
        'worsened': False,
        'same': False,
        'message': '',
        'recommendation': ''
    }

    if previous_detection.detected_disease == current_disease:
        if curr_severity_score < prev_severity_score:
            comparison['improved'] = True
            comparison['message'] = f"🎉 Great news! Your {previous_detection.plant_type} is improving! Severity reduced from {previous_detection.severity} to {current_severity}."
            comparison['recommendation'] = "Continue with your current treatment plan. Keep monitoring regularly."

        elif curr_severity_score > prev_severity_score:
            comparison['worsened'] = True
            comparison['message'] = f"⚠️ Alert: Disease severity has increased from {previous_detection.severity} to {current_severity}."
            comparison['recommendation'] = "Current treatment may not be effective. Consider switching to stronger alternatives or consult an expert."

        else:
            comparison['same'] = True
            comparison['message'] = f"📊 Disease severity remains {current_severity}."
            comparison['recommendation'] = "Continue treatment. If no improvement in next week, consider alternative methods."

    else:
        if 'healthy' in current_disease.lower():
            comparison['improved'] = True
            comparison['message'] = f"🌟 Excellent! Your plant has recovered from {previous_detection.detected_disease}!"
            comparison['recommendation'] = "Maintain good crop management practices to prevent future infections."
        else:
            comparison['worsened'] = True
            comparison['message'] = f"⚠️ New disease detected: {current_disease} (previously: {previous_detection.detected_disease})"
            comparison['recommendation'] = "Multiple diseases detected. Implement comprehensive disease management strategy."

    return comparison


# ===== ROUTES =====

@app.route('/')
def index():
    if current_user.is_authenticated:
        logger.info(f"Authenticated user {current_user.username} accessing root - redirecting to dashboard")
        return redirect(url_for('dashboard'))
    logger.info("Guest user accessing landing page")
    return render_template('index2.html')


@app.route('/chatbot')
@login_required
def chatbot_page():
    logger.info(f"User {current_user.username} accessing chatbot")
    return render_template('chatbot.html')


@app.route('/dashboard')
@login_required
def dashboard():
    total_detections = DiseaseDetection.query.filter_by(user_id=current_user.id).count()
    recent_detections = DiseaseDetection.query.filter_by(user_id=current_user.id) \
        .order_by(DiseaseDetection.detection_time.desc()).limit(10).all()

    total_assessments = WeeklyAssessment.query.filter_by(user_id=current_user.id).count()

    disease_stats = db.session.query(
        DiseaseDetection.detected_disease,
        db.func.count(DiseaseDetection.id).label('count')
    ).filter_by(user_id=current_user.id) \
        .group_by(DiseaseDetection.detected_disease) \
        .order_by(db.text('count DESC')) \
        .limit(5).all()

    plant_stats = db.session.query(
        DiseaseDetection.plant_type,
        db.func.count(DiseaseDetection.id).label('count')
    ).filter_by(user_id=current_user.id) \
        .group_by(DiseaseDetection.plant_type) \
        .all()

    try:
        weekly_assessments_raw = WeeklyAssessment.query.filter_by(user_id=current_user.id) \
            .order_by(WeeklyAssessment.plant_type, WeeklyAssessment.assessment_date.desc()) \
            .all()
        raw_by_plant = {}
        for _a in weekly_assessments_raw:
            raw_by_plant.setdefault(_a.plant_type, []).append(_a)
        weekly_assessments = {}
        for _pt, _recs in raw_by_plant.items():
            _sessions, _cur = [], []
            for _r in _recs:
                _cur.append(_r)
                if _r.week_number == 1:
                    _sessions.append(_cur)
                    _cur = []
            if _cur:
                _sessions.append(_cur)
            _total = len(_sessions)
            for _i, _sess in enumerate(_sessions):
                _key = _pt if _total == 1 else f"{_pt} (Session {_total - _i})"
                weekly_assessments[_key] = _sess
    except Exception as _we:
        logger.error(f"Weekly assessment query error: {_we}")
        weekly_assessments = {}

    return render_template('dashboard.html',
                           total_detections=total_detections,
                           total_assessments=total_assessments,
                           recent_detections=recent_detections,
                           disease_stats=disease_stats,
                           plant_stats=plant_stats,
                           weekly_assessments=weekly_assessments,
                           timedelta=timedelta)


@app.route('/api/chat/enhanced', methods=['POST'])
def enhanced_chat_api():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400

        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        conversation_history = data.get('history', [])
        detected_disease = data.get('detected_disease')

        if not detected_disease:
            try:
                with open('detected_disease.json', 'r') as f:
                    disease_data = json.load(f)
                    detected_disease = disease_data.get('disease')
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        response_text = get_enhanced_chatbot_response(
            user_message,
            detected_disease,
            conversation_history
        )

        return jsonify({
            'success': True,
            'response': response_text,
            'timestamp': datetime.now().isoformat(),
            'detected_disease': detected_disease,
            'ai_status': 'offline'
        })

    except Exception as e:
        logger.error(f"Enhanced Chat API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your message',
            'details': str(e)
        }), 500


@app.route('/api/chat/common-questions')
def get_common_questions_api():
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))

        if category:
            if category not in COMMON_QUESTIONS:
                return jsonify({
                    'success': False,
                    'error': f'Category not found: {category}',
                    'available_categories': list(COMMON_QUESTIONS.keys())
                }), 404

            questions = get_common_questions_by_category(category, limit)
            return jsonify({
                'success': True,
                'category': category,
                'questions': questions,
                'total': len(questions)
            })
        else:
            all_categories = {}
            for cat, questions in COMMON_QUESTIONS.items():
                all_categories[cat] = {
                    'title': cat.replace('_', ' ').title(),
                    'sample_questions': questions[:3],
                    'total_questions': len(questions)
                }

            return jsonify({
                'success': True,
                'categories': all_categories,
                'total_questions': sum(len(q) for q in COMMON_QUESTIONS.values())
            })

    except Exception as e:
        logger.error(f"Common questions API error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat/system-status')
def chat_status():
    try:
        detected_disease = None
        detection_time = None

        try:
            with open('detected_disease.json', 'r') as f:
                disease_data = json.load(f)
                detected_disease = disease_data.get('disease')
                detection_time = disease_data.get('timestamp')
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        return jsonify({
            'success': True,
            'ai_available': False,
            'detected_disease': detected_disease,
            'detection_time': detection_time,
            'model_loaded': model is not None,
            'supported_plants': len(SUPPORTED_PLANTS)
        })
    except Exception as e:
        logger.error(f"Chat status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user-data', methods=['GET'])
@login_required
def get_user_data():
    try:
        user = current_user

        user_data = {
            'location': user.location if hasattr(user, 'location') and user.location else '',
            'land_area': user.land_area if hasattr(user, 'land_area') and user.land_area else 0,
            'area_unit': user.area_unit if hasattr(user, 'area_unit') and user.area_unit else 'square_meter'
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({
            'location': '',
            'land_area': 0,
            'area_unit': 'square_meter'
        }), 200


@app.route('/detection-tool')
@login_required
def detection_tool():
    logger.info(f"User {current_user.username} accessing detection tool")
    return render_template('detection-tool.html')


@app.route('/detection')
def detection():
    logger.info("Rendering detection page")
    return render_template('detection-tool.html')


@app.route('/about-us')
def about_us():
    logger.info("Rendering about-us page")
    return render_template('about-us.html')


@app.route('/contact')
def contact():
    logger.info("Rendering contact page")
    return render_template('contact.html')


@app.route('/library')
def library():
    logger.info("Rendering library page")
    return render_template('library.html')


@app.route('/post-harvest')
def post_harvest_page():
    section = request.args.get('section', '') or request.args.get('service', '')
    shop_type = request.args.get('type', '')
    logger.info(f"Rendering post-harvest page (section={section}, shop_type={shop_type})")
    return render_template('post-harvest.html', auto_section=section, auto_shop_type=shop_type)


@app.route('/schemes')
def schemes_page():
    logger.info("Schemes route accessed - redirecting to post-harvest schemes section")
    return redirect(url_for('post_harvest_page', section='schemes'))


@app.route('/api/plant-session/active', methods=['GET'])
@login_required
def get_active_plant_session():
    try:
        cutoff = datetime.now() - timedelta(days=60)
        latest = DiseaseDetection.query.filter(
            DiseaseDetection.user_id == current_user.id,
            DiseaseDetection.detection_time >= cutoff
        ).order_by(DiseaseDetection.detection_time.desc()).first()

        if not latest:
            return jsonify({'has_active': False})

        _all_a = WeeklyAssessment.query.filter_by(
            user_id=current_user.id, plant_type=latest.plant_type
        ).order_by(WeeklyAssessment.assessment_date.desc()).all()
        _sess = []
        for _a in _all_a:
            _sess.append(_a)
            if _a.week_number == 1:
                break
        weeks = len(_sess)
        _sev = _sess[0].severity_level if _sess else (latest.severity or 'Unknown')
        days_ago = (datetime.now() - latest.detection_time).days
        return jsonify({
            'has_active': True,
            'plant_type': latest.plant_type,
            'disease': latest.detected_disease,
            'severity': _sev,
            'weeks_tracked': weeks,
            'last_detection_days_ago': days_ago,
            'last_detection_date': latest.detection_time.strftime('%d %b %Y'),
        })
    except Exception as e:
        logger.error(f"Error getting active plant session: {e}")
        return jsonify({'has_active': False, 'error': str(e)}), 500


@app.route('/api/plant-session/history', methods=['GET'])
@login_required
def get_plant_session_history():
    try:
        cutoff = datetime.now() - timedelta(days=90)
        detections = DiseaseDetection.query.filter(
            DiseaseDetection.user_id == current_user.id,
            DiseaseDetection.detection_time >= cutoff
        ).order_by(DiseaseDetection.detection_time.desc()).all()

        plants = {}
        for det in detections:
            if det.plant_type not in plants:
                _all_a = WeeklyAssessment.query.filter_by(
                    user_id=current_user.id, plant_type=det.plant_type
                ).order_by(WeeklyAssessment.assessment_date.desc()).all()
                _sess = []
                for _a in _all_a:
                    _sess.append(_a)
                    if _a.week_number == 1:
                        break
                latest_week = _sess[0] if _sess else None
                week_count = len(_sess)
                _sev = latest_week.severity_level if latest_week else (det.severity or 'Unknown')
                plants[det.plant_type] = {
                    'plant_type': det.plant_type,
                    'latest_disease': det.detected_disease,
                    'latest_severity': _sev,
                    'latest_date': det.detection_time.strftime('%d %b %Y'),
                    'days_ago': (datetime.now() - det.detection_time).days,
                    'weeks_tracked': week_count,
                    'latest_week': latest_week.week_number if latest_week else 0,
                    'is_improving': latest_week.is_improving if latest_week else None,
                    'is_cured': latest_week.is_cured if latest_week else None,
                }

        return jsonify({'success': True, 'plants': list(plants.values())})
    except Exception as e:
        logger.error(f"Error getting plant session history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plant-session/set', methods=['POST'])
@login_required
def set_plant_session():
    try:
        data = request.get_json()
        mode = data.get('detection_mode', 'new')
        plant_type = data.get('plant_type', '')

        session['detection_mode'] = mode
        session['active_plant_type'] = plant_type if mode == 'continue' else ''

        logger.info(f"Plant session set: mode={mode}, plant={plant_type}")
        return jsonify({'success': True, 'mode': mode, 'plant_type': plant_type})
    except Exception as e:
        logger.error(f"Error setting plant session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plant-session/weekly-history/<plant_type>', methods=['GET'])
@login_required
def get_weekly_history(plant_type):
    try:
        assessments = WeeklyAssessment.query.filter_by(
            user_id=current_user.id,
            plant_type=plant_type
        ).order_by(WeeklyAssessment.week_number.asc()).all()

        history = [{
            'week': a.week_number,
            'date': a.assessment_date.strftime('%d %b'),
            'severity': a.severity_level,
            'severity_score': a.severity_score,
            'disease': a.disease_name,
            'affected_area': a.affected_area_percent,
            'is_improving': a.is_improving,
            'is_worsening': a.is_worsening,
            'is_cured': a.is_cured,
            'recommendation': a.recommendation,
        } for a in assessments]

        return jsonify({'success': True, 'plant_type': plant_type, 'total_weeks': len(history), 'history': history})
    except Exception as e:
        logger.error(f"Error getting weekly history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/info')
def api_info():
    return jsonify({
        'message': 'AGRI_PAL Unified API',
        'version': '2.0',
        'status': 'running',
        'endpoints': {
            'disease_detection': {
                'predict': 'POST /predict',
                'supported_plants': 'GET /api/supported-plants',
                'treatment': 'GET /api/treatment/<disease_name>'
            },
            'post_harvest': {
                'agro_shops': 'POST /post-harvest/agro-shops',
                'markets': 'POST /post-harvest/markets',
                'storage': 'POST /post-harvest/storage'
            },
            'schemes': {
                'all_schemes': 'GET /api/schemes',
                'categories': 'GET /api/schemes/categories',
                'by_category': 'GET /api/schemes/category/<category>',
                'by_id': 'GET /api/schemes/<scheme_id>',
                'search': 'GET /api/schemes/search?q=<query>'
            },
            'chatbot': {
                'chat': 'POST /api/chat/enhanced',
                'common_questions': 'GET /api/chat/common-questions',
                'status': 'GET /api/chat/system-status'
            }
        }
    })


@app.route('/plant-library')
def plant_library():
    logger.info("Rendering plant library page")
    return render_template('library.html')


@app.route('/api/supported-plants')
def get_supported_plants():
    return jsonify({
        'supported_plants': SUPPORTED_PLANTS,
        'total_plants': len(SUPPORTED_PLANTS),
        'total_conditions': len(class_names)
    })


@app.route('/upload')
def upload_file():
    logger.info("Upload file route accessed - redirecting to detection tool")
    return detection_tool()


from flask_login import login_required, current_user


# ============================================================================
# /predict — CLOUD MODE WITH FULL WEEKLY ASSESSMENT CONTINUITY
# ============================================================================

@app.route('/predict', methods=['POST'])
@login_required
def analyze():
    """
    Cloud-mode predict endpoint.

    TensorFlow / .h5 model has been removed to stay within Render free-tier
    memory limits (512 MB).  This route:
      - Saves the uploaded image
      - Calls analyze_weekly_progress() so the week counter advances each upload
      - Calls save_weekly_assessment()  so dashboard graphs stay populated
      - Records a DiseaseDetection row so the history log keeps updating
      - Renders result1.html with a maintenance placeholder

    Dashboard continuity is preserved: every upload creates a new weekly
    data-point even while the AI model is offline.
    """

    # ── Clear any previous detection file at the start ───────────────────────
    try:
        if os.path.exists('detected_disease.json'):
            os.remove('detected_disease.json')
    except Exception as e:
        logger.error(f"Error removing old detection file: {e}")

    logger.info("=" * 80)
    logger.info("🚀 PREDICT ENDPOINT — CLOUD / MAINTENANCE MODE (with assessment tracking)")
    logger.info("=" * 80)

    # ── Validate uploaded file ────────────────────────────────────────────────
    if 'image' not in request.files:
        flash("Error: No image file uploaded.", "error")
        return render_template("error.html", back_link="/detection-tool")

    image_file = request.files['image']

    if image_file.filename == '':
        flash("Error: No image selected.", "error")
        return render_template("error.html", back_link="/detection-tool")

    if not allowed_file(image_file.filename):
        flash("Error: Invalid file type. Please upload PNG, JPG, or JPEG.", "error")
        return render_template("error.html", back_link="/detection-tool")

    try:
        # ── Get form data ─────────────────────────────────────────────────────
        location   = request.form.get("location", "").strip()
        area       = request.form.get("area", "0")
        area_unit  = request.form.get("area_unit", "square_meter")
        area_float = float(area) if area else 0.0

        # ── Save user profile data (location / land size) ─────────────────────
        try:
            user_data_updated = False
            if location:
                current_user.location = location
                user_data_updated = True
            if area_float > 0:
                current_user.land_area  = area_float
                current_user.area_unit  = area_unit
                user_data_updated = True
            if user_data_updated:
                db.session.commit()
                logger.info("✅ User profile data saved")
        except Exception as user_save_error:
            logger.warning(f"⚠️ Could not save user profile data: {user_save_error}")
            db.session.rollback()

        # ── Save uploaded image ───────────────────────────────────────────────
        image_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        image_path     = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(image_path)
        logger.info(f"✅ Image saved to: {image_path}")

        # ── Cloud-mode placeholder values ─────────────────────────────────────
        predicted_class    = "Cloud Mode — Review Required"
        overall_severity   = "Maintenance"
        dominant_plant_type = "Detected Plant"

        # ── Determine detection mode from session ─────────────────────────────
        # Honour whatever mode the user set via /api/plant-session/set;
        # fall back to 'continue' so existing tracking sessions keep advancing.
        detection_mode = session.get('detection_mode', 'continue')
        logger.info(f"📋 Detection mode from session: {detection_mode}")

        # ── Build minimal current_detection dict for assessment logic ─────────
        current_detection_data = {
            'disease'            : predicted_class,
            'severity'           : overall_severity,
            'color_severity'     : 0,
            'affected_percentage': 0,
            'image_filename'     : image_filename,
        }

        # ── Run weekly assessment logic ───────────────────────────────────────
        # This ensures the week counter increments and dashboard graphs keep
        # moving even while the AI model is offline.
        logger.info("📊 Running weekly assessment logic (cloud-mode)...")
        try:
            assessment_result = analyze_weekly_progress(
                current_user.id,
                dominant_plant_type,
                current_detection_data,
                detection_mode=detection_mode
            )
            logger.info(f"✅ Assessment complete: Week {assessment_result.get('week_number', 1)}")
        except Exception as assessment_error:
            logger.error(f"⚠️ Weekly assessment error (non-fatal): {assessment_error}")
            # Provide a safe fallback so the rest of the route still works
            assessment_result = {
                'is_first_assessment' : True,
                'week_number'         : 1,
                'recommendation'      : (
                    'AI model is currently paused on the cloud deployment. '
                    'Please use the KisanAI Chatbot or Talk to Expert for guidance.'
                ),
                'dosage_recommendation': 'maintain',
                'next_assessment_date' : (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'is_improving'         : False,
                'is_worsening'         : False,
                'is_stable'            : False,
                'is_cured'             : False,
            }

        # ── Save weekly assessment to database ────────────────────────────────
        # Keeps the dashboard graphs populated with a data-point for today.
        logger.info("💾 Saving weekly assessment record...")
        try:
            save_detection_data = {
                'disease'           : predicted_class,
                'severity'          : overall_severity,
                'color_severity'    : 0,
                'affected_percentage': 0,
                'image_filename'    : image_filename,
                'pesticide_used'    : 'N/A — Cloud Mode',
                'pesticide_type'    : 'none',
                'dosage_applied'    : 0.0,
                'application_method': 'N/A',
                'farmer_notes'      : 'Recorded during cloud/maintenance deployment.',
            }
            save_weekly_assessment(
                current_user.id,
                dominant_plant_type,
                save_detection_data,
                assessment_result
            )
            logger.info("✅ Weekly assessment record saved")
        except Exception as save_error:
            logger.error(f"⚠️ Could not save weekly assessment (non-fatal): {save_error}")
            # Do NOT re-raise — the detection record below is more important

        # ── Save detection to DB for history log ──────────────────────────────
        logger.info("💾 Saving detection record to database...")
        try:
            detection = DiseaseDetection(
                user_id              = current_user.id,
                detected_disease     = predicted_class,
                confidence           = 0.0,
                severity             = overall_severity,
                plant_type           = dominant_plant_type,
                image_filename       = image_filename,
                gradcam_filename     = None,
                farm_area            = area_float,
                farm_area_unit       = area_unit,
                farm_location        = location,
                total_leaves_analyzed= 0,
                unique_diseases_count= 0,
                is_multi_disease     = False,
                chemical_dosage      = None,
                organic_dosage       = None
            )
            db.session.add(detection)
            db.session.commit()
            logger.info("✅ Detection record saved to database (cloud-mode)")
        except Exception as db_error:
            logger.error(f"❌ Could not save detection record: {db_error}")
            db.session.rollback()

        # ── Write detected_disease.json for chatbot context ───────────────────
        try:
            with open("detected_disease.json", "w") as f:
                json.dump({
                    "disease"    : predicted_class,
                    "confidence" : 0.0,
                    "severity"   : overall_severity,
                    "plant_type" : dominant_plant_type,
                    "timestamp"  : str(datetime.now()),
                    "cloud_mode" : True
                }, f, indent=2)
        except Exception as json_error:
            logger.warning(f"⚠️ Could not write detected_disease.json: {json_error}")

        # ── Build disease_info placeholder for the result page ────────────────
        disease_info = {
            "name"       : "Manual Review Required",
            "description": (
                "The AI prediction engine is currently in maintenance mode for "
                "the cloud deployment. Your image has been logged successfully and "
                "your weekly progress record has been updated. "
                "Please use the KisanAI Chatbot for immediate crop advice or "
                "visit the 'Talk to Expert' section to send this photo to our team."
            ),
            "treatment"  : [
                "Use the KisanAI Chatbot below for immediate disease guidance.",
                "Upload clear photos of affected leaves and describe symptoms.",
                "Consult the 'Talk to Expert' section to reach our agronomists.",
                "Check the Plant Library for common disease identification tips.",
            ],
            "severity"   : overall_severity,
            "pesticide"  : {
                "chemical": {
                    "name"               : "Consult Chatbot / Expert",
                    "dosage_per_hectare" : 0,
                    "unit"               : "L",
                    "usage"              : "Please use the KisanAI Chatbot for treatment recommendations.",
                    "frequency"          : "N/A",
                    "safety"             : "Always follow product label instructions."
                },
                "organic" : {
                    "name"               : "Consult Chatbot / Expert",
                    "dosage_per_hectare" : 0,
                    "unit"               : "L",
                    "usage"              : "Please use the KisanAI Chatbot for organic treatment recommendations.",
                    "frequency"          : "N/A",
                    "safety"             : "Safe for environment — always follow label."
                }
            }
        }

        # ── Determine whether to show dosage-change banner on result page ─────
        show_dosage_change = (
            not assessment_result.get('is_first_assessment', True) and
            assessment_result.get('dosage_recommendation') != 'maintain'
        )

        logger.info("📦 Rendering cloud-mode result page")
        logger.info(f"   Week number  : {assessment_result.get('week_number', 1)}")
        logger.info(f"   Show dosage  : {show_dosage_change}")
        logger.info("=" * 80)

        return render_template(
            "result1.html",

            # ── Images ────────────────────────────────────────────────────────
            image_url          = url_for("static", filename=f"uploads/{image_filename}"),
            gradcam_url        = None,
            heatmap_url        = None,
            segmented_image_url= None,

            # ── Prediction data (placeholder) ─────────────────────────────────
            predicted_class    = predicted_class,
            confidence         = 0.0,
            severity           = overall_severity,
            total_leaves       = 0,
            all_predictions    = [],

            # ── Plant & disease info ──────────────────────────────────────────
            dominant_plant_type= dominant_plant_type,
            unique_diseases    = None,
            combined_treatments= None,
            is_multi_disease   = False,

            # ── Plant severity ────────────────────────────────────────────────
            plant_severity       = 0,
            plant_severity_level = "N/A",

            # ── Disease information ───────────────────────────────────────────
            result             = disease_info,

            # ── Farm data ─────────────────────────────────────────────────────
            area               = area,
            area_unit          = area_unit,
            location           = location,

            # ── Dosage (not calculated in cloud mode) ─────────────────────────
            chemical_dosage    = None,
            organic_dosage     = None,
            hectare_conversion = 0,

            # ── Infection-aware fields ────────────────────────────────────────
            infection_percent      = 0,
            plant_severity_pct     = 0,
            effective_infection_pct= 0,
            area_in_hectares       = 0,
            effective_area_hectares= 0,

            # ── Leaf results ──────────────────────────────────────────────────
            leaf_results       = [],

            # ── Comparison / history ──────────────────────────────────────────
            has_previous       = False,
            comparison         = None,
            days_since_last    = 0,

            # ── Weekly assessment (live data from DB) ─────────────────────────
            assessment         = assessment_result,
            has_assessment     = True,
            show_dosage_change = show_dosage_change
        )

    except Exception as e:
        db.session.rollback()
        logger.error("=" * 80)
        logger.error("❌ ERROR IN PREDICT ROUTE (CLOUD MODE)")
        logger.error("=" * 80)
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        flash("Unexpected error occurred during analysis.", "error")
        return render_template("error.html", back_link="/detection-tool"), 500


# ============================================================================
# END /predict
# ============================================================================


@app.route('/health')
def health_check():
    health_status = {
        "status"            : "ok",
        "model_loaded"      : model is not None,
        "treatments_loaded" : len(disease_treatments) > 0,
        "upload_dir_exists" : os.path.exists(app.config['UPLOAD_FOLDER']),
        "total_diseases"    : len(disease_treatments),
        "cloud_mode"        : True
    }
    return jsonify(health_status)


@app.route('/api/treatment/<disease_name>')
def treatment_api(disease_name):
    try:
        logger.info(f"Treatment API called for disease: {disease_name}")
        disease_info = get_disease_info(disease_name)
        if disease_info:
            return jsonify(disease_info)
        else:
            logger.warning(f"No disease info found for: {disease_name}")
            return jsonify({'error': 'Disease information not found'}), 404
    except Exception as e:
        logger.error(f"Treatment API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/resources/<disease_name>')
def resources_api(disease_name):
    try:
        logger.info(f"Resources API called for disease: {disease_name}")
        disease_info = get_disease_info(disease_name)
        if disease_info and 'additional_resources' in disease_info:
            return jsonify(disease_info['additional_resources'])
        else:
            return jsonify({'error': 'Additional resources not found'}), 404
    except Exception as e:
        logger.error(f"Resources API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate-dosage', methods=['POST'])
def calculate_dosage_api():
    """
    Infection-aware dosage calculation API.
    """
    try:
        data = request.json

        disease_name = data.get('disease_name')
        area         = data.get('area')
        area_unit    = data.get('area_unit', 'hectare')

        try:
            infection_percent = float(data.get('infection_percent', 50))
            infection_percent = max(1.0, min(100.0, infection_percent))
        except (ValueError, TypeError):
            infection_percent = 50.0

        try:
            plant_severity = float(data.get('plant_severity', 0))
            plant_severity = max(0.0, min(100.0, plant_severity))
        except (ValueError, TypeError):
            plant_severity = 0.0

        effective_pct = max(infection_percent, plant_severity)
        effective_pct = max(1.0, min(100.0, effective_pct))

        disease_info = get_disease_info(disease_name)
        if disease_info and 'pesticide' in disease_info:
            chemical_dosage, organic_dosage, hectare_conversion = calculate_dosage(
                area, area_unit, disease_info['pesticide'],
                infection_pct=effective_pct
            )

            CONVERSIONS = {
                'hectare': 1.0, 'acre': 0.404686,
                'square_meter': 0.0001, 'square_feet': 0.0000092903
            }
            total_ha    = float(area or 0) * CONVERSIONS.get(area_unit, 1.0)
            effective_ha= total_ha * (effective_pct / 100.0)

            if effective_pct >= 75:
                severity_mult = 1.25
            elif effective_pct >= 50:
                severity_mult = 1.10
            elif effective_pct >= 25:
                severity_mult = 1.00
            else:
                severity_mult = 0.85

            chem_info = disease_info['pesticide'].get('chemical', {})
            org_info  = disease_info['pesticide'].get('organic', {})

            return jsonify({
                'success'               : True,
                'chemical_dosage'       : chemical_dosage,
                'organic_dosage'        : organic_dosage,
                'hectare_conversion'    : hectare_conversion,
                'area'                  : area,
                'area_unit'             : area_unit,
                'effective_infection_pct': round(effective_pct, 1),
                'plant_severity_ai'     : round(plant_severity, 1),
                'user_reported_pct'     : round(infection_percent, 1),
                'total_area_hectares'   : round(total_ha, 4),
                'effective_area_hectares': round(effective_ha, 4),
                'severity_multiplier'   : severity_mult,
                'pesticide_names'       : {
                    'chemical': chem_info.get('name', 'N/A'),
                    'organic' : org_info.get('name',  'N/A'),
                },
                'breakdown_text': (
                    f"{round(effective_pct, 1)}% of your field ({round(effective_ha, 3)} ha) "
                    f"is infected out of {round(total_ha, 3)} ha total. "
                    f"Dosage multiplier: x{severity_mult} for this severity level."
                )
            })
        else:
            return jsonify({'error': 'Disease or pesticide information not found'}), 404

    except Exception as e:
        logger.error(f"Dosage calculation API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# NUTRITION TESTING ROUTES
# ============================================================================

@app.route('/nutrition-testing')
@login_required
def nutrition_testing():
    return render_template('nutrition_testing.html',
                           user=current_user,
                           location =current_user.location  if hasattr(current_user, 'location')  else '',
                           land_area=current_user.land_area if hasattr(current_user, 'land_area') else 0,
                           area_unit=current_user.area_unit if hasattr(current_user, 'area_unit') else 'square_meter')


@app.route('/analyze-nutrition', methods=['POST'])
@login_required
def analyze_nutrition():
    logger.info("=" * 80)
    logger.info("🔬 NUTRITION DEFICIENCY ANALYSIS ENDPOINT")
    logger.info("=" * 80)

    if 'image' not in request.files:
        flash("Error: No image file uploaded.", "error")
        return render_template("error.html", back_link="/nutrition-testing")

    image_file = request.files['image']

    if image_file.filename == '':
        flash("Error: No image selected.", "error")
        return render_template("error.html", back_link="/nutrition-testing")

    if not allowed_file(image_file.filename):
        flash("Error: Invalid file type. Please upload PNG, JPG, or JPEG.", "error")
        return render_template("error.html", back_link="/nutrition-testing")

    try:
        location   = request.form.get("location", "").strip()
        area       = request.form.get("area", "0")
        area_unit  = request.form.get("area_unit", "square_meter")
        area_float = float(area) if area else 0.0

        try:
            if location:
                current_user.location = location
            if area_float > 0:
                current_user.land_area = area_float
                current_user.area_unit = area_unit
            db.session.commit()
            logger.info("✅ User profile data saved")
        except Exception as e:
            logger.warning(f"⚠️ Could not save user data: {e}")
            db.session.rollback()

        image_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        image_path     = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(image_path)
        logger.info(f"✅ Image saved to: {image_path}")

        analysis_result = analyze_nutrition_deficiency(image_path)

        if not analysis_result['success']:
            flash(f"Error during analysis: {analysis_result.get('error', 'Unknown error')}", "error")
            return render_template("error.html", back_link="/nutrition-testing")

        diagnoses = analysis_result['diagnoses']

        if len(diagnoses) == 0:
            return render_template('nutrition_result.html',
                                   healthy      = True,
                                   image_url    = url_for('static', filename=f'uploads/{image_filename}'),
                                   location     = location,
                                   area         = area,
                                   area_unit    = area_unit,
                                   color_analysis=analysis_result['color_analysis'])

        primary_deficiency = diagnoses[0]

        if area_float > 0:
            chemical_dosage, organic_dosage, hectare_conversion = calculate_fertilizer_dosage(
                area_float, area_unit, primary_deficiency['fertilizer']
            )
        else:
            chemical_dosage   = None
            organic_dosage    = None
            hectare_conversion= 0

        return render_template('nutrition_result.html',
                               healthy            = False,
                               diagnoses          = diagnoses,
                               primary_deficiency = primary_deficiency,
                               image_url          = url_for('static', filename=f'uploads/{image_filename}'),
                               location           = location,
                               area               = area,
                               area_unit          = area_unit,
                               chemical_dosage    = chemical_dosage,
                               organic_dosage     = organic_dosage,
                               hectare_conversion = hectare_conversion,
                               color_analysis     = analysis_result['color_analysis'])

    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ ERROR IN NUTRITION ANALYSIS")
        logger.error("=" * 80)
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        flash("Unexpected error occurred during nutrition analysis.", "error")
        return render_template("error.html", back_link="/nutrition-testing"), 500


@app.route('/api/nutrition/<deficiency_key>')
def nutrition_api(deficiency_key):
    try:
        logger.info(f"Nutrition API called for: {deficiency_key}")

        if deficiency_key in nutrition_deficiency_data:
            return jsonify(nutrition_deficiency_data[deficiency_key])
        else:
            logger.warning(f"No nutrition info found for: {deficiency_key}")
            return jsonify({'error': 'Nutrition deficiency information not found'}), 404

    except Exception as e:
        logger.error(f"Nutrition API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate-fertilizer', methods=['POST'])
def calculate_fertilizer_api():
    try:
        data          = request.json
        deficiency_key= data.get('deficiency_key')
        area          = data.get('area')
        area_unit     = data.get('area_unit', 'hectare')

        if deficiency_key in nutrition_deficiency_data:
            deficiency_info = nutrition_deficiency_data[deficiency_key]

            chemical_dosage, organic_dosage, hectare_conversion = calculate_fertilizer_dosage(
                float(area), area_unit, deficiency_info['fertilizer']
            )

            return jsonify({
                'success'           : True,
                'chemical_dosage'   : chemical_dosage,
                'organic_dosage'    : organic_dosage,
                'hectare_conversion': hectare_conversion,
                'area'              : area,
                'area_unit'         : area_unit
            })
        else:
            return jsonify({'success': False, 'error': 'Deficiency information not found'}), 404

    except Exception as e:
        logger.error(f"Fertilizer calculation API error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


from datetime import datetime

gemini_status = startup_gemini_check()

# ============================================================
# CUSTOMER CENTER — Talk to Expert
# ============================================================
import sqlite3 as _sq3
from werkzeug.utils import secure_filename as _sfn

EXPERT_UPLOAD_DIR = os.path.join('static', 'expert_uploads')
os.makedirs(EXPERT_UPLOAD_DIR, exist_ok=True)


def migrate_expert_uploads():
    old_dir = 'uploads'
    if os.path.exists(old_dir):
        for fname in os.listdir(old_dir):
            old_path = os.path.join(old_dir, fname)
            new_path = os.path.join(EXPERT_UPLOAD_DIR, fname)
            if os.path.isfile(old_path) and not os.path.exists(new_path):
                import shutil as _sh
                _sh.copy2(old_path, new_path)
                logger.info(f"Migrated expert upload: {fname}")


migrate_expert_uploads()


def init_expert_db():
    conn = _sq3.connect("database.db")
    cur  = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS expert_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT, crop TEXT, description TEXT,
        image_path TEXT, audio_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reply TEXT
    )""")
    conn.commit()
    conn.close()


init_expert_db()


@app.route("/talk-to-expert")
def talk_to_expert():
    return render_template("talk_to_expert.html")


@app.route("/submit-expert", methods=["POST"])
def submit_expert():
    phone       = request.form.get("phone")
    crop        = request.form.get("crop")
    description = request.form.get("description")
    image       = request.files.get("image")
    audio       = request.files.get("audio")
    image_path, audio_path = "", ""
    if image and image.filename != "":
        fname      = str(uuid.uuid4()) + "_" + _sfn(image.filename)
        image_path = os.path.join(EXPERT_UPLOAD_DIR, fname)
        image.save(image_path)
    if audio and audio.filename != "":
        fname      = str(uuid.uuid4()) + "_" + _sfn(audio.filename)
        audio_path = os.path.join(EXPERT_UPLOAD_DIR, fname)
        audio.save(audio_path)
    conn = _sq3.connect("database.db")
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO expert_requests(phone,crop,description,image_path,audio_path) VALUES(?,?,?,?,?)",
        (phone, crop, description, image_path, audio_path)
    )
    conn.commit()
    conn.close()
    return redirect("/enter-phone")


@app.route("/enter-phone")
def enter_phone():
    return render_template("enter_phone.html")


@app.route("/check-requests", methods=["GET", "POST"])
def check_requests():
    rows  = []
    phone = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        if phone:
            conn = _sq3.connect("database.db")
            cur  = conn.cursor()
            cur.execute(
                "SELECT * FROM expert_requests WHERE phone=? ORDER BY created_at DESC", (phone,)
            )
            rows = cur.fetchall()
            conn.close()
    return render_template("check_requests.html", requests=rows, phone=phone)


@app.route("/farmer-dashboard", methods=["GET", "POST"])
def farmer_dashboard():
    rows  = []
    phone = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        if phone:
            conn = _sq3.connect("database.db")
            cur  = conn.cursor()
            cur.execute(
                "SELECT * FROM expert_requests WHERE phone=? ORDER BY created_at DESC", (phone,)
            )
            rows = cur.fetchall()
            conn.close()
    return render_template("farmer_dashboard.html", rows=rows, phone=phone)


EXPERT_ADMIN_USER = "admin"
EXPERT_ADMIN_PASS = "Agripal@123"


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form.get("username") == EXPERT_ADMIN_USER and
                request.form.get("password") == EXPERT_ADMIN_PASS):
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")


@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = _sq3.connect("database.db")
    cur  = conn.cursor()
    cur.execute("SELECT * FROM expert_requests ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("admin.html", rows=rows)


@app.route("/reply/<int:req_id>", methods=["POST"])
def expert_reply(req_id):
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = _sq3.connect("database.db")
    cur  = conn.cursor()
    cur.execute(
        "UPDATE expert_requests SET reply=? WHERE id=?",
        (request.form.get("reply"), req_id)
    )
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/logout")
def expert_logout():
    session.pop("admin", None)
    return redirect("/admin-login")

# ============================================================
# END CUSTOMER CENTER
# ============================================================


# ============================================================
# KISANAI CHATBOT — AgricultureChatbot class + /chat route
# ============================================================

class _AgriConfig:
    MYSQL_CONFIG = {
        'host'    : os.environ.get('MYSQL_HOST',     'localhost'),
        'user'    : os.environ.get('MYSQL_USER',     'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'pavan'),
        'database': os.environ.get('MYSQL_DATABASE', 'agriculture_llm'),
        'port'    : int(os.environ.get('MYSQL_PORT',  3306)),
    }

    VECTOR_DB_PATH = os.environ.get('CHROMA_PATH', str(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma_db')))

    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

    CHUNK_SIZE    = 800
    CHUNK_OVERLAP = 100
    MIN_CHUNK_SIZE= 200

    CROP_CATEGORIES = [
        'Rice', 'Wheat', 'Maize', 'Corn', 'Cotton', 'Sugarcane',
        'Tomato', 'Potato', 'Onion', 'Chilli', 'Brinjal',
        'Mango', 'Banana', 'Coconut', 'Tea', 'Coffee',
        'Groundnut', 'Soybean', 'Sunflower', 'Mustard',
        'Chickpea', 'Lentil', 'Pigeon Pea', 'Green Gram',
        'Barley', 'Jowar', 'Bajra', 'Ragi',
        'Turmeric', 'Ginger', 'Rubber',
        'Pulses', 'Vegetables', 'Fruits', 'Spices', 'Oilseeds',
    ]

    STATES = [
        'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Kerala',
        'Gujarat', 'Rajasthan', 'Punjab', 'Haryana',
        'Uttar Pradesh', 'Madhya Pradesh', 'Andhra Pradesh',
        'Telangana', 'West Bengal', 'Bihar', 'Odisha',
        'Chhattisgarh', 'Jharkhand', 'Assam', 'Himachal Pradesh',
        'Uttarakhand', 'Goa', 'Delhi',
    ]

    SEASONS = ['Kharif', 'Rabi', 'Zaid', 'Zayad', 'Summer', 'Winter', 'Monsoon', 'Perennial', 'Annual']

    TOP_K_DOCUMENTS   = 5
    SIMILARITY_THRESHOLD = 0.3
    MAX_CONTEXT_TOKENS= 8000

    INTENT_KEYWORDS = {
        'scheme'      : ['scheme', 'subsidy', 'yojana', 'benefit', 'government', 'pm-kisan', 'pmfby'],
        'market_price': ['price', 'mandi', 'market', 'rate', 'sell', 'buy', 'cost'],
        'disease'     : ['disease', 'pest', 'infection', 'treatment', 'cure', 'control', 'fungus'],
        'crop_guide'  : ['cultivation', 'farming', 'planting', 'sowing', 'harvest', 'grow'],
        'fertilizer'  : ['fertilizer', 'nutrient', 'soil', 'compost', 'npk', 'organic'],
        'weather'     : ['weather', 'rainfall', 'temperature', 'climate', 'forecast'],
    }


_agri_config = _AgriConfig()


class AgricultureChatbot:
    """KisanAI chatbot: combines MySQL queries + ChromaDB vector search."""

    def __init__(self):
        self.mysql_conn   = None
        self.mysql_cursor = None
        if MYSQL_AVAILABLE:
            try:
                self.mysql_conn   = _mysql.connect(**_agri_config.MYSQL_CONFIG)
                self.mysql_cursor = self.mysql_conn.cursor(dictionary=True)
                logger.info("✅ KisanAI: MySQL connected")
            except Exception as e:
                logger.warning(f"⚠️  KisanAI: MySQL not connected: {e}")

        self.collection = None
        if CHROMA_AVAILABLE:
            try:
                chroma_client   = _chromadb.PersistentClient(
                    path    = _agri_config.VECTOR_DB_PATH,
                    settings= _ChromaSettings(anonymized_telemetry=False)
                )
                self.collection = chroma_client.get_collection("agriculture_docs")
                logger.info("✅ KisanAI: Vector DB connected")
            except Exception as e:
                logger.warning(f"⚠️  KisanAI: Vector DB not ready: {e}")

        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info("📦 KisanAI: Loading embedding model...")
                self.embedding_model = _SentenceTransformer(_agri_config.EMBEDDING_MODEL)
                logger.info("✅ KisanAI: Embedding model loaded")
            except Exception as e:
                logger.warning(f"⚠️  KisanAI: Embedding model failed: {e}")

    def classify_query(self, query):
        q = query.lower()
        c = {
            'type': 'general',
            'needs_price': False, 'needs_weather': False,
            'needs_scheme': False, 'needs_production': False,
            'needs_pest': False, 'needs_docs': True
        }
        kw = _agri_config.INTENT_KEYWORDS
        if any(w in q for w in kw['market_price'] + ['msp', 'mandi']):
            c['type'] = 'price';    c['needs_price']      = True
        elif any(w in q for w in kw['weather'] + ['rain', 'monsoon']):
            c['type'] = 'weather';  c['needs_weather']    = True
        elif any(w in q for w in kw['scheme'] + ['loan']):
            c['type'] = 'scheme';   c['needs_scheme']     = True
        elif any(w in q for w in kw['crop_guide'] + ['production', 'yield', 'area']):
            c['type'] = 'production'; c['needs_production'] = True
        elif any(w in q for w in kw['disease'] + ['insect']):
            c['type'] = 'pest';     c['needs_pest']       = True
        return c

    def extract_entities(self, query):
        q        = query.lower()
        entities = {'crop': None, 'state': None, 'season': None}
        for crop in _agri_config.CROP_CATEGORIES:
            if crop.lower() in q:
                entities['crop'] = crop
                break
        for state in _agri_config.STATES:
            if state.lower() in q:
                entities['state'] = state
                break
        for season in _agri_config.SEASONS:
            if season.lower() in q:
                entities['season'] = season
                break
        return entities

    def _run_query(self, sql, params=()):
        if not self.mysql_cursor:
            return []
        try:
            if not self.mysql_conn.is_connected():
                self.mysql_conn.reconnect()
            self.mysql_cursor.execute(sql, params)
            return self.mysql_cursor.fetchall()
        except Exception as e:
            logger.error(f"KisanAI SQL error: {e}")
            return []

    def get_market_prices(self, crop=None, state=None):
        sql    = """SELECT DISTINCT crop_name, state, district, market, variety,
                        min_price, max_price, modal_price, msp, date
                 FROM market_prices WHERE 1=1"""
        params = []
        if crop:
            sql += " AND crop_name LIKE %s";  params.append(f"%{crop}%")
        if state:
            sql += " AND state LIKE %s";      params.append(f"%{state}%")
        sql += " ORDER BY date DESC LIMIT 10"
        return self._run_query(sql, params)

    def get_schemes(self, state=None):
        sql    = """SELECT DISTINCT scheme_name, scheme_type, state, description,
                        eligibility, benefits, application_process, contact_info
                 FROM government_schemes WHERE is_active = TRUE"""
        params = []
        if state:
            sql += " AND (state LIKE %s OR state = 'All India')";  params.append(f"%{state}%")
        sql += " LIMIT 5"
        return self._run_query(sql, params)

    def get_production_data(self, crop=None, state=None):
        sql    = """SELECT DISTINCT year, season, state, district, crop_name,
                        area_hectares, production_tonnes, yield_per_hectare
                 FROM crop_production WHERE 1=1"""
        params = []
        if crop:
            sql += " AND crop_name LIKE %s";  params.append(f"%{crop}%")
        if state:
            sql += " AND state LIKE %s";      params.append(f"%{state}%")
        sql += " ORDER BY year DESC LIMIT 10"
        return self._run_query(sql, params)

    def get_pest_info(self, query_text):
        sql  = """SELECT DISTINCT name, type, affected_crops, symptoms, causes,
                        prevention, treatment, severity, season
                 FROM pest_diseases WHERE name LIKE %s OR affected_crops LIKE %s LIMIT 5"""
        term = f"%{query_text}%"
        return self._run_query(sql, (term, term))

    def search_documents(self, query, n_results=3, filters=None):
        empty = {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
        if not self.collection or not self.embedding_model:
            return empty
        try:
            emb    = self.embedding_model.encode(query)
            kwargs = {'query_embeddings': [emb.tolist()], 'n_results': n_results}
            if filters:
                conditions = []
                if filters.get('crop'):
                    conditions.append({'crop': {'$eq': filters['crop']}})
                if filters.get('state'):
                    conditions.append({'state': {'$eq': filters['state']}})
                if len(conditions) == 1:
                    kwargs['where'] = conditions[0]
                elif len(conditions) > 1:
                    kwargs['where'] = {'$and': conditions}
            return self.collection.query(**kwargs)
        except Exception as e:
            logger.error(f"KisanAI vector search error: {e}")
            return empty

    def is_useful_chunk(self, text):
        t = text.strip()
        if len(t) < 80:
            return False
        words = _re.findall(r'[a-zA-Z]{3,}', t)
        if len(words) < 15:
            return False
        non_alpha = _re.sub(r'[a-zA-Z\s]', '', t)
        if len(non_alpha) > len(t) * 0.4:
            return False
        lines = [l.strip() for l in t.splitlines() if l.strip()]
        if len(lines) <= 3 and all(l.isupper() or len(l) < 40 for l in lines):
            return False
        if not _re.search(r'[a-zA-Z]{4,}.*[a-zA-Z]{4,}', t):
            return False
        return True

    def generate_response(self, query):
        start          = _time.time()
        classification = self.classify_query(query)
        entities       = self.extract_entities(query)

        response_data = {
            'query': query, 'classification': classification['type'],
            'entities': entities, 'sql_data': {}, 'documents': [], 'answer': ''
        }

        if classification['needs_price']:
            response_data['sql_data']['prices']     = self.get_market_prices(entities['crop'], entities['state'])
        if classification['needs_scheme']:
            response_data['sql_data']['schemes']    = self.get_schemes(entities['state'])
        if classification['needs_production']:
            response_data['sql_data']['production'] = self.get_production_data(entities['crop'], entities['state'])
        if classification['needs_pest']:
            response_data['sql_data']['pest_info']  = self.get_pest_info(query)

        if classification['needs_docs']:
            doc_filters  = {k: v for k, v in entities.items() if v}
            doc_results  = self.search_documents(query, n_results=5, filters=doc_filters or None)
            if doc_results['documents'][0]:
                clean_docs = []
                for doc, meta, dist in zip(
                    doc_results['documents'][0],
                    doc_results['metadatas'][0],
                    doc_results['distances'][0]
                ):
                    if self.is_useful_chunk(doc):
                        clean_docs.append({'text': doc, 'metadata': meta, 'relevance_score': 1 - dist})
                response_data['documents'] = clean_docs[:2]

        response_data['answer']           = self.format_answer(response_data, classification)
        response_data['response_time_ms'] = int((_time.time() - start) * 1000)
        self.log_query(query, classification['type'], entities, response_data['response_time_ms'])
        return response_data

    def format_answer(self, response_data, classification):
        parts = []

        if response_data['sql_data'].get('prices'):
            parts.append("📊 Market Prices:\n")
            for p in response_data['sql_data']['prices'][:5]:
                parts.append(
                    f"• {p['crop_name']} in {p['state']}, {p['district']}\n"
                    f"  Market: {p['market']}\n"
                    f"  Modal Price: ₹{p['modal_price']:.2f}/quintal\n"
                    f"  MSP: ₹{p['msp']:.2f}/quintal\n"
                    f"  Date: {p['date']}\n"
                )

        if response_data['sql_data'].get('schemes'):
            parts.append("\n🏛️ Government Schemes:\n")
            for s in response_data['sql_data']['schemes'][:3]:
                parts.append(
                    f"• {s['scheme_name']} ({s['scheme_type']})\n"
                    f"  {s['description']}\n"
                    f"  Eligibility: {s['eligibility']}\n"
                    f"  Benefits: {s['benefits']}\n"
                    f"  Apply: {s['application_process']}\n"
                    f"  Contact: {s['contact_info']}\n"
                )

        if response_data['sql_data'].get('production'):
            parts.append("\n🌾 Production Data:\n")
            for pr in response_data['sql_data']['production'][:5]:
                parts.append(
                    f"• {pr['crop_name']} ({pr['year']}, {pr['season']})\n"
                    f"  State: {pr['state']}, District: {pr['district']}\n"
                    f"  Area: {pr['area_hectares']:,.0f} hectares\n"
                    f"  Production: {pr['production_tonnes']:,.0f} tonnes\n"
                    f"  Yield: {pr['yield_per_hectare']:.2f} tonnes/hectare\n"
                )

        if response_data['sql_data'].get('pest_info'):
            parts.append("\n🐛 Pest / Disease Information:\n")
            for pest in response_data['sql_data']['pest_info'][:3]:
                parts.append(
                    f"• {pest['name']} ({pest['type']}, Severity: {pest['severity']})\n"
                    f"  Affects: {pest['affected_crops']}\n"
                    f"  Symptoms: {pest['symptoms']}\n"
                    f"  Prevention: {pest['prevention']}\n"
                    f"  Treatment: {pest['treatment']}\n"
                )

        has_sql = any(response_data['sql_data'].get(k) for k in ['prices', 'schemes', 'production', 'pest_info'])
        if response_data['documents'] and not has_sql:
            parts.append("\n📚 Related Agricultural Knowledge:\n")
            for i, doc in enumerate(response_data['documents'], 1):
                clean   = _re.sub(r'\n{3,}', '\n\n', doc['text']).strip()
                preview = clean[:350] + "…" if len(clean) > 350 else clean
                source  = doc['metadata'].get('source_file', 'Agricultural Document')
                parts.append(f"{i}. {preview}\n   Source: {source}\n")

        if not parts:
            parts.append(
                "I could not find specific data for your query. Try asking about:\n"
                "• Market prices for crops (e.g. rice price in Karnataka)\n"
                "• Government schemes (e.g. PM-KISAN)\n"
                "• Crop production data\n"
                "• Pest and disease management\n"
                "• Farming practices"
            )

        return "\n".join(parts)

    def log_query(self, query, query_type, entities, response_time_ms):
        if not self.mysql_cursor:
            return
        try:
            self.mysql_cursor.execute(
                "INSERT INTO user_queries (query_text, query_type, state, crop_name, response_time_ms) "
                "VALUES (%s, %s, %s, %s, %s)",
                (query, query_type, entities.get('state'), entities.get('crop'), response_time_ms)
            )
            self.mysql_conn.commit()
        except Exception as e:
            logger.error(f"KisanAI log_query error: {e}")

    def close(self):
        if self.mysql_cursor:
            self.mysql_cursor.close()
        if self.mysql_conn:
            self.mysql_conn.close()


agriculture_chatbot = AgricultureChatbot()
logger.info("✅ KisanAI AgricultureChatbot initialized")


@app.route('/chat', methods=['POST'])
def kisan_chat():
    """KisanAI chat endpoint — used by chatbot.html"""
    data  = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    try:
        response = agriculture_chatbot.generate_response(query)
        return jsonify(response)
    except Exception as e:
        logger.error(f"KisanAI /chat error: {e}")
        return jsonify({'error': str(e), 'answer': 'Sorry, something went wrong. Please try again.'}), 500

# ============================================================
# END KISANAI CHATBOT
# ============================================================


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n" + "=" * 80)
    logger.info("🛑 SHUTDOWN SIGNAL RECEIVED (Ctrl+C)")
    logger.info("=" * 80)
    logger.info("Cleaning up resources...")

    try:
        temp_files = ['detected_disease.json']
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.info(f"✅ Cleaned up: {temp_file}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

    logger.info("👋 AgriPal Server Stopped Successfully!")
    logger.info("=" * 80)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    from waitress import serve

    clear_sessions_on_startup()
    init_database()

    local_ip = get_local_ip()

    print("=" * 60)
    print("🌱 AGRIPAL - PRODUCTION SERVER STARTING")
    print("=" * 60)
    print(f"   Local:   http://127.0.0.1:5000")
    print(f"   Network: http://{local_ip}:5000")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)

    serve(
        app,
        host   = '0.0.0.0',
        port   = 5000,
        threads= 8
    )
