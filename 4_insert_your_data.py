"""
=============================================================
  DIRECT DATA ENTRY — Agriculture Chatbot (MySQL)
=============================================================
  No PDF needed! Add your real agriculture data here directly.
  Run:  python 4_insert_your_data.py

  SECTIONS:
    1. CROPS           — crop details, season, duration
    2. MARKET PRICES   — daily/weekly prices per market
    3. CROP PRODUCTION — area, yield, production stats
    4. WEATHER DATA    — rainfall, temperature per district
    5. GOVT SCHEMES    — PM-KISAN, PMFBY etc.
    6. PEST & DISEASES — symptoms, treatment, prevention
    7. FARMING PRACTICES — best practices per crop
=============================================================
"""

import mysql.connector
from mysql.connector import Error
import agri_config as config


# ──────────────────────────────────────────────────────────────
# ✏️  EDIT THIS DATA — Add your own rows below each section
# ──────────────────────────────────────────────────────────────

# 1. CROPS
# (crop_name, crop_type, botanical_name, category, season, duration_days, description)
CROPS = [
    ('Rice',       'Cereal',    'Oryza sativa',              'Cereals',    'Kharif',    120, 'Staple food crop grown in flooded fields. Needs heavy water.'),
    ('Wheat',      'Cereal',    'Triticum aestivum',         'Cereals',    'Rabi',      125, 'Winter cereal; major food grain of North India.'),
    ('Maize',      'Cereal',    'Zea mays',                  'Cereals',    'Kharif',     90, 'Used as food, fodder and in industry.'),
    ('Cotton',     'Fiber',     'Gossypium hirsutum',        'Cash Crops', 'Kharif',    180, 'Commercial fiber crop; "white gold" of India.'),
    ('Sugarcane',  'Cash Crop', 'Saccharum officinarum',     'Cash Crops', 'Perennial', 365, 'Sugar and ethanol production crop.'),
    ('Groundnut',  'Oilseed',   'Arachis hypogaea',          'Oilseeds',   'Kharif',    120, 'Major oilseed crop of peninsular India.'),
    ('Soybean',    'Oilseed',   'Glycine max',               'Oilseeds',   'Kharif',    100, 'Rich in protein; grown heavily in Madhya Pradesh & Maharashtra.'),
    ('Tomato',     'Vegetable', 'Solanum lycopersicum',      'Vegetables', 'Rabi',       75, 'High-value horticulture crop.'),
    ('Onion',      'Vegetable', 'Allium cepa',               'Vegetables', 'Rabi',      120, 'Major vegetable export crop; grown in Maharashtra & Karnataka.'),
    ('Tur/Arhar',  'Pulse',     'Cajanus cajan',             'Pulses',     'Kharif',    180, 'Pigeon pea; major pulse crop of India.'),
    ('Chickpea',   'Pulse',     'Cicer arietinum',           'Pulses',     'Rabi',      120, 'Also called Bengal gram; largest pulse crop.'),
    ('Banana',     'Fruit',     'Musa acuminata',            'Fruits',     'Perennial', 365, 'Tropical fruit; major export from Andhra, Tamil Nadu, Maharashtra.'),
    ('Turmeric',   'Spice',     'Curcuma longa',             'Spices',     'Kharif',    270, 'High-value spice crop; India is world\'s largest producer.'),
    ('Jute',       'Fiber',     'Corchorus olitorius',       'Cash Crops', 'Kharif',    120, 'Natural fiber crop; grown mainly in West Bengal.'),
    ('Mustard',    'Oilseed',   'Brassica juncea',           'Oilseeds',   'Rabi',      110, 'Major Rabi oilseed; grown in Rajasthan and Haryana.'),
    # ── ADD MORE CROPS BELOW ──
]


