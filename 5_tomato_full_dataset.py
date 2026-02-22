"""
=============================================================
  🍅 TOMATO FULL DATASET — Agriculture Chatbot (MySQL)
=============================================================
  Complete tomato data covering:
    1.  Crop varieties & details
    2.  Market prices (multi-state, multi-season)
    3.  Production statistics (state & district level)
    4.  Weather impact data
    5.  Government schemes for tomato farmers
    6.  Pest & disease (10+ entries)
    7.  Farming practices (10+ entries)

  Run:
      python 2_setup_agriculture_db.py   # if not done yet
      python 5_tomato_full_dataset.py
=============================================================
"""

import mysql.connector
from mysql.connector import Error
import agri_config as config


# ══════════════════════════════════════════════════════════════
# 1. CROPS — Tomato varieties
# (crop_name, crop_type, botanical_name, category, season, duration_days, description)
# ══════════════════════════════════════════════════════════════
CROPS = [
    (
        'Tomato', 'Vegetable', 'Solanum lycopersicum', 'Vegetables', 'Rabi', 75,
        'Tomato is the most widely cultivated vegetable in India. It is a warm-season crop '
        'grown across all states. India is the 2nd largest producer globally after China. '
        'Used fresh, in processing (ketchup, puree, paste) and has high export value. '
        'Key growing states: Andhra Pradesh, Madhya Pradesh, Karnataka, Gujarat, Odisha, West Bengal.'
    ),
    (
        'Tomato - Pusa Ruby', 'Vegetable', 'Solanum lycopersicum cv. Pusa Ruby', 'Vegetables', 'Rabi', 70,
        'Popular open-pollinated variety by IARI. Medium-sized red fruits, 60-70g each. '
        'Suitable for fresh market. Duration 70 days. Yield 20-25 tonnes/ha. '
        'Tolerant to cracking. Good shelf life. Recommended for plains.'
    ),
    (
        'Tomato - Arka Vikas', 'Vegetable', 'Solanum lycopersicum cv. Arka Vikas', 'Vegetables', 'Kharif', 75,
        'Hybrid variety by IIHR Bengaluru. Indeterminate type. Large fruits 70-80g. '
        'Resistant to ToMV (Tomato Mosaic Virus). Yield 25-35 tonnes/ha. '
        'Good for processing and fresh market. Widely grown in South India.'
    ),
    (
        'Tomato - Arka Rakshak', 'Vegetable', 'Solanum lycopersicum cv. Arka Rakshak', 'Vegetables', 'Kharif', 80,
        'Triple disease resistant hybrid by IIHR. Resistant to ToMV, TLCV and bacterial wilt. '
        'Yield 18-20 kg/plant or 70-80 tonnes/ha. Firm fruits 75-80g. '
        'Long shelf life, suitable for distant markets. Premium price variety.'
    ),
    (
        'Tomato - Navodaya', 'Vegetable', 'Solanum lycopersicum cv. Navodaya', 'Vegetables', 'Rabi', 65,
        'Early maturing hybrid. Duration 65 days from transplanting. Yield 30-35 tonnes/ha. '
        'Round fruits 80-90g, attractive red color. Suitable for North India plains and hills.'
    ),
    (
        'Tomato - Sakthi', 'Vegetable', 'Solanum lycopersicum cv. Sakthi', 'Vegetables', 'Perennial', 70,
        'Popular hybrid in South India, especially Karnataka and Tamil Nadu. '
        'Heat-tolerant. Yield 35-40 tonnes/ha. Oval-shaped fruits 60-70g. '
        'Good for Kharif and summer season. Resistant to cracking.'
    ),
]


