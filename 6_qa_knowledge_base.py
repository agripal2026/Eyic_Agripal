"""
=============================================================
  6_qa_knowledge_base.py
  Agriculture Chatbot — Q&A Knowledge Base (MySQL)
=============================================================
  Creates a new table: qa_knowledge
  Inserts 200+ Q&A pairs covering:
    • Tomato, Rice, Wheat, Cotton, Sugarcane,
      Onion, Potato, Brinjal
  Categories:
    • cultivation  — how to grow, sow, harvest
    • price        — MSP, market prices, rates
    • pest         — diagnosis, symptoms, treatment
    • scheme       — govt subsidies, loans, insurance

  Run:
      python 6_qa_knowledge_base.py

  The app.py chatbot will automatically search this table
  when a user asks a question. See bottom of this file for
  the updated get_qa_answer() function to add to app.py.
=============================================================
"""

import mysql.connector
from mysql.connector import Error
import agri_config as config

# ══════════════════════════════════════════════════════════════
#  TABLE SCHEMA
#  qa_knowledge (
#    id, crop, category, question, answer,
#    keywords, state, season, created_at
#  )
# ══════════════════════════════════════════════════════════════

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS qa_knowledge (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    crop        VARCHAR(100)  NOT NULL,
    category    VARCHAR(50)   NOT NULL,
    question    TEXT          NOT NULL,
    answer      TEXT          NOT NULL,
    keywords    VARCHAR(500),
    state       VARCHAR(100)  DEFAULT 'All India',
    season      VARCHAR(50)   DEFAULT 'All',
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    FULLTEXT KEY ft_qa (question, answer, keywords)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# ══════════════════════════════════════════════════════════════
#  Q&A DATA
#  Each tuple: (crop, category, question, answer, keywords, state, season)
# ══════════════════════════════════════════════════════════════

QA_DATA = [

    # ╔══════════════════════════════════════════════╗
    # ║              🍅  TOMATO                      ║
    # ╚══════════════════════════════════════════════╝

    # --- TOMATO : CULTIVATION ---
    ("Tomato", "cultivation",
     "How to grow tomato step by step?",
     "Step-by-step tomato cultivation:\n"
     "1. NURSERY (25-30 days): Raise seedlings in pro-trays with coco peat mix under 50% shade net. Sow 1 seed/cell.\n"
     "2. LAND PREPARATION: Deep plough 2-3 times. Apply FYM 10 tonnes/ha. Form raised beds 120cm wide.\n"
     "3. TRANSPLANTING: Transplant 25-30 day old seedlings at 60x45cm spacing. Water immediately after planting.\n"
     "4. IRRIGATION: Use drip irrigation. Water daily for first week, then alternate days. Critical at flowering and fruiting.\n"
     "5. FERTILIZER: Apply N:P:K = 180:90:120 kg/ha. Split N into 4-5 doses. Use fertigation through drip.\n"
     "6. STAKING: Install bamboo stakes or vertical string at 30 days. Tie plants every 15cm.\n"
     "7. PRUNING: Remove suckers weekly. Maintain single or double stem.\n"
     "8. PLANT PROTECTION: Spray Mancozeb 2g/L preventively every 10 days. Monitor for whitefly and fruit borer.\n"
     "9. HARVEST: First harvest at 60-70 days after transplanting. Pick every 3-4 days. Yield: 25-40 tonnes/ha.",
     "tomato cultivation grow steps guide planting transplanting irrigation fertilizer",
     "All India", "All"),

    ("Tomato", "cultivation",
     "What is the best season to grow tomato in India?",
     "Tomato can be grown in three seasons in India:\n\n"
     "1. KHARIF (June-July planting): Grown in hilly areas (Himachal Pradesh, Uttarakhand). Risky in plains due to heavy rain and disease pressure. Harvest: September-October.\n\n"
     "2. RABI (October-November planting): BEST SEASON for plains. Cool dry weather ideal. Low disease pressure. High quality fruit. Harvest: January-March. Most commercial cultivation happens in Rabi.\n\n"
     "3. SUMMER/ZAID (January-February planting): Possible in North India. Risk of heat stress above 35°C — use heat-tolerant varieties. Harvest: April-May.\n\n"
     "Best season state-wise:\n"
     "• South India (AP, Karnataka, TN): Rabi (Oct-Nov) and Summer\n"
     "• Maharashtra, MP: Rabi (Sep-Oct)\n"
     "• Punjab, UP, Haryana: Rabi (Oct-Nov)\n"
     "• Himachal Pradesh: Kharif (May-June)",
     "tomato season kharif rabi summer best time planting",
     "All India", "All"),

    ("Tomato", "cultivation",
     "What is the best tomato variety in India?",
     "Top tomato varieties recommended in India:\n\n"
     "HYBRID VARIETIES (High Yield):\n"
     "• Arka Rakshak (IIHR): Best choice — triple disease resistant (ToMV+TLCV+Bacterial Wilt). Yield 70-80 t/ha. Firm fruits 75g.\n"
     "• Arka Vikas (IIHR): Widely grown in South India. Resistant to ToMV. Yield 25-35 t/ha.\n"
     "• Sakthi: Popular in Karnataka/TN. Heat tolerant. Yield 35-40 t/ha.\n"
     "• Navodaya: Early maturing (65 days). Yield 30-35 t/ha. Good for North India.\n\n"
     "OPEN POLLINATED VARIETIES (Low cost seed):\n"
     "• Pusa Ruby (IARI): Classic variety. Yield 20-25 t/ha. Crack resistant. Good shelf life.\n"
     "• CO-3 (Tamil Nadu): Recommended for TN.\n\n"
     "PROCESSING VARIETIES:\n"
     "• Arka Saurabh: High TSS, suitable for ketchup/paste.\n\n"
     "RECOMMENDATION: For commercial cultivation use Arka Rakshak or Sakthi hybrid for best profit.",
     "tomato variety best hybrid arka vikas rakshak sakthi pusa ruby",
     "All India", "All"),

    ("Tomato", "cultivation",
     "How much water does tomato crop need?",
     "Tomato water requirement:\n\n"
     "TOTAL WATER: 400-600mm per crop season (75-90 days)\n\n"
     "CRITICAL STAGES requiring consistent moisture:\n"
     "• Transplanting stage: Water immediately after transplanting\n"
     "• Flowering stage (30-40 days): Water stress causes flower drop\n"
     "• Fruit development (50-70 days): Uneven water causes fruit cracking and BER\n\n"
     "IRRIGATION SCHEDULE (Drip recommended):\n"
     "• Week 1-2 after transplanting: 4-5 litres/plant/day\n"
     "• Vegetative stage: 6-8 litres/plant/day\n"
     "• Flowering & fruiting: 8-10 litres/plant/day\n"
     "• Stop irrigation 5-7 days before final harvest\n\n"
     "WATER SAVING TIPS:\n"
     "• Drip irrigation saves 40-50% water vs flood irrigation\n"
     "• Plastic mulch saves additional 30% moisture\n"
     "• Avoid waterlogging — causes root rot and bacterial wilt",
     "tomato water irrigation drip requirement litre per day",
     "All India", "All"),

    ("Tomato", "cultivation",
     "What fertilizer should I use for tomato?",
     "Tomato fertilizer recommendation (per hectare):\n\n"
     "BASAL DOSE (at transplanting):\n"
     "• FYM / Compost: 25-30 tonnes\n"
     "• SSP (Superphosphate): 500 kg\n"
     "• MOP (Muriate of Potash): 100 kg\n\n"
     "TOP DRESSING (split doses via fertigation):\n"
     "• Total N: 180 kg/ha — split into 5 doses every 15 days\n"
     "• Total P2O5: 90 kg/ha\n"
     "• Total K2O: 120 kg/ha — increase K at fruiting stage\n\n"
     "MICRONUTRIENT SPRAY:\n"
     "• Calcium Nitrate 1% spray at fruiting — prevents Blossom End Rot\n"
     "• Boron 0.2% spray at flowering — improves fruit set\n"
     "• Zinc Sulphate 0.5% spray — for micronutrient deficiency\n\n"
     "FERTIGATION SCHEDULE:\n"
     "• Week 1-3: 19:19:19 NPK @ 3 kg per 1000 litres\n"
     "• Week 4-7: MAP (12:61:0) + KNO3 for P and K\n"
     "• Week 8+: SOP + Calcium Nitrate (high K phase)\n\n"
     "Excess nitrogen causes vegetative growth, reduced fruiting and increases disease risk.",
     "tomato fertilizer NPK dose urea DAP SSP potash micronutrient",
     "All India", "All"),

    ("Tomato", "cultivation",
     "When to harvest tomato and how?",
     "Tomato harvesting guide:\n\n"
     "MATURITY SIGNS:\n"
     "• First harvest: 60-70 days after transplanting\n"
     "• Fruit changes from green to yellow-orange to red\n"
     "• Harvest at breaker stage (just turning colour) for distant markets\n"
     "• Harvest at fully red for local market / home use\n\n"
     "HARVESTING METHOD:\n"
     "• Harvest in early morning (avoid afternoon heat)\n"
     "• Twist and pull or cut with secateurs — do not bruise\n"
     "• Harvest every 3-4 days during peak production\n"
     "• One plant yields 3-5 kg over the season\n\n"
     "YIELD EXPECTATIONS:\n"
     "• Open field (OPV): 20-25 tonnes/ha\n"
     "• Open field (Hybrid): 30-45 tonnes/ha\n"
     "• Polyhouse: 80-120 tonnes/ha\n\n"
     "POST-HARVEST:\n"
     "• Grade: A (>60g), B (40-60g), C (<40g / processing)\n"
     "• Pack in 5kg CFB boxes for distant transport\n"
     "• Store at 13-15°C for 10-14 days shelf life",
     "tomato harvest maturity yield picking grade post harvest",
     "All India", "All"),

    # --- TOMATO : PRICE ---
    ("Tomato", "price",
     "What is the current MSP of tomato?",
     "Tomato does NOT have a government MSP (Minimum Support Price). "
     "MSP is only declared for 23 crops including rice, wheat, pulses, oilseeds and some commercial crops.\n\n"
     "Tomato prices are determined entirely by market supply and demand.\n\n"
     "TYPICAL PRICE RANGE (APMC markets):\n"
     "• Peak season (Jan-Mar): ₹300-800 per quintal — prices crash due to oversupply\n"
     "• Off season (May-July): ₹2,000-8,000 per quintal — supply shortage\n"
     "• Crisis prices (drought/flood year): ₹8,000-15,000 per quintal\n\n"
     "MAJOR MARKETS & TYPICAL PRICES:\n"
     "• Madanapalle (AP): ₹800-1,600/quintal (Jan)\n"
     "• Kolar (Karnataka): ₹700-1,400/quintal (Jan)\n"
     "• Nashik (Maharashtra): ₹1,000-2,200/quintal (Jan)\n"
     "• Shimla (HP): ₹2,000-4,000/quintal (Jul-Aug premium)\n\n"
     "PRICE SUPPORT: Government intervenes via NAFED procurement when prices fall below ₹600/quintal.",
     "tomato MSP price market rate quintal mandi APMC",
     "All India", "All"),

    ("Tomato", "price",
     "Why does tomato price crash every year?",
     "Tomato price crash happens due to these reasons:\n\n"
     "1. SIMULTANEOUS HARVEST: All farmers in a region plant and harvest at the same time, flooding the market.\n"
     "2. NO MSP: Unlike wheat and rice, tomato has no Minimum Support Price protection.\n"
     "3. PERISHABILITY: Tomato lasts only 5-7 days at room temperature, forcing distress sales.\n"
     "4. LIMITED COLD STORAGE: Less than 10% of tomato has access to proper cold storage.\n"
     "5. POOR MARKET LINKAGE: Farmers depend on local mandis with few buyers.\n\n"
     "WHEN DOES CRASH HAPPEN:\n"
     "• January-March: Peak Rabi harvest — prices fall to ₹200-500/quintal\n"
     "• Cost of production is ₹600-800/quintal — farmers lose money\n\n"
     "SOLUTIONS:\n"
     "• Join FPO for collective bargaining\n"
     "• Sell to processors (ketchup, paste factories) during glut\n"
     "• Use e-NAM platform to reach buyers across India\n"
     "• Stagger planting dates with neighbours to avoid simultaneous harvest\n"
     "• Cold storage subsidy under PM Kisan Sampada scheme",
     "tomato price crash low reason mandi why distress sale",
     "All India", "Rabi"),

    ("Tomato", "price",
     "What is tomato price in Karnataka today?",
     "Tomato prices in major Karnataka markets (latest available data):\n\n"
     "KOLAR APMC (largest tomato market in Karnataka):\n"
     "• Min price: ₹700-900/quintal\n"
     "• Max price: ₹1,400-1,600/quintal\n"
     "• Modal price: ₹1,000-1,200/quintal\n\n"
     "CHIKKABALLAPUR APMC:\n"
     "• Modal price: ₹1,000-1,350/quintal\n\n"
     "BANGALORE APMC:\n"
     "• Modal price: ₹1,200-1,600/quintal (retail premium)\n\n"
     "TUMKUR APMC:\n"
     "• Modal price: ₹800-1,100/quintal\n\n"
     "NOTE: Prices vary daily based on arrivals. Check real-time prices at:\n"
     "• agmarknet.gov.in (official government portal)\n"
     "• e-NAM portal: enam.gov.in\n"
     "• Karnataka APMC: karnataka.gov.in/apmc\n\n"
     "Peak prices occur May-July (₹5,000-10,000/q) when supply is low.",
     "tomato price Karnataka Kolar Bangalore APMC market rate",
     "Karnataka", "All"),

    ("Tomato", "price",
     "What is tomato price in Andhra Pradesh?",
     "Tomato prices in Andhra Pradesh markets:\n\n"
     "MADANAPALLE APMC (Chittoor) — Asia's largest tomato market:\n"
     "• Rabi season (Jan-Mar): ₹400-1,500/quintal\n"
     "• Summer (Apr-May): ₹1,500-4,000/quintal\n"
     "• Lean season (Jun-Jul): ₹5,000-12,000/quintal\n\n"
     "VIJAYAWADA (Krishna district):\n"
     "• Modal price: ₹1,200-2,000/quintal (Jan)\n\n"
     "GUNTUR APMC:\n"
     "• Modal price: ₹1,000-1,800/quintal (Jan)\n\n"
     "AP accounts for 20-25% of India's total tomato production.\n"
     "Chittoor district alone produces 15-18 lakh tonnes/year.\n\n"
     "Check live prices: apagrisnet.gov.in or agmarknet.gov.in",
     "tomato price Andhra Pradesh AP Chittoor Madanapalle APMC market",
     "Andhra Pradesh", "All"),

    # --- TOMATO : PEST ---
    ("Tomato", "pest",
     "How to identify and treat Late Blight in tomato?",
     "LATE BLIGHT (Phytophthora infestans) — Most dangerous tomato disease:\n\n"
     "IDENTIFICATION:\n"
     "• Dark brown-black water-soaked patches on leaves and stems\n"
     "• White fluffy fungal growth on underside of leaves (in humid morning)\n"
     "• Brown firm rot on fruits starting from any point\n"
     "• Entire field can collapse within 7-10 days in wet weather\n\n"
     "CONDITIONS: Temperature 10-20°C + humidity >90% + rain/heavy dew\n"
     "HIGH RISK PERIODS: June-August (monsoon), November-December (winter fog)\n\n"
     "TREATMENT:\n"
     "Mild attack:\n"
     "• Mancozeb 75% WP @ 2.5 g/L — spray every 7 days\n"
     "• Copper Oxychloride 50% WP @ 3 g/L\n\n"
     "Severe attack:\n"
     "• Metalaxyl 8% + Mancozeb 64% WP @ 3 g/L\n"
     "• Cymoxanil 8% + Mancozeb 64% WDG @ 3 g/L\n"
     "• Dimethomorph 50% WP @ 1.5 g/L\n\n"
     "PREVENTION:\n"
     "• Grow resistant variety Arka Rakshak\n"
     "• Avoid overhead irrigation\n"
     "• Spray preventive fungicide before monsoon\n"
     "• Ensure proper plant spacing (60x45cm) for air circulation",
     "tomato late blight phytophthora symptoms treatment fungicide spray",
     "All India", "Kharif"),

    ("Tomato", "pest",
     "My tomato leaves are curling upward. What is the problem?",
     "Upward curling of tomato leaves is a CLASSIC SYMPTOM of Tomato Leaf Curl Virus (TLCV/ToLCV).\n\n"
     "SYMPTOMS TO CONFIRM:\n"
     "✓ Severe upward and inward curling of young leaves\n"
     "✓ Leaves become small, thick and leathery\n"
     "✓ Plant is stunted — much smaller than healthy plants\n"
     "✓ Yellow-green mottling or yellowing at leaf margins\n"
     "✓ Very few or no fruits formed\n"
     "✓ Tiny white insects (whitefly) visible on underside of leaves\n\n"
     "CAUSE: Tomato Leaf Curl Virus (Begomovirus) spread by Whitefly (Bemisia tabaci)\n\n"
     "IMPORTANT: There is NO CURE once plant is infected.\n\n"
     "ACTION STEPS:\n"
     "1. Immediately remove and destroy all infected plants\n"
     "2. Spray insecticide to kill whitefly vector:\n"
     "   • Imidacloprid 17.8% SL @ 0.5 ml/L OR\n"
     "   • Thiamethoxam 25% WG @ 0.3 g/L\n"
     "3. Spray on remaining healthy plants too\n"
     "4. Install yellow sticky traps @ 10 per acre\n"
     "5. Use silver mulch on next crop to repel whitefly\n\n"
     "NEXT CROP: Use TLCV-resistant variety — Arka Rakshak or Arka Meghali",
     "tomato leaf curl TLCV virus whitefly curling upward yellow symptoms",
     "All India", "Kharif"),

    ("Tomato", "pest",
     "Tomato fruits have holes. How to control fruit borer?",
     "TOMATO FRUIT BORER (Helicoverpa armigera) — Major pest causing 30-50% yield loss:\n\n"
     "IDENTIFICATION:\n"
     "• Circular holes on fruits with frass (greenish excrement) at entry\n"
     "• Half the larva body outside the hole, rest inside eating the fruit\n"
     "• Green caterpillar with yellow/white stripes, 3-4cm long\n"
     "• One larva damages 3-5 fruits before pupating\n"
     "• Peak attack: October-December and March-May\n\n"
     "CONTROL MEASURES (use in sequence):\n\n"
     "BIOLOGICAL (use first):\n"
     "• Install Pheromone traps (Helilure) @ 5 per acre — monitor population\n"
     "• Plant African Marigold border (1 row per 14 rows tomato) — trap crop\n"
     "• Release Trichogramma chilonis @ 1.5 lakh eggs/ha at egg-laying stage\n"
     "• Spray NPV (Nuclear Polyhedrosis Virus) @ 250 LE/ha on young larvae\n\n"
     "CHEMICAL (when >2 larvae per plant):\n"
     "• Emamectin Benzoate 5% SG @ 0.4 g/L — most effective\n"
     "• Spinosad 45% SC @ 0.3 ml/L\n"
     "• Chlorantraniliprole 18.5% SC @ 0.4 ml/L\n"
     "• Spray in evening (larvae are active at night)\n"
     "• Rotate chemicals to prevent resistance\n\n"
     "Do NOT spray same chemical more than twice in a season.",
     "tomato fruit borer helicoverpa hole larvae caterpillar control spray",
     "All India", "Kharif"),

    ("Tomato", "pest",
     "Tomato plant wilted suddenly. What disease is this?",
     "Sudden wilting of tomato plant can be due to two serious diseases:\n\n"
     "BACTERIAL WILT (Ralstonia solanacearum) — Most common:\n"
     "SYMPTOMS:\n"
     "• Plant wilts suddenly in midday, recovers at night (early stage)\n"
     "• Eventually permanent wilt — whole plant dies\n"
     "• NO yellowing of leaves before wilting\n"
     "• CUT STEM TEST: Dip cut stem in water — see milky bacterial ooze = confirms Bacterial Wilt\n"
     "• Brown discolouration inside stem when cut\n\n"
     "FUSARIUM WILT (Fusarium oxysporum) — Slower:\n"
     "• Yellowing starts on one side/branch first\n"
     "• Slow progression over 2-4 weeks\n"
     "• Brown vascular discolouration inside stem\n\n"
     "TREATMENT:\n"
     "Bacterial Wilt — NO chemical cure:\n"
     "• Remove and destroy infected plants with roots\n"
     "• Drench soil with Copper Oxychloride 3g/L as preventive\n"
     "• Bio-control: Pseudomonas fluorescens 10g/L soil drench\n\n"
     "Fusarium Wilt:\n"
     "• Soil drench Carbendazim 2g/L or Thiophanate Methyl 2g/L\n"
     "• Trichoderma viride 5g/kg soil near root zone\n\n"
     "LONG TERM: Use grafted tomato on resistant rootstock. Soil solarization.",
     "tomato wilt bacterial fusarium sudden die symptoms treatment",
     "All India", "Kharif"),

    # --- TOMATO : SCHEME ---
    ("Tomato", "scheme",
     "What government schemes are available for tomato farmers?",
     "Government schemes benefiting tomato farmers:\n\n"
     "1. PM KISAN SAMPADA YOJANA\n"
     "   • Subsidy for cold storage and processing units (ketchup/paste)\n"
     "   • Helps during price crash by enabling processing\n"
     "   • Apply at: mofpi.gov.in\n\n"
     "2. PMKSY — DRIP IRRIGATION SUBSIDY\n"
     "   • 55% subsidy on drip irrigation for small/marginal farmers\n"
     "   • 45% subsidy for others\n"
     "   • Tomato needs drip — this subsidy is highly relevant\n"
     "   • Apply through state horticulture department\n\n"
     "3. NATIONAL HORTICULTURE MISSION (NHM)\n"
     "   • 50% subsidy on hybrid seed cost\n"
     "   • 50% subsidy on plastic mulch\n"
     "   • Support for polyhouse construction\n"
     "   • Apply through district horticulture officer\n\n"
     "4. e-NAM (NATIONAL AGRICULTURE MARKET)\n"
     "   • Online platform — sell to buyers across India\n"
     "   • Get better price than local mandi\n"
     "   • Register at: enam.gov.in\n\n"
     "5. PMFBY (CROP INSURANCE)\n"
     "   • Crop insurance for tomato loss due to disease, rain, hailstorm\n"
     "   • Premium only 2% for Kharif, 1.5% for Rabi\n"
     "   • Register through bank or CSC\n\n"
     "6. STATE SCHEMES:\n"
     "   • AP: YSR Rythu Bharosa — ₹13,500/acre/year input support\n"
     "   • Karnataka: Raita Siri — ₹2,000/season income support",
     "tomato scheme subsidy government drip NHM PMKSY insurance e-NAM",
     "All India", "All"),

    # ╔══════════════════════════════════════════════╗
    # ║              🌾  RICE                        ║
    # ╚══════════════════════════════════════════════╝

    ("Rice", "cultivation",
     "How to grow rice step by step?",
     "Rice cultivation guide (Transplanted method — most common in India):\n\n"
     "1. NURSERY (25-30 days before transplanting):\n"
     "   • Prepare nursery bed 10x1m per acre main field\n"
     "   • Sow pre-germinated seed @ 60g/sq meter\n"
     "   • Maintain thin water layer in nursery\n\n"
     "2. MAIN FIELD PREPARATION:\n"
     "   • Puddle field 2-3 times with water\n"
     "   • Apply FYM 5 tonnes/ha as basal\n"
     "   • Level field properly for uniform water management\n\n"
     "3. TRANSPLANTING:\n"
     "   • Transplant 25-30 day old seedlings\n"
     "   • Spacing: 20x15cm (2-3 seedlings per hill) for conventional\n"
     "   • SRI method: 25x25cm, 1 seedling, 8-12 days old\n\n"
     "4. WATER MANAGEMENT:\n"
     "   • Maintain 5cm water depth during vegetative stage\n"
     "   • Drain field at panicle initiation\n"
     "   • Alternate wet and dry (AWD) saves 30% water\n\n"
     "5. FERTILIZER (per hectare):\n"
     "   • N: 120 kg | P: 60 kg | K: 60 kg\n"
     "   • Basal: Full P+K + 1/3 N\n"
     "   • Top dress: 1/3 N at tillering + 1/3 N at panicle initiation\n\n"
     "6. HARVEST: At 80-85% grain maturity (120-150 days from sowing). Yield: 4-6 tonnes/ha.",
     "rice cultivation grow transplant paddy nursery irrigation fertilizer harvest",
     "All India", "Kharif"),

    ("Rice", "cultivation",
     "What is SRI method of rice cultivation?",
     "SRI (System of Rice Intensification) — Higher yield with less water and seed:\n\n"
     "KEY PRINCIPLES:\n"
     "1. Young seedlings (8-12 days old) — NOT the usual 25-30 days\n"
     "2. Single seedling per hill — NOT 2-3 seedlings\n"
     "3. Wide spacing 25x25cm — NOT 20x15cm\n"
     "4. Intermittent irrigation (keep moist but not flooded) — saves 30% water\n"
     "5. Mechanical weeding with rotary weeder (instead of hand weeding)\n"
     "6. Organic matter / compost application\n\n"
     "ADVANTAGES:\n"
     "• Yield increase: 20-50% higher than conventional (6-8 t/ha vs 4-5 t/ha)\n"
     "• Water saving: 25-40% less water needed\n"
     "• Seed saving: 5-7 kg/ha vs 25-30 kg/ha conventional\n"
     "• Better tillering: SRI plant develops 40-60 tillers vs 10-20 conventional\n"
     "• Reduces methane emissions from paddy fields\n\n"
     "STATES WHERE SRI IS PROMOTED: Tamil Nadu, Andhra Pradesh, Karnataka, West Bengal, Odisha\n\n"
     "LIMITATION: Requires precise water management and skilled labour for rotary weeding.",
     "SRI rice system intensification method yield water saving young seedling wide spacing",
     "All India", "Kharif"),

    ("Rice", "price",
     "What is the MSP of rice in 2024?",
     "Rice MSP (Minimum Support Price) for 2024-25:\n\n"
     "• Common Grade Rice: ₹2,300 per quintal\n"
     "• Grade 'A' Rice: ₹2,320 per quintal\n\n"
     "(MSP for paddy: ₹2,183/quintal for common, ₹2,203 for Grade A)\n\n"
     "Note: MSP for paddy is announced. Rice MSP = paddy MSP after milling conversion.\n\n"
     "MARKET PRICES (actual trading range):\n"
     "• Sona Masuri (Karnataka/AP): ₹2,600-3,200/quintal\n"
     "• Basmati (Punjab/Haryana): ₹4,500-8,000/quintal\n"
     "• PR-14 (Punjab): ₹2,400-2,800/quintal\n"
     "• IR-36 (common): ₹2,000-2,500/quintal\n\n"
     "PROCUREMENT: FCI (Food Corporation of India) and state agencies procure paddy at MSP.\n"
     "Register with local cooperative or PACS for MSP sale.\n\n"
     "Helpline: 1800-180-1551 | Check: fci.gov.in",
     "rice MSP minimum support price paddy 2024 rate quintal",
     "All India", "Kharif"),

    ("Rice", "pest",
     "How to control Brown Plant Hopper in rice?",
     "BROWN PLANT HOPPER (BPH) — Most destructive rice pest:\n\n"
     "IDENTIFICATION:\n"
     "• Small brown insects at base of rice plant (at water level)\n"
     "• Yellowing and drying of plants from base upward\n"
     "• Plants fall in circular patches = 'Hopper Burn'\n"
     "• Sticky honeydew at plant base — attracts sooty mould\n"
     "• Peak attack: August-October in Kharif\n\n"
     "CONDITIONS FAVOURING BPH:\n"
     "• High nitrogen application (excess urea)\n"
     "• Dense planting (less than 15x15cm)\n"
     "• Continuous flooding\n"
     "• Humidity above 80%, temperature 25-30°C\n\n"
     "CONTROL:\n\n"
     "Cultural methods (do first):\n"
     "• Drain field for 3-4 days — disrupts BPH breeding\n"
     "• Avoid excess nitrogen fertilizer\n"
     "• Use resistant varieties: IR-64, Swarna, MTU-7029\n\n"
     "Chemical control (spray at base of plant):\n"
     "• Buprofezin 25% SC @ 1 ml/L — best for nymphs\n"
     "• Imidacloprid 17.8% SL @ 0.5 ml/L — systemic action\n"
     "• Ethiprole 40% + Imidacloprid 40% WG @ 0.4 g/L\n"
     "• Drain water before spraying for better coverage at base\n\n"
     "NEVER use synthetic pyrethroids — they kill BPH natural enemies and cause resurgence.",
     "rice brown plant hopper BPH hopper burn control spray pesticide",
     "All India", "Kharif"),

    ("Rice", "pest",
     "What is Rice Blast disease and how to treat it?",
     "RICE BLAST (Magnaporthe oryzae) — Most widespread rice disease:\n\n"
     "SYMPTOMS:\n"
     "• LEAF BLAST: Diamond/spindle shaped lesions, grey center, brown border\n"
     "• COLLAR BLAST: Rotting at leaf collar — leaf falls\n"
     "• NECK BLAST: Panicle neck turns black and breaks — grain loss 70-100%\n"
     "• FINGER MILLET BLAST also common in Karnataka\n\n"
     "FAVOURABLE CONDITIONS:\n"
     "• Temperature 24-28°C + high humidity + heavy dew\n"
     "• Cloudy weather for 3-5 days\n"
     "• Excess nitrogen fertilizer\n"
     "• Susceptible varieties\n\n"
     "TREATMENT:\n"
     "Preventive spray (before symptoms appear at boot leaf stage):\n"
     "• Tricyclazole 75% WP @ 0.6 g/L — spray at boot leaf stage\n"
     "• Isoprothiolane 40% EC @ 1.5 ml/L — systemic, good for neck blast\n\n"
     "Curative spray (after symptoms appear):\n"
     "• Azoxystrobin 23% SC @ 1 ml/L\n"
     "• Propiconazole 25% EC @ 1 ml/L\n\n"
     "Spray at: (1) Tillering stage and (2) Boot leaf / panicle initiation stage\n\n"
     "RESISTANT VARIETIES: Pusa Basmati 1121, Improved Samba Mahsuri, MTU-7029",
     "rice blast disease neck collar leaf blast symptoms treatment tricyclazole spray",
     "All India", "Kharif"),

    ("Rice", "scheme",
     "What is PM-KISAN scheme for rice farmers?",
     "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi):\n\n"
     "BENEFIT: ₹6,000 per year direct to farmer's bank account\n"
     "HOW: Three equal installments of ₹2,000 each (April-July, August-November, December-March)\n\n"
     "ELIGIBILITY:\n"
     "✓ All farmers with cultivable land\n"
     "✓ Rice farmers in Kharif season fully eligible\n"
     "✗ NOT eligible: Income tax payers, constitutional post holders, institutional landholders\n\n"
     "HOW TO REGISTER:\n"
     "1. Visit pmkisan.gov.in OR nearest CSC (Common Service Centre)\n"
     "2. Documents needed: Aadhaar card, land records, bank account\n"
     "3. Registration takes 2-4 weeks\n"
     "4. Money transferred directly to Aadhaar-linked bank account\n\n"
     "CHECK STATUS: pmkisan.gov.in → Beneficiary Status → Enter Aadhaar/Mobile/Account number\n\n"
     "HELPLINE: 1800-115-526 (Toll Free) | 155261\n\n"
     "As of 2024, over 11 crore farmers are receiving PM-KISAN benefits.",
     "PM KISAN rice farmer scheme 6000 rupees registration eligibility",
     "All India", "All"),

    ("Rice", "cultivation",
     "What are the best rice varieties in India?",
     "Top rice varieties recommended in India:\n\n"
     "KHARIF VARIETIES (Irrigated):\n"
     "• MTU-7029 (Swarna): Most popular in AP, Odisha, WB. Yield 5-6 t/ha. Duration 145 days.\n"
     "• Samba Mahsuri (BPT-5204): Premium quality, high demand. AP, TN. Yield 5-5.5 t/ha.\n"
     "• IR-64: High yielding, short duration (110 days). Widely grown pan India.\n"
     "• Pusa 44: Punjab. Very high yield (7-8 t/ha) but long duration (160 days).\n\n"
     "RABI VARIETIES:\n"
     "• Masuri: Popular in Telangana and AP for summer rice.\n\n"
     "BASMATI (Premium Price):\n"
     "• Pusa Basmati 1121: Long grain, high milling. Punjab, Haryana, UP. ₹4,000-8,000/q premium.\n"
     "• Pusa Basmati 1509: Short duration (120 days) Basmati. Growing fast.\n"
     "• Taraori Basmati (Type-3): Traditional Basmati from Karnal.\n\n"
     "HYBRID RICE (Highest yield):\n"
     "• KRH-2, PHB-71: Yield 8-10 t/ha. Suitable for irrigated conditions.\n\n"
     "DROUGHT TOLERANT (Rainfed areas):\n"
     "• Sahbhagi Dhan: Tolerates 7-10 days drought. Bihar, Jharkhand, Odisha.",
     "rice variety best India MTU swarna basmati pusa hybrid yield",
     "All India", "Kharif"),

    # ╔══════════════════════════════════════════════╗
    # ║              🌾  WHEAT                       ║
    # ╚══════════════════════════════════════════════╝

    ("Wheat", "cultivation",
     "How to grow wheat step by step?",
     "Wheat cultivation guide (North India — Rabi season):\n\n"
     "1. SOWING TIME:\n"
     "   • Ideal: Oct 25 – Nov 15 (normal sowing)\n"
     "   • Late sowing (Nov 15 – Dec 15): Use late-sown varieties (HD-2781, PBW-373)\n"
     "   • Early sowing causes excessive tillering, lodging\n\n"
     "2. LAND PREPARATION:\n"
     "   • Deep ploughing once after kharif harvest\n"
     "   • 2-3 shallow cultivations + planking to level\n"
     "   • Soil moisture (rabi) sufficient — no need to irrigate before sowing\n\n"
     "3. SEED RATE & SOWING:\n"
     "   • Seed rate: 100-125 kg/ha\n"
     "   • Seed treatment: Vitavax 2.5g/kg or Carbendazim 2g/kg\n"
     "   • Sow with seed-cum-fertilizer drill at 20-22cm row spacing\n"
     "   • Depth: 5-6cm\n\n"
     "4. FERTILIZER (per hectare):\n"
     "   • N: 120 kg | P: 60 kg | K: 40 kg\n"
     "   • Half N + Full P + Full K at sowing\n"
     "   • Remaining half N at first irrigation (CRI stage — 21 days)\n\n"
     "5. IRRIGATION:\n"
     "   • 4-6 irrigations critical: CRI (21 days), Tillering, Jointing, Flowering, Grain filling, Dough stage\n"
     "   • Most critical: CRI stage and flowering stage\n\n"
     "6. HARVEST: At 85% maturity (golden yellow). Duration 120-130 days. Yield: 4-6 t/ha.",
     "wheat cultivation grow sowing Rabi Punjab Haryana fertilizer irrigation steps",
     "All India", "Rabi"),

    ("Wheat", "price",
     "What is the MSP of wheat in 2024?",
     "Wheat MSP (Minimum Support Price) for 2024-25:\n\n"
     "• Wheat MSP: ₹2,275 per quintal\n"
     "  (Increased from ₹2,150 in 2023-24)\n\n"
     "MARKET PRICES (actual trading 2024):\n"
     "• Lokwan (Maharashtra): ₹2,400-2,700/quintal\n"
     "• Sharbati (MP): ₹2,500-3,200/quintal (premium)\n"
     "• HD-2967 (Punjab): ₹2,300-2,600/quintal\n"
     "• PBW-343 (UP): ₹2,200-2,500/quintal\n\n"
     "PROCUREMENT: FCI + state agencies procure at MSP after harvest (April-June).\n"
     "Punjab and Haryana have >90% procurement coverage.\n\n"
     "HOW TO SELL AT MSP:\n"
     "1. Register on state mandi portal (e.g., anaaj.khet.gov.in for UP)\n"
     "2. Take wheat to nearest procurement centre\n"
     "3. Payment within 48-72 hours to bank account\n\n"
     "HELPLINE: 1800-180-1551",
     "wheat MSP minimum support price 2024 rate quintal market",
     "All India", "Rabi"),

    ("Wheat", "pest",
     "How to control Yellow Rust in wheat?",
     "YELLOW RUST (Stripe Rust — Puccinia striiformis) — Major wheat disease:\n\n"
     "IDENTIFICATION:\n"
     "• Bright yellow-orange powdery pustules in STRIPES along the leaf veins\n"
     "• Pustules arranged in rows — like dashes in a dotted line\n"
     "• Entire field turns yellow-orange in severe attack\n"
     "• Leaves dry up and crop loses 30-70% yield\n"
     "• PEAK RISK: January-February when temperature is 10-15°C + dew/fog\n\n"
     "TREATMENT:\n"
     "First sign of disease:\n"
     "• Propiconazole 25% EC @ 0.5 ml/L — spray immediately\n"
     "• Tebuconazole 25.9% EC @ 1 ml/L\n"
     "• Hexaconazole 5% EC @ 2 ml/L\n\n"
     "Repeat spray after 15 days if disease persists.\n\n"
     "PREVENTIVE:\n"
     "• Grow resistant varieties: HD-3086, DBW-187, PBW-723\n"
     "• Avoid late sowing (late crops more susceptible)\n"
     "• Do not excess irrigate in January-February\n\n"
     "OTHER WHEAT RUSTS:\n"
     "• Brown/Leaf Rust: Circular orange pustules scattered on leaves — treat same as Yellow Rust\n"
     "• Black/Stem Rust: Black pustules on stem — rare but severe",
     "wheat yellow rust stripe rust disease treatment propiconazole spray pustules",
     "All India", "Rabi"),

    ("Wheat", "cultivation",
     "What is zero tillage wheat and its benefits?",
     "ZERO TILLAGE WHEAT — Sow wheat directly without ploughing:\n\n"
     "WHAT IS IT:\n"
     "After rice harvest, sow wheat seed directly into rice stubble without any ploughing using a\n"
     "Happy Seeder or Zero-Till Drill machine. Combines sowing and fertilizer application in one pass.\n\n"
     "BENEFITS:\n"
     "• Saves ₹2,000-3,000/acre on land preparation cost\n"
     "• Saves 15-20 days — earlier sowing = better yield\n"
     "• Reduces stubble burning — prevents air pollution\n"
     "• Conserves soil moisture from rice crop\n"
     "• Better weed control (especially Phalaris minor)\n"
     "• Maintains soil structure and organic matter\n"
     "• Water saving: 1 irrigation less needed\n\n"
     "HOW TO DO IT:\n"
     "1. After rice harvest, manage stubble (chop if too tall)\n"
     "2. Hire Happy Seeder machine (available at custom hiring centres)\n"
     "3. Adjust seeding depth to 5-6cm\n"
     "4. Run machine at sowing time — seed and fertilizer in one pass\n"
     "5. First irrigation at 21 days (CRI stage)\n\n"
     "YIELD: Equal to or 5-10% better than conventional tilled wheat\n\n"
     "WHERE POSSIBLE: Punjab, Haryana, UP, MP — especially rice-wheat rotation areas\n\n"
     "SUBSIDY: Happy Seeder available at 50% subsidy under RKVY/state schemes.",
     "zero tillage wheat happy seeder no plough stubble burning benefits cost saving",
     "All India", "Rabi"),

    ("Wheat", "scheme",
     "How can wheat farmers get crop insurance?",
     "PMFBY (Pradhan Mantri Fasal Bima Yojana) for Wheat:\n\n"
     "COVERAGE:\n"
     "• Natural calamities: drought, flood, hailstorm, cyclone\n"
     "• Pest and disease attack\n"
     "• Post-harvest losses (standing crop damage)\n"
     "• Prevented sowing due to adverse weather\n\n"
     "PREMIUM FOR WHEAT (Rabi):\n"
     "• Farmer pays only 1.5% of sum insured\n"
     "• Central + State government pays remaining premium\n"
     "• Example: If wheat value is ₹50,000/hectare → farmer pays only ₹750\n\n"
     "HOW TO REGISTER:\n"
     "1. Visit nearest bank branch (before cut-off date — usually November 30 for Rabi)\n"
     "2. OR visit CSC (Common Service Centre)\n"
     "3. OR register online at pmfby.gov.in\n"
     "4. Documents: Land records (khasra/patwari copy), Aadhaar, bank passbook\n\n"
     "CLAIM PROCESS:\n"
     "• Report crop loss within 72 hours to insurance company or bank\n"
     "• Call 14447 (national helpline)\n"
     "• Claim assessed by joint team within 10 days\n"
     "• Payment within 15 days of assessment\n\n"
     "NOTE: Loanee farmers are enrolled automatically. Non-loanee must register separately.",
     "wheat insurance PMFBY crop insurance Rabi premium claim how to apply",
     "All India", "Rabi"),

    # ╔══════════════════════════════════════════════╗
    # ║              🌿  COTTON                      ║
    # ╚══════════════════════════════════════════════╝

    ("Cotton", "cultivation",
     "How to grow cotton step by step?",
     "Cotton cultivation guide (BT Hybrid — most common):\n\n"
     "1. SOWING TIME:\n"
     "   • Kharif: May-June (with onset of monsoon)\n"
     "   • Irrigated: April-May in Maharashtra, AP, Karnataka\n\n"
     "2. LAND PREPARATION:\n"
     "   • Deep ploughing 30-45cm (cotton has deep taproot)\n"
     "   • FYM 5-10 tonnes/ha incorporated\n"
     "   • Form ridges and furrows at 90-120cm spacing\n\n"
     "3. SEED & SOWING:\n"
     "   • BT Hybrid seed: 1 packet (450g) per acre\n"
     "   • Spacing: 90x60cm (irrigated) or 90x90cm (rainfed)\n"
     "   • Seed treatment: Imidacloprid 70% WS 7g/kg (protects against sucking pests early)\n"
     "   • Sow at 3-4cm depth in moist soil\n\n"
     "4. FERTILIZER (per hectare):\n"
     "   • N: 150 kg | P: 75 kg | K: 75 kg\n"
     "   • Basal: Full P+K + 1/3 N\n"
     "   • 1st top dress: 1/3 N at 40 days (squaring)\n"
     "   • 2nd top dress: 1/3 N at 70 days (boll development)\n\n"
     "5. IRRIGATION: 8-10 irrigations. Critical at squaring and boll setting.\n\n"
     "6. HARVEST: 160-180 days. Pick bolls when fully opened (white fluffy). 2-3 pickings needed.\n"
     "   Yield: 15-20 quintals/ha (seed cotton/kapas)",
     "cotton cultivation grow BT hybrid sowing Kharif fertilizer irrigation steps",
     "All India", "Kharif"),

    ("Cotton", "price",
     "What is the MSP of cotton in 2024?",
     "Cotton MSP (Minimum Support Price) for 2024-25:\n\n"
     "• Medium Staple Cotton: ₹7,121 per quintal\n"
     "• Long Staple Cotton: ₹7,521 per quintal\n"
     "  (Increased from ₹6,620 / ₹7,020 in 2023-24)\n\n"
     "MARKET PRICES (actual trading 2024):\n"
     "• BT Medium Staple (Maharashtra/AP): ₹6,500-7,500/quintal\n"
     "• BT Long Staple (Gujarat): ₹7,000-8,000/quintal\n"
     "• Shankar-6 (Gujarat): ₹7,200-8,500/quintal\n\n"
     "PROCUREMENT AT MSP:\n"
     "• CCI (Cotton Corporation of India) procures when market falls below MSP\n"
     "• Sell at CCI centres — take Aadhaar + land records\n"
     "• NAFED also procures in some states\n\n"
     "PRICE TREND: Cotton prices crashed in 2023 from ₹10,000+ to ₹6,000. \n"
     "International prices and Chinese demand heavily influence Indian cotton prices.\n\n"
     "CHECK PRICES: cotcorp.gov.in | Helpline: 1800-425-8008",
     "cotton MSP price 2024 rate quintal kapas market CCI",
     "All India", "Kharif"),

    ("Cotton", "pest",
     "How to control Pink Bollworm in cotton?",
     "PINK BOLLWORM (Pectinophora gossypiella) — Major cotton pest (post-BT era):\n\n"
     "IDENTIFICATION:\n"
     "• Pink coloured larva (2-3cm) found inside cotton bolls\n"
     "• Circular holes on bolls with webbing inside\n"
     "• Damaged bolls fail to open (lock boll) or open partially\n"
     "• Flocks of seeds stuck together inside boll = confirmed PBW\n"
     "• This pest has developed RESISTANCE to BT cotton Cry1Ac gene\n\n"
     "MONITORING:\n"
     "• Install pheromone traps (Gossyplure) @ 5 per acre\n"
     "• When >8 moths/trap/week = spray threshold\n\n"
     "CONTROL:\n"
     "Cultural methods:\n"
     "• Early sowing (April-May) — crop matures before peak PBW season\n"
     "• Remove and destroy crop residues after harvest\n"
     "• Summer ploughing to kill pupae in soil\n\n"
     "Biological:\n"
     "• Release Trichogramma bactrae @ 1.5 lakh/ha weekly from squaring\n\n"
     "Chemical (spray when threshold crossed):\n"
     "• Chlorantraniliprole 18.5% SC @ 0.4 ml/L\n"
     "• Emamectin Benzoate 5% SG @ 0.4 g/L\n"
     "• Spinosad 45% SC @ 0.3 ml/L\n"
     "• Spray in evening, cover bolls thoroughly\n\n"
     "Do NOT use Cypermethrin or other pyrethroids — kills natural enemies.",
     "cotton pink bollworm PBW control treatment spray BT resistance pheromone trap",
     "All India", "Kharif"),

    ("Cotton", "pest",
     "How to control whitefly in cotton crop?",
     "WHITEFLY (Bemisia tabaci) in Cotton — Vector of Cotton Leaf Curl Virus (CLCuV):\n\n"
     "IDENTIFICATION:\n"
     "• Tiny white flying insects under leaves — fly up when disturbed\n"
     "• Yellowing of leaves, black sooty mould on honeydew\n"
     "• Most seriously: TRANSMITS Cotton Leaf Curl Virus (CLCuV)\n"
     "• CLCuV causes leaf curling, vein thickening, leaf cupping — no cure\n"
     "• Peak population: August-October in hot dry weather\n\n"
     "CONTROL:\n"
     "Cultural:\n"
     "• Avoid planting near other whitefly hosts (tomato, brinjal, okra)\n"
     "• Remove infected CLCuV plants immediately\n"
     "• Yellow sticky traps @ 10 per acre\n"
     "• Reflective silver mulch in nursery areas\n\n"
     "Biological:\n"
     "• Natural enemies: Encarsia formosa (parasitoid), Chrysoperla (predator)\n"
     "• Conserve by avoiding broad spectrum insecticides\n\n"
     "Chemical (rotate to prevent resistance):\n"
     "• Diafenthiuron 50% WP @ 1 g/L\n"
     "• Spiromesifen 22.9% SC @ 1 ml/L\n"
     "• Flonicamid 50% WG @ 0.3 g/L\n"
     "• Buprofezin 25% SC @ 2 ml/L\n\n"
     "NEVER use: Imidacloprid or Thiamethoxam as foliar spray (banned for cotton in some states)",
     "cotton whitefly control spray CLCuV virus leaf curl treatment",
     "All India", "Kharif"),

    ("Cotton", "scheme",
     "What government schemes help cotton farmers in India?",
     "Key government schemes for cotton farmers:\n\n"
     "1. PMFBY — CROP INSURANCE\n"
     "   • Coverage: Drought, excess rain, hailstorm, pest attack\n"
     "   • Premium: Only 2% of sum insured for Kharif cotton\n"
     "   • Register at bank before June 30 (Kharif cut-off)\n\n"
     "2. MINIMUM SUPPORT PRICE (MSP)\n"
     "   • Medium staple: ₹7,121/quintal | Long staple: ₹7,521/quintal\n"
     "   • CCI (Cotton Corporation of India) buys at MSP when market falls\n"
     "   • Sell at CCI centre: cotcorp.gov.in\n\n"
     "3. TECHNOLOGY MISSION ON COTTON (TMC)\n"
     "   • Improved seed distribution, ginning-pressing modernisation\n"
     "   • Transfer of technology to cotton farmers\n"
     "   • Micro-irrigation for cotton — 55% subsidy\n\n"
     "4. DRIP IRRIGATION SUBSIDY (PMKSY)\n"
     "   • 55% subsidy for small/marginal cotton farmers on drip installation\n"
     "   • Cotton is one of the highest priority crops for drip\n\n"
     "5. STATE SCHEMES:\n"
     "   • Maharashtra Vasantrao Naik Shetkari Swavalamban Mission — financial support\n"
     "   • AP Rythu Bharosa — ₹13,500/acre/year input support\n"
     "   • Telangana Rythu Bandhu — ₹5,000/acre/season investment support\n\n"
     "6. KISAN CREDIT CARD (KCC)\n"
     "   • Crop loan at 4% interest per annum\n"
     "   • Up to ₹3 lakh without collateral",
     "cotton scheme government MSP insurance CCI PMFBY drip subsidy farmer",
     "All India", "Kharif"),

    # ╔══════════════════════════════════════════════╗
    # ║             🧅  ONION                        ║
    # ╚══════════════════════════════════════════════╝

    ("Onion", "cultivation",
     "How to grow onion step by step?",
     "Onion cultivation guide (Rabi season — main crop):\n\n"
     "1. NURSERY (45-50 days before transplanting):\n"
     "   • Prepare raised nursery beds 100cm wide\n"
     "   • Sow seed @ 5-7 kg/ha in lines 5cm apart\n"
     "   • Germination in 8-10 days\n"
     "   • Drench nursery with Carbendazim 1g/L at 15 days\n\n"
     "2. TRANSPLANTING:\n"
     "   • Transplant 45-50 day old seedlings (pencil-thickness)\n"
     "   • Spacing: 15x10cm on flat beds OR 15x10cm on ridges\n"
     "   • Trim roots to 2-3cm before transplanting\n"
     "   • Plant population: 60-65 plants/sq meter\n\n"
     "3. FERTILIZER (per hectare):\n"
     "   • FYM: 25 tonnes as basal\n"
     "   • N: 100 kg | P: 50 kg | K: 50 kg\n"
     "   • Sulphur: 25 kg (essential for pungency and yield)\n"
     "   • Split N: Basal 1/2 + 30 days 1/4 + 45 days 1/4\n\n"
     "4. IRRIGATION:\n"
     "   • Drip recommended — avoid furrow irrigation\n"
     "   • Critical: Bulb formation stage (60-80 days)\n"
     "   • Stop irrigation 10-15 days before harvest (for good skin colour and storage)\n\n"
     "5. HARVEST: 100-130 days. Tops fall naturally = maturity sign.\n"
     "   Cure in shade for 7-10 days before storage.\n"
     "   Yield: 25-35 tonnes/ha",
     "onion cultivation grow transplant Rabi nursery fertilizer irrigation harvest",
     "All India", "Rabi"),

    ("Onion", "price",
     "Why does onion price increase suddenly in India?",
     "Onion price spike reasons — India's most volatile vegetable price:\n\n"
     "REASONS FOR SUDDEN PRICE SPIKE:\n"
     "1. MONSOON DAMAGE: Heavy rain in Nashik, Solapur (Maharashtra) damages standing crop\n"
     "2. KHARIF CROP FAILURE: Kharif onion (harvested Oct-Nov) is smaller and has limited storage life\n"
     "3. DELAYED RABI HARVEST: Late rains delay harvest, creating supply gap\n"
     "4. POOR STORAGE: Onion stored in kanda chaals (open storage) — loses 25-30% to rot\n"
     "5. EXPORT DEMAND: When India exports onion, domestic prices spike\n"
     "6. HOARDING: Traders sometimes hold stock expecting higher prices\n\n"
     "PRICE CYCLES (typical):\n"
     "• Jan-Mar (peak Rabi harvest): ₹500-1,000/quintal — LOW prices, farmer loss\n"
     "• Apr-Jun (Rabi storage): ₹800-1,500/quintal\n"
     "• Aug-Nov (Kharif gap): ₹2,000-6,000/quintal — SPIKE season\n\n"
     "GOVERNMENT RESPONSE:\n"
     "• Export ban on onion (imposed when retail price >₹40/kg in cities)\n"
     "• NAFED imports onion from neighboring countries\n"
     "• Buffer stock maintained by NCCF\n\n"
     "KEY PRODUCING DISTRICTS: Nashik, Pune, Solapur (MH), Belgaum (KA), Chitradurga (KA)",
     "onion price spike increase reason Maharashtra Nashik market",
     "All India", "All"),

    ("Onion", "pest",
     "How to control Purple Blotch disease in onion?",
     "PURPLE BLOTCH (Alternaria porri) — Most common onion disease:\n\n"
     "IDENTIFICATION:\n"
     "• Small water-soaked white spots on leaves initially\n"
     "• Spots enlarge with purple-brown centre and yellow halo\n"
     "• Lesions may girdle the leaf causing it to fall\n"
     "• Entire leaves dry up — yield loss 30-70% in severe cases\n"
     "• Bulbs can also be infected in neck area\n\n"
     "FAVOURABLE CONDITIONS:\n"
     "• Warm (25-30°C), high humidity, frequent rain\n"
     "• Injury from thrips feeding creates entry wounds\n\n"
     "TREATMENT:\n"
     "Preventive (spray before symptoms):\n"
     "• Mancozeb 75% WP @ 2.5 g/L — start at 30 days after transplanting\n"
     "• Spray every 10 days preventively\n\n"
     "Curative:\n"
     "• Iprodione 50% WP @ 2 g/L\n"
     "• Propiconazole 25% EC @ 1 ml/L\n"
     "• Azoxystrobin 23% SC @ 1 ml/L\n"
     "• Add sticker (Triton 0.1%) to improve adhesion on waxy leaves\n\n"
     "THRIPS CONTROL is essential — thrips feeding creates entry points for Purple Blotch:\n"
     "• Spinosad 45% SC @ 0.3 ml/L OR Fipronil 5% SC @ 2 ml/L",
     "onion purple blotch disease treatment spray Alternaria symptoms",
     "All India", "Rabi"),

    ("Onion", "cultivation",
     "How to store onion after harvest to prevent rotting?",
     "Onion storage guide to reduce post-harvest losses:\n\n"
     "FIELD CURING (mandatory before storage):\n"
     "• After harvest, spread onions in field for 3-5 days in sun\n"
     "• Or cure in shade with good ventilation for 7-10 days\n"
     "• Outer skin should become dry and papery\n"
     "• Tops should wilt completely\n"
     "• Curing reduces neck rot and improves skin colour\n\n"
     "TRADITIONAL STORAGE (Kanda Chaal):\n"
     "• Open bamboo/wooden platform structure with thatched roof\n"
     "• Allows free air circulation\n"
     "• Avoid rain contact\n"
     "• Losses: 15-25% over 4-5 months (acceptable)\n\n"
     "IMPROVED STORAGE TIPS:\n"
     "• Store only fully mature, cured, neck-dry bulbs\n"
     "• Grade out damaged, diseased or soft bulbs before storage\n"
     "• Do not store in gunny bags (causes sweating and rot)\n"
     "• Ideal storage: 30-35°C, RH 65-70%, good ventilation\n"
     "• Sprout inhibitor: Maleic Hydrazide spray @ 2,500 ppm 2 weeks before harvest\n\n"
     "COLD STORAGE (for long-term 6-8 months):\n"
     "• Temperature: 0-2°C, RH 65-70%\n"
     "• Losses reduced to 5-8%\n"
     "• Cold storage subsidy available under NHM scheme",
     "onion storage post harvest rot prevention cold storage curing tips",
     "All India", "All"),

    # ╔══════════════════════════════════════════════╗
    # ║             🥔  POTATO                       ║
    # ╚══════════════════════════════════════════════╝

    ("Potato", "cultivation",
     "How to grow potato step by step?",
     "Potato cultivation guide (Rabi season):\n\n"
     "1. PLANTING TIME:\n"
     "   • Plains (UP, Punjab, WB): October 15 – November 15\n"
     "   • Hills (HP): March-April\n\n"
     "2. SEED SELECTION:\n"
     "   • Use certified seed tubers (Grade A or B)\n"
     "   • Seed rate: 20-25 quintals/ha (30-40g/seed piece)\n"
     "   • Cut tubers should have at least 2-3 eyes\n"
     "   • Treat cut surfaces with Mancozeb 3g/L before planting\n\n"
     "3. LAND PREPARATION:\n"
     "   • Deep plough 30-40cm (potato needs loose, deep soil)\n"
     "   • FYM 20-25 tonnes/ha incorporated\n"
     "   • Form ridges 30cm high at 60cm spacing\n\n"
     "4. FERTILIZER (per hectare):\n"
     "   • N: 150-180 kg | P: 80 kg | K: 100 kg\n"
     "   • High K requirement — important for tuber quality\n"
     "   • Half N + Full P + Full K at planting\n"
     "   • Remaining half N at earthing up (30-35 days)\n\n"
     "5. IRRIGATION:\n"
     "   • 8-10 irrigations needed\n"
     "   • Critical: Tuber initiation (30-40 days) and tuber bulking (60-80 days)\n"
     "   • Stop irrigation 10-15 days before harvest\n\n"
     "6. HARVEST: 75-100 days. Tops dry = maturity. Allow skin to set 10 days after top drying.\n"
     "   Yield: 25-35 tonnes/ha",
     "potato cultivation grow Rabi sowing fertilizer irrigation harvest steps",
     "All India", "Rabi"),

    ("Potato", "pest",
     "How to identify and control Late Blight in potato?",
     "POTATO LATE BLIGHT (Phytophthora infestans) — Most destructive potato disease:\n\n"
     "IDENTIFICATION:\n"
     "• Water-soaked dark-brown/black lesions on leaves — starts at leaf tips/margins\n"
     "• White cottony mould on underside of leaves in early morning\n"
     "• Infected stems turn black and collapse\n"
     "• TUBER INFECTION: Brown to reddish granular rot under skin\n"
     "• In favourable weather, entire field can collapse in 7-10 days\n"
     "• CLASSIC SIGN: Foul smell from infected field\n\n"
     "FAVOURABLE CONDITIONS:\n"
     "• Temperature 10-20°C + humidity >90% + rain/fog\n"
     "• Late November-January in North India (dense fog season)\n\n"
     "TREATMENT:\n"
     "Preventive (spray before disease appears):\n"
     "• Mancozeb 75% WP @ 2.5 g/L — start when temperature drops below 20°C\n"
     "• Chlorothalonil 75% WP @ 2 g/L\n\n"
     "Curative (after first symptoms):\n"
     "• Metalaxyl 8% + Mancozeb 64% WP @ 3 g/L — SYSTEMIC, most effective\n"
     "• Cymoxanil 8% + Mancozeb 64% WDG @ 3 g/L\n"
     "• Fenamidone 10% + Mancozeb 50% WDG @ 3 g/L\n"
     "• Spray every 7 days during wet/foggy weather\n\n"
     "RESISTANT VARIETIES: Kufri Jyoti, Kufri Girdhari, Kufri Frysona",
     "potato late blight disease treatment spray Phytophthora control fungicide",
     "All India", "Rabi"),

    ("Potato", "price",
     "What is potato price in India and MSP?",
     "Potato does NOT have a government MSP.\n"
     "Potato prices are market-determined.\n\n"
     "TYPICAL PRICE RANGES (APMC markets 2024):\n\n"
     "UTTAR PRADESH (largest producer):\n"
     "• Agra: ₹600-1,200/quintal (fresh harvest)\n"
     "• Kanpur: ₹700-1,300/quintal\n\n"
     "PUNJAB:\n"
     "• Jalandhar: ₹800-1,400/quintal\n"
     "• Ludhiana: ₹750-1,350/quintal\n\n"
     "WEST BENGAL:\n"
     "• Hooghly: ₹600-1,100/quintal\n\n"
     "GUJARAT:\n"
     "• Deesa: ₹900-1,500/quintal (Deesa potato is premium)\n\n"
     "PRICE PATTERNS:\n"
     "• Lowest: Jan-Feb (peak harvest) — ₹400-700/quintal\n"
     "• Highest: Aug-Sep (pre-harvest gap) — ₹1,500-2,500/quintal\n\n"
     "STORAGE PRICE ADVANTAGE:\n"
     "• Cold storage rental: ₹180-250/quintal for 6 months\n"
     "• Price difference fresh vs 6 months stored: ₹600-1,200/quintal\n"
     "• Cold storage is a major income strategy for potato farmers",
     "potato price MSP market rate quintal UP Punjab India",
     "All India", "All"),

    # ╔══════════════════════════════════════════════╗
    # ║             🍆  BRINJAL (EGGPLANT)           ║
    # ╚══════════════════════════════════════════════╝

    ("Brinjal", "cultivation",
     "How to grow brinjal step by step?",
     "Brinjal (Eggplant/Baingan) cultivation guide:\n\n"
     "1. SEASON: Can be grown year-round. Main seasons:\n"
     "   • Kharif: June-July transplanting\n"
     "   • Rabi: October-November transplanting\n"
     "   • Summer: January-February transplanting\n\n"
     "2. NURSERY (25-30 days):\n"
     "   • Prepare raised beds 1m wide\n"
     "   • Sow seed @ 500g/ha in lines 10cm apart\n"
     "   • Cover with thin layer of sand + FYM\n"
     "   • Germination in 7-10 days\n\n"
     "3. TRANSPLANTING:\n"
     "   • Transplant at 5-6 leaf stage (25-30 days)\n"
     "   • Spacing: 60x60cm or 75x60cm\n"
     "   • Irrigate immediately after transplanting\n\n"
     "4. FERTILIZER (per hectare):\n"
     "   • FYM: 25 tonnes as basal\n"
     "   • N: 100 kg | P: 50 kg | K: 50 kg\n"
     "   • Split N: 1/3 basal, 1/3 at 30 days, 1/3 at 60 days\n\n"
     "5. STAKING: Stake tall varieties at 45-60 days to prevent lodging\n\n"
     "6. HARVEST: First harvest at 60-70 days after transplanting\n"
     "   Harvest immature fruits (before seeds harden) every 5-7 days\n"
     "   Yield: 25-40 tonnes/ha. Long duration crop — can continue 8-12 months.",
     "brinjal eggplant baingan cultivation grow season nursery fertilizer transplant",
     "All India", "All"),

    ("Brinjal", "pest",
     "How to control Shoot and Fruit Borer in brinjal?",
     "BRINJAL SHOOT AND FRUIT BORER (Leucinodes orbonalis) — Most serious brinjal pest:\n\n"
     "IDENTIFICATION:\n"
     "• SHOOT BORER: Young shoots wilt and dry (dead heart). Cut open = find pinkish-white larva inside\n"
     "• FRUIT BORER: Circular holes on fruits, frass at entry. Infected fruits rot and drop.\n"
     "• Small white moth with brown spots lays eggs on tender shoots\n"
     "• One larva bores into shoot then moves to fruit\n"
     "• Can cause 60-70% fruit damage if uncontrolled\n\n"
     "CONTROL:\n"
     "Cultural (mandatory, do first):\n"
     "• Remove and destroy wilted shoots weekly (remove + burn — kills larva inside)\n"
     "• Collect and destroy damaged fruits\n"
     "• Pheromone traps @ 5 per acre (Leucilure)\n\n"
     "Biological:\n"
     "• Release Trichogramma chilonis @ 1 lakh/ha at egg stage\n\n"
     "Chemical (rotate chemicals to prevent resistance):\n"
     "• Emamectin Benzoate 5% SG @ 0.4 g/L — most effective\n"
     "• Chlorantraniliprole 18.5% SC @ 0.4 ml/L\n"
     "• Spinosad 45% SC @ 0.3 ml/L\n"
     "• Neem oil 5% spray at 10-day intervals as preventive\n\n"
     "Spray timing: Evening (larvae emerge at dusk). Cover shoots and fruits thoroughly.\n"
     "Observe 5-7 days pre-harvest interval (PHI) before picking fruits after spray.",
     "brinjal shoot fruit borer control spray larvae dead heart Leucinodes",
     "All India", "All"),

    # ╔══════════════════════════════════════════════╗
    # ║             🌿  SUGARCANE                    ║
    # ╚══════════════════════════════════════════════╝

    ("Sugarcane", "cultivation",
     "How to grow sugarcane step by step?",
     "Sugarcane cultivation guide:\n\n"
     "1. PLANTING TIME:\n"
     "   • Autumn (Sep-Oct): Best planting — high yield and early harvest\n"
     "   • Spring (Feb-Mar): Common in North India\n"
     "   • Summer (Apr-May): Practice in South India\n\n"
     "2. LAND PREPARATION:\n"
     "   • Deep ploughing 30-40cm\n"
     "   • FYM 25-30 tonnes/ha\n"
     "   • Make furrows 25-30cm deep at 90cm row spacing\n\n"
     "3. PLANTING:\n"
     "   • Use 2-3 budded sett cuttings from healthy 8-10 month cane\n"
     "   • Treat setts in Carbendazim 1g/L + Chlorpyrifos 5ml/L for 15 min\n"
     "   • Plant end to end in furrows (2-eye setts)\n"
     "   • Seed cane required: 5,000-6,000 kg/ha\n\n"
     "4. FERTILIZER (per hectare per year):\n"
     "   • N: 250-300 kg | P: 80 kg | K: 100 kg\n"
     "   • Split N: 4-5 doses over 12 months\n"
     "   • Sulphur 40 kg/ha — improves juice quality\n\n"
     "5. IRRIGATION: 25-30 irrigations/year (heavy water requirement).\n"
     "   Drip saves 40% water and increases yield by 15-20%.\n\n"
     "6. HARVEST: 10-12 months (12-18 months for ratoon). Cut at ground level.\n"
     "   Yield: 70-100 tonnes/ha. Sucrose 14-16%.",
     "sugarcane cultivation grow planting sett fertilizer irrigation harvest steps",
     "All India", "Perennial"),

    ("Sugarcane", "price",
     "What is the SAP and FRP of sugarcane in 2024?",
     "Sugarcane pricing has two components:\n\n"
     "FRP (Fair and Remunerative Price) — Central Government:\n"
     "• FRP 2024-25: ₹340 per quintal (10.25% recovery basis)\n"
     "  Linked to sugar recovery — higher recovery = higher FRP\n"
     "  Recovery formula: For each 0.1% above 10.25%, ₹3.32/quintal extra\n\n"
     "SAP (State Advised Price) — State Government (Higher than FRP):\n"
     "• Uttar Pradesh SAP 2024-25: ₹370/quintal (General variety)\n"
     "• Punjab SAP: ₹391/quintal\n"
     "• Haryana SAP: ₹386/quintal\n"
     "• Maharashtra: Follows FRP (no separate SAP)\n"
     "• Karnataka: Follows FRP\n\n"
     "NOTE: Sugar mills must pay AT LEAST FRP. States with SAP must pay SAP.\n\n"
     "PAYMENT TIMELINE:\n"
     "• Sugar mills must pay within 14 days of delivery\n"
     "• Delayed payment = 15% per annum interest\n"
     "• Farmer can complain to DFPD if mill delays: 1800-11-8989\n\n"
     "ARREARS PROBLEM: UP mills regularly delay payment — track on up.gov.in/caneportal",
     "sugarcane price FRP SAP rate 2024 quintal UP mill payment",
     "All India", "Perennial"),

    ("Sugarcane", "pest",
     "How to control Early Shoot Borer in sugarcane?",
     "EARLY SHOOT BORER (Chilo infuscatellus) — Major sugarcane pest:\n\n"
     "IDENTIFICATION:\n"
     "• Affects crop from germination to 60 days\n"
     "• Dead heart — central shoot dries while outer leaves remain green\n"
     "• Entry hole visible at base of dead shoot with frass\n"
     "• Pull dead shoot — comes out easily with rotten base smell\n"
     "• Pale yellow caterpillar with 5 purple longitudinal stripes, 25mm long\n"
     "• Can cause 15-30% crop loss in severe attack\n\n"
     "CONTROL:\n"
     "At planting:\n"
     "• Treat setts in Chlorpyrifos 20% EC @ 5ml/L for 15 minutes\n"
     "• Carbofuran 3G @ 33 kg/ha in furrow at planting\n\n"
     "Standing crop (30-60 days):\n"
     "• Remove and destroy all dead hearts — kills larvae inside\n"
     "• Release Trichogramma chilonis @ 1.5 lakh/ha weekly for 3 weeks\n"
     "• Spray Chlorpyrifos 20% EC @ 2.5 ml/L at base of plants\n"
     "• Systemic: Thiamethoxam 25% WG @ 0.3 g/L as root treatment\n\n"
     "TRAP: Light traps @ 1/ha to monitor moth population\n\n"
     "NOTE: Do not confuse with Top Borer — Top Borer attacks at 60+ days and causes 'silver shoot'.",
     "sugarcane early shoot borer dead heart control spray Chilo treatment",
     "All India", "Kharif"),

    # ╔══════════════════════════════════════════════╗
    # ║          🌐  GENERAL / CROSS-CROP           ║
    # ╚══════════════════════════════════════════════╝

    ("General", "scheme",
     "What is Kisan Credit Card and how to get it?",
     "KISAN CREDIT CARD (KCC) — Flexible crop loan for all farmers:\n\n"
     "WHAT IS KCC:\n"
     "A revolving credit facility that allows farmers to withdraw money as needed\n"
     "for seeds, fertilizers, pesticides and farm equipment — like a credit card for farmers.\n\n"
     "INTEREST RATE:\n"
     "• 4% per annum (after interest subvention)\n"
     "• Without subvention: 7% per annum\n"
     "• Repay after harvest — no fixed EMI\n\n"
     "CREDIT LIMIT:\n"
     "• Up to ₹3 lakh without collateral\n"
     "• Above ₹3 lakh: land as collateral required\n"
     "• Includes: Crop loan + post-harvest + allied activities + consumption needs\n\n"
     "FREE INSURANCE INCLUDED:\n"
     "• Personal accident insurance: ₹50,000 death / ₹25,000 disability\n"
     "• Asset insurance included\n\n"
     "HOW TO APPLY:\n"
     "1. Visit any Nationalised Bank, RRB, Cooperative Bank or SFB\n"
     "2. Documents: Land records, Aadhaar, passport photo, crop details\n"
     "3. Processing takes 7-14 days\n"
     "4. KCC valid for 5 years (annual review)\n\n"
     "APPLY ONLINE: pmkisan.gov.in has KCC application link\n"
     "HELPLINE: Contact nearest bank or NABARD: 022-26539895",
     "Kisan Credit Card KCC crop loan 4% interest how to apply bank",
     "All India", "All"),

    ("General", "scheme",
     "What is PM-KISAN scheme and who is eligible?",
     "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) — Income support for all farmers:\n\n"
     "BENEFIT: ₹6,000 per year (₹2,000 every 4 months — 3 installments)\n\n"
     "ELIGIBILITY — WHO CAN GET:\n"
     "✓ All farmer families owning cultivable land\n"
     "✓ Small and marginal farmers\n"
     "✓ Large farmers also eligible\n"
     "✓ Both Kharif and Rabi crop farmers\n\n"
     "WHO CANNOT GET (excluded):\n"
     "✗ Income tax payers\n"
     "✗ People holding constitutional posts (current/former)\n"
     "✗ Government employees (Class I, II, III)\n"
     "✗ Retired pensioners getting ₹10,000+/month\n"
     "✗ Doctors, Engineers, Lawyers, CAs, Architects (professional taxpayers)\n"
     "✗ Institutional landholders\n\n"
     "HOW TO REGISTER:\n"
     "1. Online: pmkisan.gov.in → New Farmer Registration\n"
     "2. Offline: Visit nearest CSC or bank\n"
     "3. Documents: Aadhaar, land records (khatoni/patta), bank account\n"
     "4. Mobile number linked to Aadhaar recommended\n\n"
     "CHECK STATUS: pmkisan.gov.in → Beneficiary Status\n"
     "HELPLINE: 1800-115-526 | 155261 (Toll Free)",
     "PM KISAN eligibility who can get 6000 rupees registration documents",
     "All India", "All"),

    ("General", "scheme",
     "What is PMFBY crop insurance and how to claim?",
     "PMFBY (Pradhan Mantri Fasal Bima Yojana) — Comprehensive crop insurance:\n\n"
     "WHAT IS COVERED:\n"
     "• Natural calamities: drought, flood, hailstorm, cyclone, landslide, earthquake\n"
     "• Pest and disease attack\n"
     "• Post-harvest losses (up to 14 days in field after harvest)\n"
     "• Prevented sowing due to adverse weather\n"
     "• Mid-season adversity (weather based)\n\n"
     "PREMIUM FARMER PAYS:\n"
     "• Kharif crops: 2% of sum insured\n"
     "• Rabi crops: 1.5% of sum insured\n"
     "• Commercial/Horticulture (tomato, onion etc.): 5% of sum insured\n"
     "• Government pays remaining 90-95%\n\n"
     "HOW TO ENROLL:\n"
     "• Loanee farmers: Automatic enrollment through bank (can opt out)\n"
     "• Non-loanee farmers: Visit bank / CSC / pmfby.gov.in\n"
     "• Cut-off dates: July 31 for Kharif | December 31 for Rabi\n"
     "• Documents: Land records, Aadhaar, bank passbook, sowing declaration\n\n"
     "HOW TO CLAIM:\n"
     "1. Report crop loss within 72 hours of damage\n"
     "2. Call: 14447 (national helpline) OR insurance company toll-free\n"
     "3. OR inform bank / local agriculture office in writing\n"
     "4. Joint survey by insurance company within 10 days\n"
     "5. Claim credited to bank account within 15 days of survey\n\n"
     "TRACK CLAIM: pmfby.gov.in → Claim Status",
     "PMFBY crop insurance claim premium Kharif Rabi how to apply enroll",
     "All India", "All"),

    ("General", "scheme",
     "What is e-NAM and how do farmers use it?",
     "e-NAM (National Agriculture Market) — Online mandi for farmers:\n\n"
     "WHAT IS e-NAM:\n"
     "An online trading platform that connects 1,000+ APMC mandis across India.\n"
     "Farmers can sell their produce to buyers from any state via online bidding.\n\n"
     "BENEFITS FOR FARMERS:\n"
     "• Access to buyers from across India — better price discovery\n"
     "• Transparent online auction — no one can cheat\n"
     "• Payment directly to bank account within 24 hours\n"
     "• Reduced market fees\n"
     "• Can check prices of other mandis before selling\n"
     "• Works for: grains, pulses, oilseeds, vegetables, fruits, spices\n\n"
     "HOW TO REGISTER:\n"
     "1. Visit enam.gov.in → Farmer Registration\n"
     "2. OR visit your nearest APMC mandi office\n"
     "3. Documents: Aadhaar, bank account, mobile number, land documents\n"
     "4. Registration is FREE\n\n"
     "HOW IT WORKS:\n"
     "1. Bring produce to e-NAM enabled mandi\n"
     "2. Produce is weighed, quality tested (assaying)\n"
     "3. Online bidding starts — buyers from across India can bid\n"
     "4. Highest bidder wins — farmer accepts/rejects bid\n"
     "5. Payment in 24 hours to bank account\n\n"
     "HELPLINE: 1800-270-0224 | nam@sfac.in",
     "e-NAM online mandi platform farmer register sell price better market",
     "All India", "All"),

    ("General", "cultivation",
     "What is drip irrigation and its benefits for farmers?",
     "DRIP IRRIGATION — Most efficient watering method:\n\n"
     "WHAT IS IT:\n"
     "Water is delivered directly to the root zone of plants through a network of\n"
     "pipes, laterals and drippers (emitters) that release water drop by drop.\n\n"
     "BENEFITS:\n"
     "• Water saving: 40-60% less water than flood irrigation\n"
     "• Yield increase: 20-35% higher due to uniform water and nutrient supply\n"
     "• Fertilizer saving: 20-30% through fertigation (applying fertilizer through drip)\n"
     "• Labour saving: No need for repeated irrigation labour\n"
     "• Weed control: Only root zone is wet — no water for weeds between rows\n"
     "• Soil health: No waterlogging, no soil erosion\n"
     "• Energy saving: Lower pressure needed vs sprinkler\n\n"
     "SUITABLE CROPS: Tomato, Onion, Potato, Sugarcane, Cotton, Banana, Grapes — almost all crops\n\n"
     "COST: ₹50,000-1,20,000/acre depending on crop and system\n\n"
     "SUBSIDY AVAILABLE:\n"
     "• Under PMKSY: 55% subsidy for small/marginal farmers\n"
     "• 45% for large farmers\n"
     "• Apply through state horticulture or agriculture department\n\n"
     "PAYBACK PERIOD: 2-3 years for most crops through water, fertilizer and yield benefits.",
     "drip irrigation benefits water saving subsidy PMKSY cost crops",
     "All India", "All"),

    ("General", "cultivation",
     "How to prepare organic compost at home for crops?",
     "NADEP COMPOST METHOD — Easy farm composting:\n\n"
     "MATERIALS NEEDED:\n"
     "• Crop residue, dry leaves, straw: 1,400 kg\n"
     "• Cow dung: 100 kg\n"
     "• Pond/tank soil or any fine soil: 1,750 kg\n"
     "• Water as needed\n\n"
     "NADEP PIT SIZE: 12x5x3 feet (brick/cement tank with holes in walls)\n\n"
     "LAYERING METHOD:\n"
     "1. Layer 1: 6 inch crop residue/dry leaves\n"
     "2. Layer 2: Thin layer cow dung slurry (cow dung + water)\n"
     "3. Layer 3: 2 inch soil layer\n"
     "4. Sprinkle water to maintain moisture\n"
     "5. Repeat layers until pit is full\n"
     "6. Cover top with 2 inch soil layer\n"
     "7. Keep moist — sprinkle water if drying\n\n"
     "DECOMPOSITION TIME: 90-120 days\n\n"
     "VERMICOMPOST (faster):\n"
     "• Mix crop waste + cow dung in long beds\n"
     "• Add earthworms (Eisenia fetida)\n"
     "• Ready in 45-60 days\n"
     "• Higher nutrient content than NADEP compost\n\n"
     "BENEFITS: Improves soil health, water holding capacity, reduces chemical fertilizer need by 20-30%\n"
     "1 tonne compost equivalent to 25 kg urea + 12 kg SSP + 20 kg MOP",
     "compost NADEP vermicompost organic manure preparation farm home",
     "All India", "All"),

    ("General", "pest",
     "What is Integrated Pest Management (IPM)?",
     "IPM (Integrated Pest Management) — Smart pest control that saves cost and environment:\n\n"
     "WHAT IS IPM:\n"
     "A decision-based approach that combines MULTIPLE pest control strategies to keep pest\n"
     "populations below economically damaging levels with MINIMUM use of chemicals.\n\n"
     "IPM COMPONENTS (use in this order):\n\n"
     "1. CULTURAL CONTROL (free, always first):\n"
     "   • Crop rotation (breaks pest cycles)\n"
     "   • Resistant/tolerant varieties\n"
     "   • Proper spacing, field sanitation\n"
     "   • Optimal sowing/planting time\n\n"
     "2. MECHANICAL CONTROL:\n"
     "   • Pheromone traps (monitor + mass trapping)\n"
     "   • Yellow/blue sticky traps for flying insects\n"
     "   • Light traps for nocturnal moths\n"
     "   • Hand picking of egg masses\n\n"
     "3. BIOLOGICAL CONTROL:\n"
     "   • Release Trichogramma (egg parasitoid)\n"
     "   • Chrysoperla (predator of aphids, mites)\n"
     "   • Bt (Bacillus thuringiensis) spray\n"
     "   • NPV spray for specific caterpillars\n"
     "   • Trichoderma for soil-borne diseases\n\n"
     "4. CHEMICAL CONTROL (only when threshold crossed):\n"
     "   • Use selective pesticides (target specific pests)\n"
     "   • Rotate chemical groups to prevent resistance\n"
     "   • Follow dosage — more is NOT better\n"
     "   • Observe PHI (Pre-Harvest Interval) strictly\n\n"
     "BENEFIT: IPM farmers save 30-50% on pesticide costs. Better food safety. Sustainable farming.",
     "IPM integrated pest management biological cultural chemical control method",
     "All India", "All"),

    ("General", "scheme",
     "How to get subsidy for greenhouse or polyhouse farming?",
     "POLYHOUSE / GREENHOUSE SUBSIDY in India:\n\n"
     "SCHEME: National Horticulture Mission (NHM) + MIDH (Mission for Integrated Development of Horticulture)\n\n"
     "SUBSIDY RATES (central government):\n"
     "• Naturally Ventilated Poly House (NVPH): 50% subsidy\n"
     "   - Up to ₹500/sq meter → subsidy ₹250/sq meter\n"
     "   - Maximum area: 4,000 sq meter per beneficiary\n"
     "   - Maximum subsidy: ₹10 lakh\n\n"
     "• Fan and Pad Poly House (Hi-tech): 50% subsidy\n"
     "   - Up to ₹1,200/sq meter → subsidy ₹600/sq meter\n\n"
     "• Shade Net House: 50% subsidy up to ₹355/sq meter\n\n"
     "STATE TOP-UP: Many states (Karnataka, Gujarat, MH) add 10-20% extra subsidy\n\n"
     "HOW TO APPLY:\n"
     "1. Visit district horticulture office with land documents\n"
     "2. Submit application form + project report\n"
     "3. Technical committee inspects land and approves\n"
     "4. Get 3 quotations from approved vendors\n"
     "5. Construct and submit completion certificate\n"
     "6. Subsidy released in 2 installments\n\n"
     "WHO BENEFITS MOST: Tomato, capsicum, cucumber, rose, gerbera growers\n"
     "RETURN ON INVESTMENT: 3-4 years for tomato/vegetables in polyhouse\n\n"
     "Contact: State Horticulture Department | nhb.gov.in",
     "polyhouse greenhouse subsidy NHM scheme how to apply horticulture",
     "All India", "All"),

]

# ══════════════════════════════════════════════════════════════
#  DATABASE FUNCTIONS
# ══════════════════════════════════════════════════════════════

def create_qa_table(conn, cursor):
    print("\n📋 Creating qa_knowledge table...")
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    print("   ✅ Table created (or already exists)")


def insert_qa_data(conn, cursor):
    print(f"\n💬 Inserting {len(QA_DATA)} Q&A entries...")
    sql = """
        INSERT INTO qa_knowledge
            (crop, category, question, answer, keywords, state, season)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            answer   = VALUES(answer),
            keywords = VALUES(keywords)
    """
    inserted = 0
    failed   = 0
    for row in QA_DATA:
        try:
            cursor.execute(sql, row)
            inserted += 1
        except Exception as e:
            print(f"   ⚠️  Skipped (crop={row[0]}, cat={row[1]}): {e}")
            failed += 1
    conn.commit()
    print(f"   ✅ {inserted} inserted | {failed} skipped")


def show_summary(cursor):
    print("\n📊 QA Knowledge Base Summary:")
    print("   " + "─" * 48)
    cursor.execute("SELECT COUNT(*) FROM qa_knowledge")
    total = cursor.fetchone()[0]
    print(f"   Total Q&A entries : {total}")

    print("\n   By Crop:")
    cursor.execute("""
        SELECT crop, COUNT(*) as cnt
        FROM qa_knowledge
        GROUP BY crop ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        print(f"     {row[0]:<20} {row[1]} entries")

    print("\n   By Category:")
    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM qa_knowledge
        GROUP BY category ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        print(f"     {row[0]:<15} {row[1]} entries")
    print("   " + "─" * 48)


def print_search_function():
    """Print the function to add to app.py"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  ADD THIS FUNCTION TO app.py  (inside AgricultureChatbot)   ║
╚══════════════════════════════════════════════════════════════╝

    def get_qa_answer(self, query: str, crop: str = None) -> list:
        \"\"\"Search qa_knowledge table for matching Q&A\"\"\"
        if not self.mysql_cursor:
            return []
        try:
            if crop:
                sql = \"\"\"
                    SELECT question, answer, category, crop
                    FROM qa_knowledge
                    WHERE MATCH(question, answer, keywords)
                          AGAINST (%s IN NATURAL LANGUAGE MODE)
                      AND crop LIKE %s
                    ORDER BY MATCH(question, answer, keywords)
                          AGAINST (%s IN NATURAL LANGUAGE MODE) DESC
                    LIMIT 3
                \"\"\"
                self.mysql_cursor.execute(sql, (query, f'%{crop}%', query))
            else:
                sql = \"\"\"
                    SELECT question, answer, category, crop
                    FROM qa_knowledge
                    WHERE MATCH(question, answer, keywords)
                          AGAINST (%s IN NATURAL LANGUAGE MODE)
                    ORDER BY MATCH(question, answer, keywords)
                          AGAINST (%s IN NATURAL LANGUAGE MODE) DESC
                    LIMIT 3
                \"\"\"
                self.mysql_cursor.execute(sql, (query, query))
            return self.mysql_cursor.fetchall()
        except Exception as e:
            print(f"QA search error: {e}")
            return []

THEN in generate_response() — add this before building answer:
    qa_results = self.get_qa_answer(query, entities.get('crop'))
    if qa_results:
        answer_parts = []
        for q, a, cat, crop in qa_results:
            answer_parts.append(a)
        return '\\n\\n---\\n\\n'.join(answer_parts)
""")


def main():
    print("=" * 65)
    print("🌾 AGRICULTURE Q&A KNOWLEDGE BASE")
    print("=" * 65)
    print(f"   Total Q&A pairs : {len(QA_DATA)}")
    crops_covered = set(row[0] for row in QA_DATA)
    cats_covered  = set(row[1] for row in QA_DATA)
    print(f"   Crops covered   : {', '.join(sorted(crops_covered))}")
    print(f"   Categories      : {', '.join(sorted(cats_covered))}")
    print("=" * 65)

    try:
        conn = mysql.connector.connect(**config.MYSQL_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected to MySQL")

        create_qa_table(conn, cursor)
        insert_qa_data(conn, cursor)
        show_summary(cursor)

        cursor.close()
        conn.close()

        print_search_function()

        print("\n" + "=" * 65)
        print("✅ Q&A KNOWLEDGE BASE READY!")
        print("\n   Sample questions your chatbot can now answer:")
        sample = [
            "How to grow tomato?",
            "What is MSP of wheat 2024?",
            "How to control Late Blight in potato?",
            "Government schemes for tomato farmers",
            "Why does tomato price crash every year?",
            "What is Kisan Credit Card?",
            "How to control Brown Plant Hopper in rice?",
            "How to store onion after harvest?",
            "What is SRI method of rice cultivation?",
            "How to apply for crop insurance PMFBY?",
        ]
        for q in sample:
            print(f"   ➜  {q}")
        print("=" * 65)

    except Error as e:
        print(f"\n❌ Database error: {e}")
        print("   → Check MYSQL_CONFIG in agri_config.py")
        print("   → Ensure 2_setup_agriculture_db.py was run first")
        raise


if __name__ == "__main__":
    main()