# 2. MARKET PRICES
# (date, state, district, market, crop_name, variety, min_price, max_price, modal_price, msp, unit)
MARKET_PRICES = [
    # Karnataka
    ('2024-01-15', 'Karnataka', 'Bangalore',  'APMC Bangalore',  'Rice',      'Sona Masuri', 2700, 3100, 2900, 2183, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Bangalore',  'APMC Bangalore',  'Rice',      'Basmati',     3500, 4200, 3800, 2183, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Mysore',     'APMC Mysore',     'Maize',     'Hybrid',       1700, 1950, 1820, 1870, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Dharwad',    'APMC Dharwad',    'Cotton',    'BT Hybrid',   6200, 6800, 6500, 6620, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Raichur',    'APMC Raichur',    'Tur/Arhar', 'Desi',        6800, 7500, 7100, 7000, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Belgaum',    'APMC Belgaum',    'Sugarcane', 'Co-86032',     350,  400,  375,  315, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Bangalore',  'APMC Bangalore',  'Tomato',    'Local',        1200, 2500, 1800, None, 'per quintal'),
    ('2024-01-15', 'Karnataka', 'Bangalore',  'APMC Bangalore',  'Onion',     'Bellary Red',   800, 1400, 1100, None, 'per quintal'),
    # Maharashtra
    ('2024-01-15', 'Maharashtra', 'Pune',     'APMC Pune',       'Wheat',     'Sharbati',    2400, 2700, 2550, 2275, 'per quintal'),
    ('2024-01-15', 'Maharashtra', 'Nagpur',   'APMC Nagpur',     'Cotton',    'Long Staple', 6500, 7200, 6800, 6620, 'per quintal'),
    ('2024-01-15', 'Maharashtra', 'Nashik',   'APMC Nashik',     'Onion',     'Nashik Red',   700, 1200, 950,  None, 'per quintal'),
    ('2024-01-15', 'Maharashtra', 'Solapur',  'APMC Solapur',    'Soybean',   'JS-335',      4200, 4700, 4450, 4600, 'per quintal'),
    # Punjab
    ('2024-01-15', 'Punjab',    'Ludhiana',   'APMC Ludhiana',   'Wheat',     'HD-2967',     2300, 2600, 2450, 2275, 'per quintal'),
    ('2024-01-15', 'Punjab',    'Amritsar',   'APMC Amritsar',   'Rice',      'PR-14',       2500, 2900, 2700, 2183, 'per quintal'),
    # Rajasthan
    ('2024-01-15', 'Rajasthan', 'Jaipur',     'APMC Jaipur',     'Mustard',   'RH-30',       5200, 5800, 5500, 5650, 'per quintal'),
    ('2024-01-15', 'Rajasthan', 'Bikaner',    'APMC Bikaner',    'Groundnut', 'J-11',        5500, 6200, 5800, 5850, 'per quintal'),
    # Uttar Pradesh
    ('2024-01-15', 'Uttar Pradesh', 'Lucknow','APMC Lucknow',    'Wheat',     'PBW-343',     2200, 2500, 2350, 2275, 'per quintal'),
    ('2024-01-15', 'Uttar Pradesh', 'Meerut', 'APMC Meerut',     'Sugarcane', 'Co-0238',      350,  410,  380,  315, 'per quintal'),
    # Andhra Pradesh
    ('2024-01-15', 'Andhra Pradesh','Guntur', 'APMC Guntur',     'Maize',     'Hybrid',       1800, 2100, 1950, 1870, 'per quintal'),
    ('2024-01-15', 'Andhra Pradesh','Krishna','APMC Krishna',    'Rice',      'Sona Masuri',  2600, 3000, 2800, 2183, 'per quintal'),
    # ── ADD MORE PRICES BELOW (change dates for recent data) ──
]