# ══════════════════════════════════════════════════════════════
# 2. MARKET PRICES — Tomato across states & seasons
# (date, state, district, market, crop_name, variety, min_price, max_price, modal_price, msp, unit)
# ══════════════════════════════════════════════════════════════
MARKET_PRICES = [

    # ── ANDHRA PRADESH ──
    ('2024-01-10', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid',  800, 1600, 1200, None, 'per quintal'),
    ('2024-01-15', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid',  900, 1800, 1400, None, 'per quintal'),
    ('2024-01-20', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid', 1000, 2000, 1500, None, 'per quintal'),
    ('2024-02-01', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid',  600,  900,  750, None, 'per quintal'),
    ('2024-02-15', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid',  400,  700,  550, None, 'per quintal'),
    ('2024-03-01', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid',  200,  500,  350, None, 'per quintal'),
    ('2024-04-01', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid',  500, 1000,  750, None, 'per quintal'),
    ('2024-05-15', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid', 2000, 4000, 3000, None, 'per quintal'),
    ('2024-06-01', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid', 4000, 8000, 6000, None, 'per quintal'),
    ('2024-07-01', 'Andhra Pradesh', 'Chittoor',    'APMC Madanapalle',   'Tomato', 'Local Hybrid', 6000,12000, 9000, None, 'per quintal'),
    ('2023-12-15', 'Andhra Pradesh', 'Krishna',     'APMC Vijayawada',    'Tomato', 'Navodaya',     1200, 2000, 1600, None, 'per quintal'),
    ('2024-01-15', 'Andhra Pradesh', 'Guntur',      'APMC Guntur',        'Tomato', 'Hybrid',       1000, 1800, 1400, None, 'per quintal'),

    # ── KARNATAKA ──
    ('2024-01-10', 'Karnataka',      'Kolar',       'APMC Kolar',         'Tomato', 'Sakthi Hybrid', 700, 1400, 1000, None, 'per quintal'),
    ('2024-01-15', 'Karnataka',      'Kolar',       'APMC Kolar',         'Tomato', 'Sakthi Hybrid', 900, 1600, 1200, None, 'per quintal'),
    ('2024-02-01', 'Karnataka',      'Kolar',       'APMC Kolar',         'Tomato', 'Sakthi Hybrid', 500,  900,  700, None, 'per quintal'),
    ('2024-03-15', 'Karnataka',      'Kolar',       'APMC Kolar',         'Tomato', 'Sakthi Hybrid', 300,  600,  450, None, 'per quintal'),
    ('2024-05-01', 'Karnataka',      'Kolar',       'APMC Kolar',         'Tomato', 'Sakthi Hybrid',1800, 3500, 2500, None, 'per quintal'),
    ('2024-06-15', 'Karnataka',      'Kolar',       'APMC Kolar',         'Tomato', 'Sakthi Hybrid',5000,10000, 7500, None, 'per quintal'),
    ('2024-01-15', 'Karnataka',      'Bangalore',   'APMC Bangalore',     'Tomato', 'Local',        1200, 2000, 1600, None, 'per quintal'),
    ('2024-01-15', 'Karnataka',      'Tumkur',      'APMC Tumkur',        'Tomato', 'Hybrid',        800, 1500, 1100, None, 'per quintal'),
    ('2024-01-15', 'Karnataka',      'Hassan',      'APMC Hassan',        'Tomato', 'Arka Vikas',    900, 1600, 1200, None, 'per quintal'),
    ('2024-01-15', 'Karnataka',      'Chikkaballapur','APMC Chikkaballapur','Tomato','Sakthi',      1000, 1700, 1350, None, 'per quintal'),

    # ── MAHARASHTRA ──
    ('2024-01-10', 'Maharashtra',    'Nashik',      'APMC Lasalgaon',     'Tomato', 'Hybrid',       1000, 2000, 1500, None, 'per quintal'),
    ('2024-01-15', 'Maharashtra',    'Nashik',      'APMC Nashik',        'Tomato', 'Hybrid',       1200, 2200, 1700, None, 'per quintal'),
    ('2024-02-01', 'Maharashtra',    'Nashik',      'APMC Nashik',        'Tomato', 'Hybrid',        600, 1000,  800, None, 'per quintal'),
    ('2024-03-01', 'Maharashtra',    'Nashik',      'APMC Nashik',        'Tomato', 'Hybrid',        400,  700,  550, None, 'per quintal'),
    ('2024-06-01', 'Maharashtra',    'Nashik',      'APMC Nashik',        'Tomato', 'Hybrid',       3000, 6000, 4500, None, 'per quintal'),
    ('2024-01-15', 'Maharashtra',    'Pune',        'APMC Pune',          'Tomato', 'Local',        1500, 2500, 2000, None, 'per quintal'),
    ('2024-01-15', 'Maharashtra',    'Satara',      'APMC Satara',        'Tomato', 'Pusa Ruby',     900, 1600, 1200, None, 'per quintal'),
    ('2024-01-15', 'Maharashtra',    'Kolhapur',    'APMC Kolhapur',      'Tomato', 'Hybrid',       1100, 1800, 1450, None, 'per quintal'),

    # ── MADHYA PRADESH ──
    ('2024-01-15', 'Madhya Pradesh', 'Rewa',        'APMC Rewa',          'Tomato', 'Hybrid',        800, 1400, 1100, None, 'per quintal'),
    ('2024-01-15', 'Madhya Pradesh', 'Shahdol',     'APMC Shahdol',       'Tomato', 'Local',         600, 1200,  900, None, 'per quintal'),
    ('2024-01-15', 'Madhya Pradesh', 'Chhindwara',  'APMC Chhindwara',    'Tomato', 'Hybrid',        700, 1300, 1000, None, 'per quintal'),
    ('2024-06-01', 'Madhya Pradesh', 'Rewa',        'APMC Rewa',          'Tomato', 'Hybrid',       4000, 8000, 6000, None, 'per quintal'),

    # ── GUJARAT ──
    ('2024-01-15', 'Gujarat',        'Surat',       'APMC Surat',         'Tomato', 'Hybrid',       1400, 2400, 1900, None, 'per quintal'),
    ('2024-01-15', 'Gujarat',        'Vadodara',    'APMC Vadodara',      'Tomato', 'Local',        1200, 2000, 1600, None, 'per quintal'),
    ('2024-01-15', 'Gujarat',        'Anand',       'APMC Anand',         'Tomato', 'Hybrid',       1300, 2200, 1750, None, 'per quintal'),

    # ── TAMIL NADU ──
    ('2024-01-15', 'Tamil Nadu',     'Dharmapuri',  'APMC Dharmapuri',    'Tomato', 'Local Hybrid',  900, 1700, 1300, None, 'per quintal'),
    ('2024-01-15', 'Tamil Nadu',     'Salem',       'APMC Salem',         'Tomato', 'Hybrid',       1000, 1800, 1400, None, 'per quintal'),
    ('2024-01-15', 'Tamil Nadu',     'Krishnagiri', 'APMC Krishnagiri',   'Tomato', 'Arka Vikas',   1100, 1900, 1500, None, 'per quintal'),
    ('2024-06-01', 'Tamil Nadu',     'Dharmapuri',  'APMC Dharmapuri',    'Tomato', 'Local Hybrid', 5000, 9000, 7000, None, 'per quintal'),

    # ── UTTAR PRADESH ──
    ('2024-01-15', 'Uttar Pradesh',  'Varanasi',    'APMC Varanasi',      'Tomato', 'Hybrid',       1200, 2200, 1700, None, 'per quintal'),
    ('2024-01-15', 'Uttar Pradesh',  'Lucknow',     'APMC Lucknow',       'Tomato', 'Local',        1500, 2500, 2000, None, 'per quintal'),
    ('2024-01-15', 'Uttar Pradesh',  'Agra',        'APMC Agra',          'Tomato', 'Hybrid',       1300, 2300, 1800, None, 'per quintal'),

    # ── HIMACHAL PRADESH (hill tomatoes — premium) ──
    ('2024-07-15', 'Himachal Pradesh','Shimla',     'APMC Shimla',        'Tomato', 'Hill Tomato',  2000, 4000, 3000, None, 'per quintal'),
    ('2024-08-01', 'Himachal Pradesh','Solan',      'APMC Solan',         'Tomato', 'Hill Hybrid',  1800, 3500, 2700, None, 'per quintal'),

    # ── WEST BENGAL ──
    ('2024-01-15', 'West Bengal',    'Hooghly',     'APMC Hooghly',       'Tomato', 'Local',        1000, 1800, 1400, None, 'per quintal'),
    ('2024-01-15', 'West Bengal',    'Nadia',       'APMC Nadia',         'Tomato', 'Hybrid',        900, 1700, 1300, None, 'per quintal'),

    # ── ODISHA ──
    ('2024-01-15', 'Odisha',         'Cuttack',     'APMC Cuttack',       'Tomato', 'Local Hybrid',  700, 1300, 1000, None, 'per quintal'),
    ('2024-01-15', 'Odisha',         'Bhubaneswar', 'APMC Bhubaneswar',   'Tomato', 'Hybrid',        800, 1500, 1150, None, 'per quintal'),
]


# ══════════════════════════════════════════════════════════════
# 3. CROP PRODUCTION — Tomato state & district level
# (year, season, state, district, crop_name, area_ha, production_tonnes, yield_t_per_ha)
# ══════════════════════════════════════════════════════════════
CROP_PRODUCTION = [
    # Andhra Pradesh — largest producer
    ('2023-24', 'Rabi',   'Andhra Pradesh', 'Chittoor',      'Tomato', 42000, 1764000, 42.0),
    ('2023-24', 'Kharif', 'Andhra Pradesh', 'Chittoor',      'Tomato', 18000,  630000, 35.0),
    ('2023-24', 'Rabi',   'Andhra Pradesh', 'Krishna',       'Tomato', 15000,  525000, 35.0),
    ('2023-24', 'Rabi',   'Andhra Pradesh', 'Guntur',        'Tomato', 12000,  384000, 32.0),
    ('2023-24', 'Rabi',   'Andhra Pradesh', 'West Godavari', 'Tomato',  8000,  240000, 30.0),
    # Karnataka
    ('2023-24', 'Rabi',   'Karnataka',      'Kolar',         'Tomato', 18000,  720000, 40.0),
    ('2023-24', 'Kharif', 'Karnataka',      'Kolar',         'Tomato',  8000,  280000, 35.0),
    ('2023-24', 'Rabi',   'Karnataka',      'Chikkaballapur','Tomato', 12000,  420000, 35.0),
    ('2023-24', 'Rabi',   'Karnataka',      'Tumkur',        'Tomato',  6000,  180000, 30.0),
    ('2023-24', 'Rabi',   'Karnataka',      'Hassan',        'Tomato',  5000,  160000, 32.0),
    # Madhya Pradesh
    ('2023-24', 'Rabi',   'Madhya Pradesh', 'Rewa',          'Tomato', 22000,  660000, 30.0),
    ('2023-24', 'Rabi',   'Madhya Pradesh', 'Shahdol',       'Tomato', 14000,  392000, 28.0),
    ('2023-24', 'Rabi',   'Madhya Pradesh', 'Chhindwara',    'Tomato', 10000,  300000, 30.0),
    # Maharashtra
    ('2023-24', 'Rabi',   'Maharashtra',    'Nashik',        'Tomato', 16000,  480000, 30.0),
    ('2023-24', 'Rabi',   'Maharashtra',    'Pune',          'Tomato',  9000,  252000, 28.0),
    ('2023-24', 'Kharif', 'Maharashtra',    'Satara',        'Tomato',  5000,  150000, 30.0),
    # Gujarat
    ('2023-24', 'Rabi',   'Gujarat',        'Surat',         'Tomato',  8000,  224000, 28.0),
    ('2023-24', 'Rabi',   'Gujarat',        'Vadodara',      'Tomato',  6000,  168000, 28.0),
    # Tamil Nadu
    ('2023-24', 'Rabi',   'Tamil Nadu',     'Dharmapuri',    'Tomato', 14000,  448000, 32.0),
    ('2023-24', 'Kharif', 'Tamil Nadu',     'Salem',         'Tomato',  6000,  180000, 30.0),
    # Uttar Pradesh
    ('2023-24', 'Rabi',   'Uttar Pradesh',  'Varanasi',      'Tomato', 10000,  250000, 25.0),
    ('2023-24', 'Rabi',   'Uttar Pradesh',  'Lucknow',       'Tomato',  7000,  175000, 25.0),
    # Himachal Pradesh
    ('2023-24', 'Kharif', 'Himachal Pradesh','Shimla',       'Tomato',  8000,  280000, 35.0),
    ('2023-24', 'Kharif', 'Himachal Pradesh','Solan',        'Tomato',  5000,  175000, 35.0),
    # West Bengal
    ('2023-24', 'Rabi',   'West Bengal',    'Hooghly',       'Tomato', 12000,  300000, 25.0),
    # Odisha
    ('2023-24', 'Rabi',   'Odisha',         'Cuttack',       'Tomato',  8000,  192000, 24.0),
]


# ══════════════════════════════════════════════════════════════
# 4. WEATHER DATA — Key tomato growing districts
# (date, state, district, rainfall_mm, temp_min, temp_max, humidity_%, wind_kmh, conditions)
# ══════════════════════════════════════════════════════════════
WEATHER_DATA = [
    # Chittoor (AP) — key tomato hub
    ('2024-01-15', 'Andhra Pradesh', 'Chittoor',     0.0, 14.0, 28.0, 55.0,  8.0, 'Clear — ideal tomato weather'),
    ('2024-02-15', 'Andhra Pradesh', 'Chittoor',     0.0, 16.0, 31.0, 48.0, 10.0, 'Sunny — slight heat stress risk'),
    ('2024-03-15', 'Andhra Pradesh', 'Chittoor',     5.0, 20.0, 35.0, 52.0, 12.0, 'Hot — fruit cracking risk'),
    ('2024-06-15', 'Andhra Pradesh', 'Chittoor',    85.0, 24.0, 30.0, 88.0, 22.0, 'Heavy Rain — blight risk HIGH'),
    ('2023-11-15', 'Andhra Pradesh', 'Chittoor',     2.0, 18.0, 29.0, 60.0,  9.0, 'Partly Cloudy — good for planting'),
    # Kolar (Karnataka)
    ('2024-01-15', 'Karnataka',      'Kolar',         0.0, 15.0, 27.0, 52.0,  7.0, 'Clear — ideal for Rabi tomato'),
    ('2024-02-15', 'Karnataka',      'Kolar',         0.0, 17.0, 30.0, 46.0,  9.0, 'Sunny — good fruit setting'),
    ('2024-05-15', 'Karnataka',      'Kolar',        30.0, 21.0, 28.0, 78.0, 16.0, 'Pre-monsoon showers — fungal alert'),
    ('2024-06-15', 'Karnataka',      'Kolar',        75.0, 20.0, 26.0, 90.0, 20.0, 'Heavy Rain — late blight risk'),
    # Nashik (Maharashtra)
    ('2024-01-15', 'Maharashtra',    'Nashik',        0.0, 10.0, 26.0, 48.0,  6.0, 'Cool clear — ideal Rabi tomato'),
    ('2024-02-15', 'Maharashtra',    'Nashik',        0.0, 12.0, 29.0, 44.0,  8.0, 'Warm sunny — good fruit development'),
    ('2024-07-15', 'Maharashtra',    'Nashik',       95.0, 19.0, 25.0, 92.0, 25.0, 'Very Heavy Rain — crop damage risk'),
    # Rewa (MP)
    ('2024-01-15', 'Madhya Pradesh', 'Rewa',          0.0,  8.0, 24.0, 50.0,  7.0, 'Cool clear — good for Rabi tomato'),
    ('2024-02-15', 'Madhya Pradesh', 'Rewa',          0.0, 10.0, 28.0, 45.0,  9.0, 'Warm sunny'),
    # Shimla (HP) — summer tomato
    ('2024-07-15', 'Himachal Pradesh','Shimla',       45.0, 12.0, 20.0, 82.0, 15.0, 'Monsoon rain — good for hill tomato'),
    ('2024-08-15', 'Himachal Pradesh','Shimla',       60.0, 11.0, 19.0, 85.0, 18.0, 'Heavy Rain — monitor for blight'),
]


# ══════════════════════════════════════════════════════════════
# 5. GOVERNMENT SCHEMES — Tomato & horticulture specific
# ══════════════════════════════════════════════════════════════
GOVERNMENT_SCHEMES = [
    (
        'PM Kisan Sampada Yojana (PMKSY) - Tomato Processing',
        'Processing & Value Addition', 'All India', '2017-05-31', None,
        60000, None,
        'Scheme for mega food parks, cold chain, agro-processing clusters and food processing units. '
        'Helps tomato farmers reduce post-harvest losses (currently 25-30%) by supporting cold storage, '
        'primary processing and transportation infrastructure.',
        'Farmer Producer Organizations (FPOs), cooperatives, agri-entrepreneurs, state govt agencies.',
        'Capital subsidy up to Rs. 50 lakhs for cold chain; up to 50% subsidy for food processing units. '
        'Reduces tomato wastage. Enables processing into ketchup, puree, paste during glut periods.',
        'Apply through Ministry of Food Processing Industries portal: mofpi.gov.in',
        '1800-111-175 | mofpi@gov.in',
        True
    ),
    (
        'Pradhan Mantri Krishi Sinchayee Yojana - Drip for Horticulture',
        'Irrigation Subsidy', 'All India', '2015-07-01', None,
        50000, None,
        'Subsidy on drip irrigation specifically beneficial for tomato crop. Drip reduces water usage '
        'by 40-50% and increases tomato yield by 20-30% through precise water and nutrient delivery.',
        'All tomato/vegetable farmers. Subsidy: 55% for small/marginal, 45% for others.',
        'Up to 55% subsidy on drip system cost. Average saving Rs. 15,000-20,000/acre on drip installation. '
        'Payback period reduces to 1-2 years for tomato growers.',
        'Apply through state horticulture department or pmksy.gov.in.',
        '1800-180-1551',
        True
    ),
    (
        'National Horticulture Mission (NHM) - Tomato',
        'Production Support', 'All India', '2005-05-01', None,
        None, None,
        'Provides financial assistance for quality planting material, protected cultivation, '
        'post-harvest management and market development for tomato and other horticultural crops.',
        'Individual farmers, FPOs, cooperatives growing tomato commercially.',
        '50% subsidy on hybrid seed cost. 50% subsidy on plastic mulch. Assistance for poly-house/net-house. '
        'Support for grading and packing facilities. Market linkage support.',
        'Apply through district horticulture officer.',
        'State Horticulture Department / NHB',
        True
    ),
    (
        'e-NAM (National Agriculture Market) - Tomato',
        'Market Linkage', 'All India', '2016-04-14', None,
        None, None,
        'Online trading platform connecting 1000+ APMCs. Tomato farmers can access better prices '
        'by reaching buyers across India. Reduces dependence on local traders. '
        'Real-time price discovery and online payment.',
        'All tomato farmers who are registered in their local APMC.',
        'Access to national buyer base. Transparent price discovery. Online payment within 24 hours. '
        'Reduced market fees in integrated mandis.',
        'Register at enam.gov.in or visit your APMC mandi with Aadhaar and bank details.',
        '1800-270-0224 | nam@sfac.in',
        True
    ),
    (
        'Tomato Grand Challenge — Price Stabilization Fund',
        'Price Support', 'All India', '2019-01-01', None,
        None, None,
        'Government intervention to stabilize tomato prices during sharp price crashes. '
        'NAFED procures tomatoes at reasonable prices during glut and distributes in deficit areas. '
        'Activated when prices fall below Rs. 600/quintal for sustained periods.',
        'All tomato farmers registered with APMC.',
        'Minimum procurement support during price crash. Market intervention prevents distress sales. '
        'Subsidized tomato supplied to consumers in cities during price spikes.',
        'Automatic — no registration needed. Procurement happens through APMC.',
        'NAFED Helpline: 1800-103-7700',
        True
    ),
    (
        'Andhra Pradesh - YSR Rythu Bharosa',
        'Direct Benefit Transfer', 'Andhra Pradesh', '2019-10-15', None,
        7000, 60,
        'AP state scheme providing Rs. 13,500/year per acre to farmers including tomato growers. '
        'Covers input cost for seeds, fertilizers and pesticides. '
        'Distributed in two installments per year.',
        'All farmers with agriculture land in Andhra Pradesh, including tenant farmers.',
        'Rs. 13,500 per year per acre. For tenant farmers: Rs. 13,500/year per year. '
        'Input subsidy for seeds and fertilizers.',
        'Register at sachivalayam or ap.gov.in/rytu-bharosa. Aadhaar linked bank account required.',
        '1902 | apagrisnet@ap.gov.in',
        True
    ),
    (
        'Karnataka - Tomato Crop Loss Compensation',
        'Disaster Relief', 'Karnataka', '2020-01-01', None,
        500, None,
        'Special compensation for Karnataka tomato farmers affected by sudden price crash (below cost of production) '
        'or natural calamity like unseasonal rains, hailstorm or pest outbreak causing more than 50% crop loss.',
        'Karnataka tomato farmers with crop loss above 50% due to natural calamity or price below Rs. 400/quintal.',
        'Compensation Rs. 5,000 per acre for price crash; Rs. 8,000-12,000/acre for natural calamity. '
        'One-time payment per crop season.',
        'Apply through village accountant (VA) within 30 days of crop loss with girdawari report.',
        '080-22253924 | Karnataka Agriculture Department',
        True
    ),
]


# ══════════════════════════════════════════════════════════════
# 6. PEST & DISEASES — Tomato specific (comprehensive)
# (name, type, affected_crops, symptoms, causes, prevention, treatment, severity, season)
# ══════════════════════════════════════════════════════════════
PEST_DISEASES = [
    (
        'Tomato Late Blight (Phytophthora)',
        'Disease', 'Tomato, Potato',
        'Dark brown-black water-soaked lesions on leaves and stems. White fluffy fungal growth on underside '
        'of leaves in humid conditions. Fruits show firm dark brown rot. Entire field can collapse within 7-10 days.',
        'Oomycete Phytophthora infestans. Thrives at 10-20°C with >90% humidity. Spores spread by wind and rain splash. '
        'Severe during monsoon, post-monsoon fog, or winter with heavy dew.',
        'Use resistant varieties (Arka Rakshak). Avoid overhead irrigation. Proper spacing for air circulation. '
        'Remove volunteer tomato plants. Apply preventive fungicide before monsoon.',
        'Mancozeb 75% WP @ 2.5g/L OR Cymoxanil 8% + Mancozeb 64% WDG @ 3g/L. '
        'For severe cases: Metalaxyl 8% + Mancozeb 64% WP @ 3g/L. Spray every 7 days during wet weather.',
        'Very High', 'Kharif'
    ),
    (
        'Tomato Early Blight (Alternaria)',
        'Disease', 'Tomato',
        'Circular dark brown spots with concentric rings (target board pattern) on older leaves. '
        'Yellow halo around spots. Severe defoliation. Stem canker at soil level. Fruit rot near stem end.',
        'Fungus Alternaria solani. Favoured by alternating wet and dry conditions, 24-29°C, '
        'poor plant nutrition especially nitrogen deficiency. Spreads by wind, rain and tools.',
        'Use disease-free transplants. Avoid wetting foliage. Balanced fertilization. '
        'Remove infected leaves and burn. Crop rotation (3 years away from tomato/potato).',
        'Mancozeb 75% WP @ 2g/L or Iprodione 50% WP @ 2g/L. '
        'Spray at first sign and repeat every 10 days. Add sticker. 3-4 sprays needed.',
        'High', 'Kharif'
    ),
    (
        'Tomato Leaf Curl Virus (ToLCV / TLCV)',
        'Disease', 'Tomato',
        'Severe upward curling and crinkling of leaves. Stunted plant growth. Reduced leaf size. '
        'Yellow-green mottling. Very low or zero fruit set. Infected plants remain unproductive. '
        'Characteristic yellow margin on leaf edges.',
        'Caused by Tomato Leaf Curl Virus (begomovirus group) transmitted by whitefly Bemisia tabaci. '
        'Whitefly populations explode in dry hot weather (30-35°C). Virus spreads from infected nearby crops.',
        'Grow TLCV-resistant varieties (Arka Rakshak, Arka Meghali). Install 40-mesh insect-proof net in nursery. '
        'Use silver/reflective mulch to repel whitefly. Rogue out infected plants immediately.',
        'Control vector whitefly: Imidacloprid 17.8% SL @ 0.5ml/L OR Thiamethoxam 25% WG @ 0.3g/L. '
        'No direct cure — prevention is only solution. Spray systemic insecticide on nursery before transplanting.',
        'Very High', 'Kharif'
    ),
    (
        'Tomato Mosaic Virus (ToMV)',
        'Disease', 'Tomato, Bell Pepper',
        'Yellow-green mosaic or mottling on leaves. Leaf distortion and fern-like appearance (fernleaf). '
        'Stunted plants, reduced fruit size. Necrotic streaks on fruits. Internal browning of fruit.',
        'Tobamovirus transmitted by contact (tools, hands, clothes). Seed-borne. Spreads rapidly in dense nurseries. '
        'Survives in soil and plant debris for months. Tobacco users can transmit through hands.',
        'Use ToMV-resistant varieties (Arka Vikas). Soak seeds in 10% TSP or hot water 52°C for 30 min. '
        'Dip hands in milk before handling plants. Sterilize tools. No tobacco use near crop.',
        'No cure. Remove and destroy infected plants. Apply neem oil 5ml/L to slow spread. '
        'Use resistant varieties in subsequent seasons.',
        'High', 'Kharif'
    ),
    (
        'Bacterial Wilt (Ralstonia)',
        'Disease', 'Tomato, Brinjal, Pepper, Potato',
        'Sudden wilting of entire plant in midday heat, recovering at night initially, then permanent wilt. '
        'No leaf yellowing before wilting. Brown discoloration of vascular tissue. '
        'When cut stem dipped in water — milky bacterial ooze is released (diagnostic test).',
        'Soil-borne bacteria Ralstonia solanacearum. Enters through roots, wounds. '
        'Favoured by 25-35°C, high soil moisture, sandy loam soils. Persists in soil for 3-6 years.',
        'Use resistant rootstocks (graft tomato on resistant brinjal rootstock). '
        'Long rotation (3-4 years) with non-solanaceous crops. Avoid waterlogging. '
        'Drench soil with Copper Oxychloride 3g/L before planting.',
        'No effective chemical cure once infected. Remove and destroy plants with roots. '
        'Soil drench with Streptocycline 0.5g + Copper Oxychloride 3g/L as preventive. '
        'Bio-control: drench with Pseudomonas fluorescens @ 10g/L soil application.',
        'Very High', 'Kharif'
    ),
    (
        'Fusarium Wilt (Fusarium oxysporum)',
        'Disease', 'Tomato',
        'Lower leaves turn yellow, wilt on one side of plant initially. Brown vascular discoloration. '
        'Plant slowly dies over 2-4 weeks. Root system turns brown and rotten. '
        'Differs from bacterial wilt: slower progression, affects one branch first.',
        'Soil-borne fungus Fusarium oxysporum f.sp. lycopersici. Enters through roots. '
        'Favoured by 25-28°C, acidic soils. Persists in soil for years. Spreads via infected transplants.',
        'Grow resistant/tolerant varieties. Soil solarization (6 weeks pre-planting). '
        'Maintain soil pH above 6.5 with lime. Seed treatment with Trichoderma viride 4g/kg.',
        'Soil drench with Carbendazim 2g/L or Thiophanate Methyl 2g/L. '
        'Bio-agent: Trichoderma viride @ 5g/kg soil mixed near root zone. '
        'Metalaxyl 35% WS seed treatment.',
        'High', 'Kharif'
    ),
    (
        'Tomato Fruit Borer (Helicoverpa armigera)',
        'Pest', 'Tomato, Chickpea, Cotton, Maize',
        'Round holes on fruits with frass (excrement) at entry point. Larva feeds inside fruit. '
        'One larva can damage 3-4 fruits. Damaged fruits rot due to secondary infection. '
        'Green caterpillars with yellow stripes, 3-4cm long when mature.',
        'Polyphagous moth pest. Females lay eggs singly on tender plant parts. '
        'Peak attack during fruiting stage. High population in October-December and March-May. '
        'Favoured by warm dry conditions after monsoon.',
        'Install pheromone traps @ 5/acre (Helilure). Plant African marigold as border trap crop (1 row per 14 rows tomato). '
        'Release Trichogramma chilonis eggs @ 1.5 lakh/ha. NPV (Nuclear Polyhedrosis Virus) spray.',
        'Spinosad 45% SC @ 0.3ml/L OR Emamectin Benzoate 5% SG @ 0.4g/L OR Chlorantraniliprole 18.5% SC @ 0.4ml/L. '
        'Spray at petal fall and repeat at 10-day intervals. Do not spray same chemical more than 2 times.',
        'High', 'Kharif'
    ),
    (
        'Whitefly (Bemisia tabaci) on Tomato',
        'Pest', 'Tomato, Cotton, Vegetables',
        'Tiny white insects on underside of leaves. Yellowing and curling of leaves (direct damage). '
        'Black sooty mould on honeydew secretion. Most importantly: transmits Tomato Leaf Curl Virus. '
        'Population can multiply 10x within 1 week in hot dry weather.',
        'Sucking pest with rapid reproduction. Thrives at 30-35°C, low humidity. '
        'Migrates from nearby crops. Spreads within crop rapidly.',
        'Silver/reflective plastic mulch on beds repels whitefly. Yellow sticky traps @ 10/acre. '
        'Install 40-mesh net for nursery. Avoid planting near cotton or other whitefly-prone crops.',
        'Imidacloprid 17.8% SL @ 0.5ml/L OR Diafenthiuron 50% WP @ 1g/L. '
        'Spiromesifen 22.9% SC @ 1ml/L is effective against resistant populations. '
        'Spray on underside of leaves. Rotate insecticides to avoid resistance.',
        'Very High', 'Kharif'
    ),
    (
        'Aphids on Tomato',
        'Pest', 'Tomato, Pepper, Vegetables',
        'Clusters of small green/black insects on tender shoots and underside of young leaves. '
        'Leaf curling and distortion. Sticky honeydew attracting ants. Black sooty mould. '
        'Transmits Cucumber Mosaic Virus (CMV). Plant growth stunted.',
        'Soft-bodied sucking pests. Reproduce rapidly in cool dry weather (18-25°C). '
        'Natural enemies (ladybird beetles, lacewings) keep them in check. '
        'High nitrogen use promotes succulent tissue preferred by aphids.',
        'Encourage natural enemies. Avoid excess nitrogen fertilizer. '
        'Yellow sticky traps. Spray water jet to dislodge colonies. Reflective mulch.',
        'Dimethoate 30% EC @ 2ml/L OR Imidacloprid 17.8% SL @ 0.5ml/L. '
        'Soap solution (5g/L) effective for mild attacks. '
        'Spray when > 20 aphids per plant or on young growth.',
        'Medium', 'Rabi'
    ),
    (
        'Spider Mite (Tetranychus urticae) on Tomato',
        'Pest', 'Tomato, Brinjal, Beans, Cucumber',
        'Tiny reddish or yellowish mites on underside of leaves. Silvery stippling on upper leaf surface. '
        'Fine webbing covering leaves and shoots. Leaves turn bronzed, dry and fall. '
        'Severe attack causes complete defoliation and plant death. Visible with hand lens.',
        'Hot dry weather (>30°C, <40% humidity) triggers population explosion. '
        'Often worsened after broad-spectrum insecticide use that kills natural enemies. '
        'Spreads rapidly in dry summer conditions.',
        'Maintain adequate soil moisture. Avoid water stress. '
        'Introduce predatory mite Phytoseiulus persimilis. Avoid excess broad-spectrum insecticides.',
        'Spiromesifen 22.9% SC @ 1ml/L OR Abamectin 1.9% EC @ 1ml/L OR Fenazaquin 10% EC @ 2ml/L. '
        'Cover underside of leaves thoroughly. Repeat after 7 days. '
        'Wettable sulphur 80% WP @ 3g/L as preventive/mild infestation.',
        'High', 'Kharif'
    ),
    (
        'Damping Off (Pythium/Rhizoctonia) in Tomato Nursery',
        'Disease', 'Tomato Seedlings',
        'Young seedlings collapse and die at soil level. Stem turns water-soaked and shrivels at base. '
        'Seedlings appear healthy then suddenly fall over. Entire nursery patches can be wiped out. '
        'Post-emergence damping off most common in tomato nursery.',
        'Soil-borne fungi Pythium aphanidermatum or Rhizoctonia solani. '
        'Favoured by overwatering, poorly drained nursery beds, high humidity, dense sowing. '
        'Temperature 25-30°C with wet soil ideal for pathogen spread.',
        'Sterilize nursery soil (solarization or steam). Avoid waterlogging, ensure bed drainage. '
        'Do not over-sow. Treat seeds with Thiram 3g/kg or Trichoderma 4g/kg before sowing.',
        'Drench nursery with Copper Oxychloride 3g/L or Metalaxyl 8% + Mancozeb 64% @ 2g/L. '
        'Bio-agent: Trichoderma harzianum @ 10g/sq meter in nursery soil. '
        'Remove and destroy affected seedlings immediately.',
        'High', 'Kharif'
    ),
    (
        'Tomato Fruit Cracking',
        'Physiological Disorder', 'Tomato',
        'Concentric or radial cracks on fruit surface. Cracks allow secondary fungal/bacterial infection. '
        'Reduces marketability and shelf life. Cracked fruits cannot be transported long distance.',
        'Irregular water supply — dry spell followed by heavy rain or irrigation. '
        'Boron deficiency. High temperatures during fruit development. '
        'Varieties with thin skin more susceptible.',
        'Maintain uniform soil moisture through drip irrigation or mulching. '
        'Grow crack-resistant varieties (Pusa Ruby, Arka Meghali). Maintain proper calcium and boron levels.',
        'No direct pesticide treatment. Preventive measures: '
        'Spray Calcium Nitrate 1% + Borax 0.2% at fruiting stage. '
        'Apply mulch to maintain soil moisture. Harvest before full ripening.',
        'Medium', 'All'
    ),
    (
        'Blossom End Rot (BER) in Tomato',
        'Physiological Disorder', 'Tomato, Pepper',
        'Dark, sunken, leathery rot at blossom end (bottom) of fruit. Starts as water-soaked spot, '
        'turns dark brown to black. Affects 20-50% fruits in severe cases. '
        'Affected area is dry and leathery (unlike fungal rots which are wet).',
        'Calcium deficiency in developing fruit — caused by irregular watering, root damage, '
        'excess ammonium fertilizer, or high salinity in soil. Not caused by pathogen.',
        'Maintain uniform soil moisture (critical). Avoid over-fertilization with nitrogen. '
        'Ensure calcium in soil (lime application). Do not damage roots during cultivation.',
        'Foliar spray of Calcium Chloride 0.5% (5g/L) every 10 days during fruiting. '
        'Maintain consistent drip irrigation. Correct soil pH to 6.0-6.8 for better Ca uptake.',
        'Medium', 'All'
    ),
]


# ══════════════════════════════════════════════════════════════
# 7. FARMING PRACTICES — Tomato specific (comprehensive)
# (practice_name, category, crop_name, description, benefits, implementation, cost_per_acre, success_rate, states)
# ══════════════════════════════════════════════════════════════
FARMING_PRACTICES = [
    (
        'Tomato Nursery Raising — Pro Tray Method',
        'Nursery Management', 'Tomato',
        'Raise tomato seedlings in 98-cell or 128-cell pro-trays using coco peat + perlite + vermiculite (3:1:1) '
        'mix under net house / poly-tunnel. Produces uniform, healthy, virus-free transplants in 25-30 days.',
        '95%+ germination vs 60-70% in open nursery. Virus-free seedlings (no soil contact). '
        'Uniform crop, easier gap filling. Saves 40% seed cost. Better root system. '
        '18-20% higher final yield. Reduces damping off losses.',
        '1. Fill pro-trays with sterilized coco peat mix. '
        '2. Sow 1 seed per cell at 0.5cm depth. '
        '3. Keep under 50% shade net or poly tunnel. '
        '4. Water with rose can twice daily. '
        '5. Drench with Copper Oxychloride 3g/L on day 10. '
        '6. Harden seedlings 5 days before transplanting (reduce shade). '
        '7. Transplant at 4-leaf stage (25-30 days).',
        3500, 92,
        'Karnataka, Andhra Pradesh, Tamil Nadu, Maharashtra, Gujarat'
    ),
    (
        'Tomato Staking and Pruning (Single Stem)',
        'Crop Management', 'Tomato',
        'Train tomato plants on single vertical string or bamboo stake. Remove all suckers (side shoots) '
        'leaving only main stem. Used for indeterminate hybrids in high-density planting. '
        'Plants grow 2-4 meters tall supported by overhead wire and string.',
        '30-40% higher yield per acre. Better light interception. Improved spray coverage. '
        'Reduced disease incidence. Better fruit size and quality. '
        'Can maintain crop for 6-12 months (long-duration crop).',
        '1. Install overhead wire at 2m height with end poles. '
        '2. Tie strings vertically from wire to base of each plant. '
        '3. Twist plant around string as it grows. '
        '4. Remove all suckers weekly — leave only main stem. '
        '5. Top the plant at desired height or wire level. '
        '6. Fertilize and irrigate through drip weekly.',
        8000, 85,
        'Karnataka, Andhra Pradesh, Tamil Nadu, Maharashtra, Himachal Pradesh'
    ),
    (
        'Drip Irrigation + Fertigation for Tomato',
        'Water & Nutrient Management', 'Tomato',
        'Install inline drip laterals at 1.5m spacing with drippers at 45cm. '
        'Deliver water and soluble fertilizers directly to root zone in daily small doses. '
        'Recommended schedule: N:P:K = 180:90:120 kg/ha split over crop duration.',
        '40-50% water saving. 25-30% fertilizer saving. 25-35% higher yield. '
        'Reduces soil-borne disease from overhead irrigation. Uniform plant growth. '
        'Reduced weed pressure. Labour saving.',
        '1. Install inline drip @ 3LPH drippers at 45cm. '
        '2. Base dose: FYM 10t/ha + SSP 500kg/ha at planting. '
        '3. Weeks 1-3: Fertigation with 19:19:19 (NPK) @ 3kg/1000L. '
        '4. Weeks 4-7: Switch to 12:61:0 (MAP) + Potassium Nitrate. '
        '5. Weeks 8+: High K phase — SOP + Calcium Nitrate. '
        '6. Fertigation 3x/week; adjust based on leaf color.',
        18000, 90,
        'Karnataka, Andhra Pradesh, Maharashtra, Tamil Nadu, Gujarat, Rajasthan'
    ),
    (
        'Plastic Mulching for Tomato',
        'Weed and Water Management', 'Tomato',
        'Cover raised beds with black-silver or black polyethylene mulch (25-30 micron thickness). '
        'Silver side faces up to repel whitefly; black side down for weed control. '
        'Plant through pre-cut holes at designated spacing.',
        '80-90% weed reduction (saves 4-5 manual weedings). '
        '30-35% soil moisture conservation. Prevents soil splash (reduces Early Blight). '
        'Repels whitefly and reduces virus incidence. Increases soil temperature in winter. '
        'Yield increase 20-30%.',
        '1. Prepare raised beds 120cm wide, 20cm high. '
        '2. Lay drip lateral on bed. '
        '3. Cover with silver-black 25 micron mulch, tuck edges. '
        '4. Cut holes 45x60cm spacing using heated pipe or cutter. '
        '5. Plant seedlings through holes. '
        '6. Mulch lasts 1-2 seasons.',
        6000, 88,
        'Karnataka, Andhra Pradesh, Maharashtra, Tamil Nadu, Gujarat, Madhya Pradesh'
    ),
    (
        'Grafting Tomato on Resistant Rootstock',
        'Disease Management', 'Tomato',
        'Graft commercial tomato variety (scion) onto bacterial/fungal wilt-resistant rootstock '
        '(wild tomato or resistant brinjal). Protects against Fusarium wilt, Bacterial wilt and nematodes. '
        'Used in fields with history of wilt problems.',
        'Complete protection against soil-borne diseases in infested fields. '
        '40-60% higher yield in wilt-prone areas. Crop can be grown continuously without rotation. '
        'Larger root system, better nutrient uptake.',
        '1. Sow rootstock 7-10 days before scion. '
        '2. When pencil-thick (2-3mm), do tongue-and-groove or cleft graft. '
        '3. Secure with grafting clip. Keep in humid chamber (2-3 days) at 25°C. '
        '4. Harden gradually over 7 days. '
        '5. Transplant grafted seedlings after 30 days. '
        '6. Remove rootstock suckers regularly.',
        12000, 82,
        'Karnataka, Andhra Pradesh, Tamil Nadu, West Bengal, Maharashtra'
    ),
    (
        'Integrated Disease Management (IDM) for Tomato',
        'Disease Management', 'Tomato',
        'Systematic schedule combining cultural, biological and chemical controls to manage '
        'Late Blight, Early Blight, TLCV and other major diseases in tomato throughout crop season.',
        'Reduces fungicide sprays by 30-40%. Controls multiple diseases simultaneously. '
        'Reduces development of resistance. Lower input cost. Safer produce.',
        'PHASE 1 — Nursery (day 0-25): Seed treatment with Thiram 3g/kg. Proray method. Net house. '
        'PHASE 2 — Transplanting (week 1-2): Dip roots in Trichoderma 10g/L + Pseudomonas 10g/L. '
        'PHASE 3 — Vegetative (week 3-5): Mancozeb 75% WP 2g/L spray. '
        'PHASE 4 — Flowering (week 6-8): Copper Oxychloride 3g/L + Streptocycline 0.5g/L. '
        'PHASE 5 — Fruiting (week 9-12): Metalaxyl + Mancozeb @ 3g/L (anti-blight). '
        'PHASE 6 — Harvest: Stop sprays 7-10 days before picking.',
        5000, 87,
        'Andhra Pradesh, Karnataka, Maharashtra, Tamil Nadu, Madhya Pradesh'
    ),
    (
        'Tomato High Density Planting (HDP)',
        'Planting Method', 'Tomato',
        'Plant at closer spacing 60x45cm or 45x45cm on raised beds compared to conventional 90x60cm. '
        'Combine with pruning to single stem and vertical staking for maximum productivity per unit area.',
        '40-60% more plants per acre. Higher early yield. Better land use efficiency. '
        'Suitable for small farmers with limited land. Net profit increase Rs. 50,000-80,000/acre.',
        '1. Prepare raised beds 90-120cm wide. '
        '2. Apply mulch. '
        '3. Plant at 45x45cm (double row) or 60x45cm. '
        '4. Install vertical string support system. '
        '5. Prune to single stem strictly. '
        '6. Intensive fertigation every 2-3 days.',
        10000, 80,
        'Karnataka, Andhra Pradesh, Tamil Nadu, Maharashtra'
    ),
    (
        'Integrated Pest Management (IPM) for Tomato',
        'Pest Management', 'Tomato',
        'Combines biological, cultural and chemical pest management to control Fruit Borer, '
        'Whitefly, Aphids, Spider Mites with minimum chemical use.',
        'Reduces pesticide cost 35-40%. Protects natural enemies. Prevents resistance build-up. '
        'Safer for farmers and consumers. Reduces residues in tomato fruit.',
        '1. Use pheromone traps for Fruit Borer (Helilure @ 5 traps/acre). '
        '2. Plant African Marigold border (1 row per 14 rows). '
        '3. Install yellow sticky traps @ 10/acre for whitefly. '
        '4. Silver mulch to repel whitefly. '
        '5. Release Trichogramma @ 1.5 lakh/ha at egg-laying stage. '
        '6. Spray Bt (Bacillus thuringiensis) @ 2g/L for early instar larvae. '
        '7. Chemical spray (Emamectin 0.4g/L) only when > 2 larvae/plant.',
        3500, 83,
        'Karnataka, Andhra Pradesh, Maharashtra, Tamil Nadu, Madhya Pradesh'
    ),
    (
        'Tomato Post-Harvest Handling & Grading',
        'Post-Harvest Management', 'Tomato',
        'Proper harvesting at breaker or turning stage (not fully red), field grading by size/quality, '
        'pre-cooling, and packaging in CFB boxes or bamboo baskets to reduce losses and improve price.',
        'Reduces post-harvest loss from 30-35% to 8-10%. '
        'Graded tomato fetches 20-30% premium price in market. '
        'Better shelf life (7-10 days vs 3-5 days ungraded). Access to distant markets.',
        '1. Harvest at mature green or breaker stage for distant markets. '
        '2. Avoid harvesting in afternoon heat — do in morning. '
        '3. Field sort: grade A (>60g, round), grade B (40-60g), grade C (below, processing). '
        '4. Pre-cool at 13-15°C within 2 hours of harvest if cold chain available. '
        '5. Pack in 5kg perforated CFB boxes lined with newspaper. '
        '6. Label with grade, origin and packing date.',
        2000, 85,
        'All States'
    ),
    (
        'Tomato Protected Cultivation (Polyhouse)',
        'Protected Agriculture', 'Tomato',
        'Grow tomato inside naturally ventilated polyhouse (NVPH) with 200 micron UV-stabilized '
        'polythene film and 50-mesh side walls. Protects from rain, hailstorm, excessive heat '
        'and drastically reduces pest-disease pressure.',
        '3-4x higher yield (80-120 tonnes/ha vs 25-35 open field). '
        'Year-round production possible. 60-70% reduction in pesticide use. '
        'Premium price for off-season produce. Long crop duration (8-12 months).',
        '1. Construct NVPH (50m x 24m) with galvanised structure. '
        '2. Cover with 200 micron UV poly film on top, 50-mesh insect net on sides. '
        '3. Install drip + fertigation system. '
        '4. Plant indeterminate hybrid (Arka Rakshak or similar) at 60x45cm. '
        '5. Train on vertical string to overhead wire. '
        '6. Prune to single or double stem. '
        '7. Maintain temperature 22-28°C by vent management.',
        300000, 88,
        'Karnataka, Maharashtra, Gujarat, Rajasthan, Himachal Pradesh, Tamil Nadu'
    ),
    (
        'Tomato FPO — Collective Marketing',
        'Market Linkage', 'Tomato',
        'Form or join a Farmer Producer Organization (FPO) to pool tomato produce for collective '
        'grading, branding and direct sale to supermarkets, processors and exporters — bypassing '
        'commission agents and multiple middlemen.',
        'Farmers get 15-25% more than APMC price. Direct contract with buyers. '
        'Access to processing units (ketchup, puree) during price crash. '
        'Collective bargaining power. Input procurement at bulk discount (10-15%).',
        '1. Register FPO with 100+ farmer members with NABARD or SFAC support. '
        '2. Set up common grading and packing facility. '
        '3. Tie up with modern retail chains, supermarkets, exporters. '
        '4. Sign advance contracts before season. '
        '5. Pool produce, grade uniformly, pack under FPO brand. '
        '6. Explore tomato paste/ketchup processing during glut periods.',
        None, 78,
        'Andhra Pradesh, Karnataka, Maharashtra, Madhya Pradesh, Tamil Nadu'
    ),
]


# ══════════════════════════════════════════════════════════════
# DATABASE INSERTION FUNCTIONS
# ══════════════════════════════════════════════════════════════

def connect():
    conn = mysql.connector.connect(**config.MYSQL_CONFIG)
    cursor = conn.cursor()
    return conn, cursor

def insert_crops(conn, cursor):
    print("\n🍅 Inserting tomato crop varieties...")
    sql = """INSERT IGNORE INTO crops
             (crop_name, crop_type, botanical_name, category, season, duration_days, description)
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, CROPS)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} crop variety(ies) inserted")

def insert_market_prices(conn, cursor):
    print("\n💰 Inserting tomato market prices...")
    sql = """INSERT IGNORE INTO market_prices
             (date, state, district, market, crop_name, variety,
              min_price, max_price, modal_price, msp, unit)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, MARKET_PRICES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} price record(s) inserted")

def insert_crop_production(conn, cursor):
    print("\n📊 Inserting tomato production data...")
    sql = """INSERT IGNORE INTO crop_production
             (year, season, state, district, crop_name,
              area_hectares, production_tonnes, yield_per_hectare)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, CROP_PRODUCTION)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} production record(s) inserted")

def insert_weather_data(conn, cursor):
    print("\n🌦️  Inserting weather data for tomato zones...")
    sql = """INSERT IGNORE INTO weather_data
             (date, state, district, rainfall, temperature_min, temperature_max,
              humidity, wind_speed, conditions)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, WEATHER_DATA)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} weather record(s) inserted")

def insert_government_schemes(conn, cursor):
    print("\n🏛️  Inserting tomato-related government schemes...")
    sql = """INSERT IGNORE INTO government_schemes
             (scheme_name, scheme_type, state, start_date, end_date,
              budget_amount, beneficiaries, description, eligibility,
              benefits, application_process, contact_info, is_active)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, GOVERNMENT_SCHEMES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} scheme(s) inserted")

def insert_pest_diseases(conn, cursor):
    print("\n🐛 Inserting tomato pest & disease data...")
    sql = """INSERT IGNORE INTO pest_diseases
             (name, type, affected_crops, symptoms, causes, prevention, treatment, severity, season)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, PEST_DISEASES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} pest/disease record(s) inserted")

def insert_farming_practices(conn, cursor):
    print("\n💡 Inserting tomato farming practices...")
    sql = """INSERT IGNORE INTO farming_practices
             (practice_name, category, crop_name, description, benefits,
              implementation, cost_estimate, success_rate, recommended_states)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, FARMING_PRACTICES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} practice(s) inserted")

def show_summary(cursor):
    print("\n📊 Tomato Data Summary:")
    print("   " + "─"*45)
    tables = ['crops', 'market_prices', 'crop_production', 'weather_data',
              'government_schemes', 'pest_diseases', 'farming_practices']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE 1=1")
        total = cursor.fetchone()[0]
        if table == 'crops':
            cursor.execute("SELECT COUNT(*) FROM crops WHERE crop_name LIKE '%Tomato%'")
        elif table in ('market_prices', 'crop_production'):
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE crop_name LIKE '%Tomato%'")
        elif table == 'pest_diseases':
            cursor.execute("SELECT COUNT(*) FROM pest_diseases WHERE affected_crops LIKE '%Tomato%'")
        elif table == 'farming_practices':
            cursor.execute("SELECT COUNT(*) FROM farming_practices WHERE crop_name LIKE '%Tomato%'")
        elif table == 'weather_data':
            cursor.execute("SELECT COUNT(*) FROM weather_data")
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
        tomato_count = cursor.fetchone()[0]
        print(f"   {table:<25} → {total} total rows  ({tomato_count} tomato)")
    print("   " + "─"*45)

    print("\n🍅 Tomato Price Range by State:")
    cursor.execute("""
        SELECT state, MIN(min_price) as lowest, MAX(max_price) as highest, 
               ROUND(AVG(modal_price)) as avg_modal
        FROM market_prices 
        WHERE crop_name LIKE '%Tomato%'
        GROUP BY state ORDER BY avg_modal DESC
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"   {row[0]:<20} Low: ₹{row[1]}/q  High: ₹{row[2]}/q  Avg: ₹{row[3]}/q")


def main():
    print("="*65)
    print("🍅 TOMATO FULL DATASET — AGRICULTURE CHATBOT")
    print("="*65)
    print(f"  Varieties    : {len(CROPS)} entries")
    print(f"  Market Prices: {len(MARKET_PRICES)} entries (multi-state, multi-date)")
    print(f"  Production   : {len(CROP_PRODUCTION)} entries (district level)")
    print(f"  Weather Data : {len(WEATHER_DATA)} entries (key tomato zones)")
    print(f"  Govt Schemes : {len(GOVERNMENT_SCHEMES)} entries")
    print(f"  Pest/Disease : {len(PEST_DISEASES)} entries")
    print(f"  Farming Tips : {len(FARMING_PRACTICES)} entries")
    print("="*65)

    try:
        conn, cursor = connect()
        print("✅ Connected to MySQL")

        insert_crops(conn, cursor)
        insert_market_prices(conn, cursor)
        insert_crop_production(conn, cursor)
        insert_weather_data(conn, cursor)
        insert_government_schemes(conn, cursor)
        insert_pest_diseases(conn, cursor)
        insert_farming_practices(conn, cursor)

        show_summary(cursor)

        cursor.close()
        conn.close()

        print("\n" + "="*65)
        print("✅ TOMATO DATASET INSERTED SUCCESSFULLY!")
        print("   Now run: python app.py")
        print("   Try asking: 'What is tomato price in Kolar?'")
        print("               'How to treat Late Blight in tomato?'")
        print("               'Best tomato farming practices'")
        print("               'Tomato production in Andhra Pradesh'")
        print("               'Government schemes for tomato farmers'")
        print("="*65)

    except Error as e:
        print(f"\n❌ Database error: {e}")
        print("   → Check MYSQL_CONFIG in agri_config.py")
        print("   → Make sure MySQL is running")
        print("   → Run 2_setup_agriculture_db.py first if not done")
        raise

if __name__ == "__main__":
    main()