# 3. CROP PRODUCTION
# (year, season, state, district, crop_name, area_hectares, production_tonnes, yield_per_hectare)
CROP_PRODUCTION = [
    # Karnataka
    ('2023-24', 'Kharif', 'Karnataka',    'Bangalore Rural', 'Rice',      45000,  180000, 4.0),
    ('2023-24', 'Kharif', 'Karnataka',    'Dharwad',         'Cotton',    85000,  255000, 3.0),
    ('2023-24', 'Kharif', 'Karnataka',    'Mysore',          'Maize',     32000,  192000, 6.0),
    ('2023-24', 'Rabi',   'Karnataka',    'Bidar',           'Chickpea',  28000,   42000, 1.5),
    ('2023-24', 'Kharif', 'Karnataka',    'Raichur',         'Tur/Arhar', 22000,   22000, 1.0),
    # Punjab
    ('2023-24', 'Rabi',   'Punjab',       'Ludhiana',        'Wheat',    120000,  600000, 5.0),
    ('2023-24', 'Kharif', 'Punjab',       'Amritsar',        'Rice',      95000,  475000, 5.0),
    # Maharashtra
    ('2023-24', 'Kharif', 'Maharashtra',  'Nagpur',          'Cotton',   120000,  360000, 3.0),
    ('2023-24', 'Kharif', 'Maharashtra',  'Latur',           'Soybean',   88000,  176000, 2.0),
    ('2023-24', 'Rabi',   'Maharashtra',  'Nashik',          'Onion',     15000,  450000, 30.0),
    # Rajasthan
    ('2023-24', 'Rabi',   'Rajasthan',    'Jaipur',          'Mustard',   75000,  150000, 2.0),
    ('2023-24', 'Kharif', 'Rajasthan',    'Bikaner',         'Groundnut', 42000,   84000, 2.0),
    # Uttar Pradesh
    ('2023-24', 'Rabi',   'Uttar Pradesh','Meerut',          'Wheat',    250000, 1250000, 5.0),
    ('2023-24', 'Kharif', 'Uttar Pradesh','Lucknow',         'Sugarcane',  85000, 5950000, 70.0),
    # Andhra Pradesh
    ('2023-24', 'Kharif', 'Andhra Pradesh','Krishna',        'Rice',      55000,  275000, 5.0),
    # ── ADD MORE PRODUCTION DATA BELOW ──
]


# 4. WEATHER DATA
# (date, state, district, rainfall_mm, temp_min_C, temp_max_C, humidity_%, wind_speed_kmh, conditions)
WEATHER_DATA = [
    ('2024-01-15', 'Karnataka',    'Bangalore',  0.0, 15.0, 28.0, 55.0, 8.0,  'Clear'),
    ('2024-01-15', 'Karnataka',    'Mysore',     0.0, 13.5, 27.5, 50.0, 7.0,  'Sunny'),
    ('2024-01-15', 'Karnataka',    'Dharwad',    2.0, 14.0, 26.0, 62.0, 10.0, 'Partly Cloudy'),
    ('2024-01-15', 'Maharashtra',  'Pune',       0.0, 12.0, 29.0, 45.0, 9.0,  'Sunny'),
    ('2024-01-15', 'Maharashtra',  'Nagpur',     0.0, 11.0, 30.0, 40.0, 12.0, 'Clear'),
    ('2024-01-15', 'Punjab',       'Ludhiana',   0.0,  5.0, 18.0, 72.0, 6.0,  'Foggy'),
    ('2024-01-15', 'Punjab',       'Amritsar',   0.0,  4.0, 17.0, 78.0, 5.0,  'Dense Fog'),
    ('2024-01-15', 'Rajasthan',    'Jaipur',     0.0,  8.0, 22.0, 35.0, 15.0, 'Clear'),
    ('2024-01-15', 'Uttar Pradesh','Lucknow',    0.0,  7.0, 19.0, 75.0, 8.0,  'Foggy'),
    ('2024-01-15', 'Andhra Pradesh','Guntur',    0.0, 18.0, 32.0, 65.0, 14.0, 'Sunny'),
    # Monsoon season data
    ('2023-08-15', 'Karnataka',    'Bangalore', 45.0, 20.0, 26.0, 88.0, 18.0, 'Heavy Rain'),
    ('2023-08-15', 'Maharashtra',  'Pune',      62.0, 19.0, 25.0, 90.0, 20.0, 'Very Heavy Rain'),
    ('2023-08-15', 'Kerala',       'Thrissur',  95.0, 22.0, 27.0, 95.0, 25.0, 'Extremely Heavy Rain'),
    # ── ADD MORE WEATHER DATA BELOW ──
]


# 5. GOVERNMENT SCHEMES
# (scheme_name, scheme_type, state, start_date, end_date,
#  budget_crore, beneficiaries_lakhs, description, eligibility, benefits,
#  application_process, contact_info, is_active)
GOVERNMENT_SCHEMES = [
    (
        'PM-KISAN',
        'Direct Benefit Transfer', 'All India', '2019-02-01', None,
        750000, 1100,
        'Pradhan Mantri Kisan Samman Nidhi provides income support of Rs.6000/year to all landholding farmer families in three equal installments of Rs.2000 each.',
        'All farmer families with cultivable landholding. Excludes institutional landholders, farmer families holding constitutional posts, income tax payers.',
        'Rs. 6000 per year in three installments of Rs. 2000 each directly to bank account.',
        'Register at pmkisan.gov.in or visit nearest CSC. Aadhaar, land records and bank account required.',
        '1800-115-526 (Helpline) | pmkisan@gov.in',
        True
    ),
    (
        'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
        'Crop Insurance', 'All India', '2016-02-18', None,
        130000, 550,
        'Comprehensive crop insurance against natural calamities, pests and diseases. One Nation One Scheme.',
        'All farmers growing notified crops. Compulsory for loanee farmers, voluntary for others.',
        'Coverage of sum insured with premium as low as 1.5% for Rabi, 2% for Kharif, 5% for horticulture. Claim within 72 hours of damage.',
        'Register through bank branches, CSCs, or pmfby.gov.in. Submit before cut-off date for each season.',
        '1800-180-1111 | help.agri-insurance.gov.in',
        True
    ),
    (
        'PM Kisan Credit Card (KCC)',
        'Credit & Loan', 'All India', '1998-08-01', None,
        None, 700,
        'Flexible credit for agricultural needs at low interest rate of 4% per annum. Covers cultivation, post-harvest and allied activities.',
        'All farmers — individual or joint borrowers who are owner cultivators. Tenant farmers, oral lessees and sharecroppers also eligible.',
        'Revolving credit up to Rs. 3 lakh at 4% interest (with subvention). Repay after harvest. Accident insurance coverage up to Rs. 50,000.',
        'Apply at any bank branch or cooperative with land records, ID proof, and photograph.',
        'Contact nearest bank branch or NABARD',
        True
    ),
    (
        'Soil Health Card Scheme',
        'Input Support', 'All India', '2015-02-19', None,
        568, None,
        'Provides soil health cards to all farmers showing nutrient status of soil with recommendations on dosage of fertilizers.',
        'All farmers across India.',
        'Free soil testing, report card with crop-wise fertilizer recommendations, reduces input cost by 8-10%.',
        'Collect from nearest Krishi Vigyan Kendra or soil testing laboratory. No registration needed.',
        '1800-180-1551',
        True
    ),
    (
        'PM Krishi Sinchayee Yojana (PMKSY)',
        'Irrigation', 'All India', '2015-07-01', None,
        50000, None,
        '"Har Khet Ko Pani" and "More Crop Per Drop" — convergence of irrigation schemes. Promotes micro-irrigation (drip and sprinkler).',
        'Farmers with landholdings. Subsidy: 55% for small/marginal farmers, 45% for others.',
        'Up to 55% subsidy on drip and sprinkler irrigation systems. Reduces water use by 40-50%.',
        'Apply through state agriculture department or pmksy.gov.in.',
        '1800-180-1551',
        True
    ),
    (
        'Rashtriya Krishi Vikas Yojana (RKVY)',
        'Development', 'All India', '2007-08-01', None,
        25000, None,
        'Incentivizes states to increase public investment in agriculture. Funds infrastructure, technology adoption and market linkage.',
        'State governments for agriculture development projects. Farmers benefit indirectly.',
        'Infrastructure development, technology demonstration, cold storage, market yards.',
        'Through state agriculture department.',
        'State Agriculture Department',
        True
    ),
    (
        'Karnataka Raita Siri',
        'Direct Benefit Transfer', 'Karnataka', '2023-06-01', None,
        8000, 50,
        'Karnataka state scheme providing income support of Rs. 2000 per season to eligible farmers.',
        'Karnataka farmers with land up to 10 acres enrolled in Raita Siri portal.',
        'Rs. 2000 per season directly to bank account. Kharif and Rabi seasons covered.',
        'Register at raitasiri.karnataka.gov.in with Aadhaar, land records and bank details.',
        '1800-425-7520 | raita@karnataka.gov.in',
        True
    ),
    # ── ADD MORE SCHEMES BELOW ──
]


# 6. PEST & DISEASES
# (name, type, affected_crops, symptoms, causes, prevention, treatment, severity, season)
PEST_DISEASES = [
    (
        'Brown Plant Hopper (BPH)', 'Pest',
        'Rice',
        'Yellowing and drying of leaves from base upward (hopper burn). Plants collapse in circular patches. Sticky honeydew on lower stem.',
        'Excessive nitrogen fertilizer, close planting, high humidity above 80%, temperature 25-30°C.',
        'Use resistant varieties (IR-64, Swarna), maintain proper spacing, avoid excess nitrogen, drain field intermittently.',
        'Buprofezin 25% SC @ 1ml/L or Imidacloprid 17.8% SL @ 0.5ml/L spray on lower stem. Drain water before spraying.',
        'High', 'Kharif'
    ),
    (
        'Stem Borer', 'Pest',
        'Rice, Sugarcane, Maize',
        'Dead heart (central shoot dries) in vegetative stage. White ear (unfilled grains) at flowering stage. Entry holes on stem.',
        'Moths lay eggs on leaf tips. Larvae bore into stem. Peak attack during transplanting and flowering.',
        'Remove and destroy egg masses, avoid close spacing, light traps @ 1/acre, release Trichogramma japonicum egg parasitoid.',
        'Chlorpyrifos 20% EC @ 2.5ml/L or Cartap Hydrochloride 4G @ 25kg/ha. Carbofuran 3G in standing water.',
        'High', 'Kharif'
    ),
    (
        'Blast Disease', 'Disease',
        'Rice, Wheat, Finger Millet',
        'Diamond-shaped lesions with grey center and brown border on leaves. Neck blast causes panicle to break. Grain discolouration.',
        'Fungal infection (Magnaporthe oryzae). Favoured by high humidity, low temperature (23-28°C), heavy dew, cloudy weather.',
        'Resistant varieties, balanced fertilization (avoid excess nitrogen), proper spacing for air circulation.',
        'Tricyclazole 75% WP @ 0.6g/L or Isoprothiolane 40% EC @ 1.5ml/L. Spray at boot leaf and panicle initiation stages.',
        'High', 'Kharif'
    ),
    (
        'Powdery Mildew', 'Disease',
        'Wheat, Chickpea, Mustard, Vegetables',
        'White powdery coating on upper leaf surface. Leaves turn yellow and drop. Severely affected plants dry up prematurely.',
        'Fungal infection (Erysiphe spp). Dry weather, high humidity at night, temperature 15-25°C. Spreads by wind.',
        'Grow resistant varieties. Avoid dense planting. Crop rotation. Sulphur dust (25kg/ha) as preventive.',
        'Wettable sulphur 80% WP @ 3g/L or Hexaconazole 5% EC @ 2ml/L. Spray 2-3 times at 10-day intervals.',
        'Medium', 'Rabi'
    ),
    (
        'American Bollworm (Helicoverpa)', 'Pest',
        'Cotton, Chickpea, Tomato, Maize',
        'Circular holes on bolls, fruits or pods. Larva feeds inside boll destroying fiber and seeds. Frass at entry hole.',
        'Polyphagous pest; moths lay eggs on tender plant parts. Severe damage July-October in cotton.',
        'Plant trap crop (African marigold or cowpea). Use Bt cotton varieties. Pheromone traps @ 5/acre. NPV spray.',
        'Emamectin benzoate 5% SG @ 0.4g/L or Spinosad 45% SC @ 0.3ml/L. Spray when larval count > 2/plant.',
        'High', 'Kharif'
    ),
    (
        'Late Blight', 'Disease',
        'Potato, Tomato',
        'Water-soaked dark-brown lesions on leaves and stems. White fungal growth on underside of leaves in humid conditions. Tubers rot.',
        'Fungal oomycete Phytophthora infestans. Cool temperatures (10-20°C) and high humidity above 90% trigger epidemic.',
        'Use certified disease-free seed, resistant varieties (Kufri Jyoti), avoid overhead irrigation, ensure air circulation.',
        'Mancozeb 75% WP @ 2.5g/L or Cymoxanil 8% + Mancozeb 64% @ 3g/L. Spray every 7-10 days during humid weather.',
        'High', 'Rabi'
    ),
    (
        'Yellow Mosaic Virus (YMV)', 'Disease',
        'Soybean, Mung Bean, Tur/Arhar',
        'Yellow-green mosaic pattern on young leaves. Stunted growth. Pods fail to form. Yield loss up to 100% if early infection.',
        'Transmitted by whitefly (Bemisia tabaci). Spreads from infected plants and weeds. High temperature favours whitefly.',
        'Use resistant varieties (Pusa 16 in mung). Rogue out infected plants. Control whitefly with reflective mulch.',
        'Control vector whitefly: Imidacloprid 17.8% SL @ 0.5ml/L or Thiamethoxam 25% WG @ 0.3g/L. No direct cure for virus.',
        'High', 'Kharif'
    ),
    (
        'Aphids', 'Pest',
        'Wheat, Mustard, Vegetables, Cotton',
        'Curling and yellowing of leaves. Stunted plant growth. Black sooty mold on honeydew. Ants around infested plants.',
        'Soft-bodied insects reproduce rapidly in cool dry weather. Dense populations under mild temperatures (15-25°C).',
        'Encourage natural enemies (ladybird beetles). Avoid excess nitrogen. Yellow sticky traps. Reflective mulch.',
        'Dimethoate 30% EC @ 2ml/L or Imidacloprid 17.8% SL @ 0.25ml/L. Spray only when population > 10 aphids/leaf.',
        'Medium', 'Rabi'
    ),
    # ── ADD MORE PESTS/DISEASES BELOW ──
]


# 7. FARMING PRACTICES
# (practice_name, category, crop_name, description, benefits, implementation, cost_estimate_per_acre, success_rate, recommended_states)
FARMING_PRACTICES = [
    (
        'System of Rice Intensification (SRI)',
        'Cultivation Technique', 'Rice',
        'SRI uses young seedlings (8-12 days), wide spacing (25x25cm), intermittent irrigation and organic matter for higher yield.',
        '20-50% higher yield, 25-30% less water, 20% less seed, reduced methane emissions, better grain quality.',
        '1. Transplant 8-12 day old seedlings singly. 2. Maintain 25x25cm spacing. 3. Apply weed compost. 4. Keep soil moist but not flooded. 5. Use rotary weeder.',
        3500, 85,
        'Karnataka, Tamil Nadu, Andhra Pradesh, West Bengal'
    ),
    (
        'Drip Irrigation for Sugarcane',
        'Water Management', 'Sugarcane',
        'Sub-surface or surface drip delivers water directly to root zone. Combined with fertigation for maximum efficiency.',
        '30-40% water saving, 15-20% higher yield, 25% saving in fertilizer, uniform crop growth, weed reduction.',
        '1. Lay laterals at 1.5m spacing. 2. Install drippers at 50cm intervals. 3. Fertigate NPK through system. 4. Monitor soil moisture. 5. Flush lines monthly.',
        18000, 90,
        'Maharashtra, Karnataka, Tamil Nadu, Gujarat, Uttar Pradesh'
    ),
    (
        'Zero Tillage Wheat',
        'Conservation Agriculture', 'Wheat',
        'Sowing wheat directly in rice stubble without plowing using Happy Seeder or zero-till drill. Conserves soil moisture and structure.',
        'Saves Rs.2000-3000/acre on tillage cost, reduces water use, better weed control, saves 15-20 days, reduces stubble burning.',
        '1. After rice harvest, adjust Happy Seeder. 2. Sow seed + fertilizer simultaneously. 3. No puddling or plowing needed. 4. First irrigation at 21 days.',
        1200, 88,
        'Punjab, Haryana, Uttar Pradesh, Madhya Pradesh'
    ),
    (
        'Integrated Pest Management (IPM) for Cotton',
        'Pest Management', 'Cotton',
        'Combines biological, cultural and chemical controls to minimize pesticide use while maintaining crop protection.',
        'Reduces pesticide cost by 30-40%, protects natural enemies, sustainable yield, better profit, food safety.',
        '1. Use BT cotton seed. 2. Install pheromone traps. 3. Plant marigold as border trap crop. 4. Release Chrysoperla predators. 5. Spray only when threshold crossed.',
        2500, 82,
        'Maharashtra, Telangana, Andhra Pradesh, Karnataka, Gujarat'
    ),
    (
        'Mulching in Vegetables',
        'Soil Management', 'Tomato',
        'Cover soil with black polythene or organic matter (straw, crop residue) to conserve moisture, control weeds and maintain temperature.',
        '30% water saving, 80% weed reduction, prevents soil-borne diseases, uniform soil temperature, 20-25% higher yield.',
        '1. Prepare beds. 2. Lay drip laterals. 3. Spread black polythene 25 micron. 4. Make holes for planting. 5. Plant seedlings through holes.',
        4000, 87,
        'Karnataka, Maharashtra, Tamil Nadu, Gujarat, Rajasthan'
    ),
    (
        'Intercropping Tur with Soybean',
        'Cropping System', 'Tur/Arhar',
        'Plant 2 rows Soybean + 1 row Tur in 1:2 or 2:4 pattern. Both Kharif crops with complementary growth periods.',
        'Risk reduction, better land use efficiency (LER > 1.3), additional income from soybean, nitrogen fixation benefits Tur.',
        '1. Prepare field. 2. Mark rows at 45cm spacing. 3. Sow soybean in 2 rows then Tur in 1 row. 4. Harvest soybean at 90 days, Tur at 180 days.',
        None, 80,
        'Maharashtra, Madhya Pradesh, Karnataka, Telangana'
    ),
    (
        'Fertigation through Drip',
        'Nutrient Management', 'General',
        'Applying water-soluble fertilizers through drip irrigation system directly to root zone in small frequent doses.',
        '20-30% fertilizer saving, better nutrient uptake, uniform application, reduces leaching, higher crop quality and yield.',
        '1. Ensure clean drip system. 2. Use water-soluble fertilizers (MKP, SOP, calcium nitrate). 3. Fertigate 2-3 times/week. 4. Flush system after fertigation.',
        None, 90,
        'Karnataka, Maharashtra, Gujarat, Tamil Nadu, Telangana'
    ),
    # ── ADD MORE PRACTICES BELOW ──
]


# ──────────────────────────────────────────────────────────────
# DATABASE INSERTION LOGIC (no need to edit below this line)
# ──────────────────────────────────────────────────────────────

def connect():
    conn = mysql.connector.connect(**config.MYSQL_CONFIG)
    cursor = conn.cursor()
    return conn, cursor

def insert_crops(conn, cursor):
    print("\n🌾 Inserting crops...")
    sql = """INSERT IGNORE INTO crops
             (crop_name, crop_type, botanical_name, category, season, duration_days, description)
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, CROPS)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} crop(s) inserted/updated")

def insert_market_prices(conn, cursor):
    print("\n💰 Inserting market prices...")
    sql = """INSERT IGNORE INTO market_prices
             (date, state, district, market, crop_name, variety,
              min_price, max_price, modal_price, msp, unit)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, MARKET_PRICES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} price record(s) inserted/updated")

def insert_crop_production(conn, cursor):
    print("\n📊 Inserting crop production data...")
    sql = """INSERT IGNORE INTO crop_production
             (year, season, state, district, crop_name,
              area_hectares, production_tonnes, yield_per_hectare)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, CROP_PRODUCTION)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} production record(s) inserted/updated")

def insert_weather_data(conn, cursor):
    print("\n🌦️  Inserting weather data...")
    sql = """INSERT IGNORE INTO weather_data
             (date, state, district, rainfall, temperature_min, temperature_max,
              humidity, wind_speed, conditions)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, WEATHER_DATA)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} weather record(s) inserted/updated")

def insert_government_schemes(conn, cursor):
    print("\n🏛️  Inserting government schemes...")
    sql = """INSERT IGNORE INTO government_schemes
             (scheme_name, scheme_type, state, start_date, end_date,
              budget_amount, beneficiaries, description, eligibility,
              benefits, application_process, contact_info, is_active)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, GOVERNMENT_SCHEMES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} scheme(s) inserted/updated")

def insert_pest_diseases(conn, cursor):
    print("\n🐛 Inserting pest & disease data...")
    sql = """INSERT IGNORE INTO pest_diseases
             (name, type, affected_crops, symptoms, causes, prevention, treatment, severity, season)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, PEST_DISEASES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} pest/disease record(s) inserted/updated")

def insert_farming_practices(conn, cursor):
    print("\n💡 Inserting farming practices...")
    sql = """INSERT IGNORE INTO farming_practices
             (practice_name, category, crop_name, description, benefits,
              implementation, cost_estimate, success_rate, recommended_states)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(sql, FARMING_PRACTICES)
    conn.commit()
    print(f"   ✅ {cursor.rowcount} practice(s) inserted/updated")

def show_summary(cursor):
    print("\n📊 Database Summary:")
    print("   " + "-"*40)
    tables = ['crops', 'market_prices', 'crop_production', 'weather_data',
              'government_schemes', 'pest_diseases', 'farming_practices']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table:<25} → {count} rows")
    print("   " + "-"*40)

def main():
    print("="*60)
    print("🌱 AGRICULTURE DATABASE — DIRECT DATA ENTRY")
    print("="*60)

    try:
        conn, cursor = connect()
        print("✅ Connected to MySQL database")

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

        print("\n" + "="*60)
        print("✅ ALL DATA INSERTED SUCCESSFULLY!")
        print("   Now run:  python app.py")
        print("   Open:     http://localhost:5000")
        print("="*60)

    except Error as e:
        print(f"\n❌ Database error: {e}")
        print("   → Check MYSQL_CONFIG in agri_config.py")
        print("   → Make sure MySQL is running")
        print("   → Make sure 2_setup_agriculture_db.py was run first")
        raise

if __name__ == "__main__":
    main()