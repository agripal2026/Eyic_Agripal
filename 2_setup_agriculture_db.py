import mysql.connector
from mysql.connector import Error
import agri_config as config

class AgricultureDBSetup:
    """Setup MySQL database for agriculture chatbot"""
    
    def __init__(self):
        self.config = config.MYSQL_CONFIG
        self.conn = None
        self.cursor = None
    
    def create_database(self):
        try:
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config['port']
            )
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS agriculture_llm")
            print("✅ Database 'agriculture_llm' created/verified")
            cursor.close()
            conn.close()
        except Error as e:
            print(f"❌ Error creating database: {e}")
            raise
    
    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("✅ Connected to database")
        except Error as e:
            print(f"❌ Error connecting to database: {e}")
            raise
    
    def create_tables(self):
        """Create tables with UNIQUE constraints — prevents duplicate rows on every re-run"""
        
        tables = {
            'crops': """
                CREATE TABLE IF NOT EXISTS crops (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    crop_name VARCHAR(100) NOT NULL,
                    crop_type VARCHAR(50),
                    botanical_name VARCHAR(200),
                    category VARCHAR(50),
                    season VARCHAR(50),
                    duration_days INT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_crop_name (crop_name)
                )
            """,
            'market_prices': """
                CREATE TABLE IF NOT EXISTS market_prices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    state VARCHAR(100) NOT NULL,
                    district VARCHAR(100),
                    market VARCHAR(200),
                    crop_name VARCHAR(100) NOT NULL,
                    variety VARCHAR(100),
                    min_price DECIMAL(10,2),
                    max_price DECIMAL(10,2),
                    modal_price DECIMAL(10,2),
                    msp DECIMAL(10,2),
                    unit VARCHAR(20) DEFAULT 'per quintal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_price_entry (date, state, district, crop_name, variety),
                    INDEX idx_date_crop (date, crop_name),
                    INDEX idx_state_crop (state, crop_name)
                )
            """,
            'weather_data': """
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    state VARCHAR(100) NOT NULL,
                    district VARCHAR(100),
                    rainfall DECIMAL(10,2),
                    temperature_min DECIMAL(5,2),
                    temperature_max DECIMAL(5,2),
                    humidity DECIMAL(5,2),
                    wind_speed DECIMAL(5,2),
                    conditions VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_weather_entry (date, state, district),
                    INDEX idx_date_state (date, state)
                )
            """,
            'crop_production': """
                CREATE TABLE IF NOT EXISTS crop_production (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    year VARCHAR(10) NOT NULL,
                    season VARCHAR(50),
                    state VARCHAR(100) NOT NULL,
                    district VARCHAR(100),
                    crop_name VARCHAR(100) NOT NULL,
                    area_hectares DECIMAL(15,2),
                    production_tonnes DECIMAL(15,2),
                    yield_per_hectare DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_production_entry (year, season, state, district, crop_name),
                    INDEX idx_year_crop (year, crop_name),
                    INDEX idx_state_crop (state, crop_name)
                )
            """,
            'government_schemes': """
                CREATE TABLE IF NOT EXISTS government_schemes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    scheme_name VARCHAR(200) NOT NULL,
                    scheme_type VARCHAR(100),
                    state VARCHAR(100),
                    start_date DATE,
                    end_date DATE,
                    budget_amount DECIMAL(15,2),
                    beneficiaries INT,
                    description TEXT,
                    eligibility TEXT,
                    benefits TEXT,
                    application_process TEXT,
                    contact_info TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_scheme_name (scheme_name)
                )
            """,
            'pest_diseases': """
                CREATE TABLE IF NOT EXISTS pest_diseases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    type VARCHAR(50),
                    affected_crops TEXT,
                    symptoms TEXT,
                    causes TEXT,
                    prevention TEXT,
                    treatment TEXT,
                    severity VARCHAR(20),
                    season VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_pest_name (name)
                )
            """,
            'farming_practices': """
                CREATE TABLE IF NOT EXISTS farming_practices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    practice_name VARCHAR(200) NOT NULL,
                    category VARCHAR(100),
                    crop_name VARCHAR(100),
                    description TEXT,
                    benefits TEXT,
                    implementation TEXT,
                    cost_estimate DECIMAL(10,2),
                    success_rate DECIMAL(5,2),
                    recommended_states TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_practice_name (practice_name)
                )
            """,
            'user_queries': """
                CREATE TABLE IF NOT EXISTS user_queries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    query_type VARCHAR(50),
                    state VARCHAR(100),
                    crop_name VARCHAR(100),
                    response TEXT,
                    response_time_ms INT,
                    sources_used TEXT,
                    feedback_rating INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_created_at (created_at)
                )
            """
        }
        
        for table_name, create_statement in tables.items():
            try:
                self.cursor.execute(create_statement)
                print(f"   ✅ Table '{table_name}' created/verified")
            except Error as e:
                print(f"   ❌ Error creating table '{table_name}': {e}")
                raise
        self.conn.commit()

    def add_unique_constraints_to_existing_tables(self):
        """Safely add unique constraints to tables that were created without them.
        This is idempotent — safe to run multiple times."""
        print("\n🔧 Ensuring unique constraints exist on all tables...")

        constraints = [
            ("crops",             "uq_crop_name",        "ALTER TABLE crops ADD UNIQUE KEY uq_crop_name (crop_name)"),
            ("market_prices",     "uq_price_entry",      "ALTER TABLE market_prices ADD UNIQUE KEY uq_price_entry (date, state, district, crop_name, variety)"),
            ("weather_data",      "uq_weather_entry",    "ALTER TABLE weather_data ADD UNIQUE KEY uq_weather_entry (date, state, district)"),
            ("crop_production",   "uq_production_entry", "ALTER TABLE crop_production ADD UNIQUE KEY uq_production_entry (year, season, state, district, crop_name)"),
            ("government_schemes","uq_scheme_name",      "ALTER TABLE government_schemes ADD UNIQUE KEY uq_scheme_name (scheme_name)"),
            ("pest_diseases",     "uq_pest_name",        "ALTER TABLE pest_diseases ADD UNIQUE KEY uq_pest_name (name)"),
            ("farming_practices", "uq_practice_name",    "ALTER TABLE farming_practices ADD UNIQUE KEY uq_practice_name (practice_name)"),
        ]

        for table, key_name, alter_sql in constraints:
            try:
                self.cursor.execute(f"""
                    SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = '{table}'
                      AND CONSTRAINT_NAME = '{key_name}'
                """)
                exists = self.cursor.fetchone()[0]
                if not exists:
                    self.cursor.execute(alter_sql)
                    print(f"   ✅ Added unique constraint to '{table}'")
                else:
                    print(f"   ✔  Constraint already exists on '{table}'")
            except Error as e:
                print(f"   ⚠️  Could not add constraint to '{table}': {e}")
        self.conn.commit()

    def deduplicate_existing_data(self):
        """Delete duplicate rows keeping only the row with the lowest id."""
        print("\n🧹 Removing duplicate rows from all tables...")

        dedup_queries = {
            "crops": """
                DELETE c1 FROM crops c1
                INNER JOIN crops c2
                WHERE c1.id > c2.id AND c1.crop_name = c2.crop_name
            """,
            "market_prices": """
                DELETE mp1 FROM market_prices mp1
                INNER JOIN market_prices mp2
                WHERE mp1.id > mp2.id
                  AND mp1.date = mp2.date
                  AND mp1.state = mp2.state
                  AND COALESCE(mp1.district,'') = COALESCE(mp2.district,'')
                  AND mp1.crop_name = mp2.crop_name
                  AND COALESCE(mp1.variety,'') = COALESCE(mp2.variety,'')
            """,
            "crop_production": """
                DELETE cp1 FROM crop_production cp1
                INNER JOIN crop_production cp2
                WHERE cp1.id > cp2.id
                  AND cp1.year = cp2.year
                  AND COALESCE(cp1.season,'') = COALESCE(cp2.season,'')
                  AND cp1.state = cp2.state
                  AND COALESCE(cp1.district,'') = COALESCE(cp2.district,'')
                  AND cp1.crop_name = cp2.crop_name
            """,
            "government_schemes": """
                DELETE gs1 FROM government_schemes gs1
                INNER JOIN government_schemes gs2
                WHERE gs1.id > gs2.id AND gs1.scheme_name = gs2.scheme_name
            """,
            "pest_diseases": """
                DELETE pd1 FROM pest_diseases pd1
                INNER JOIN pest_diseases pd2
                WHERE pd1.id > pd2.id AND pd1.name = pd2.name
            """,
        }

        for table, dq in dedup_queries.items():
            try:
                self.cursor.execute(dq)
                affected = self.cursor.rowcount
                if affected > 0:
                    print(f"   🗑️  Removed {affected} duplicate row(s) from '{table}'")
                else:
                    print(f"   ✔  No duplicates found in '{table}'")
            except Error as e:
                print(f"   ⚠️  Could not deduplicate '{table}': {e}")
        self.conn.commit()

    def insert_sample_data(self):
        """Insert sample data — INSERT IGNORE skips rows that already exist"""
        print("\n🌱 Inserting sample data (safe to re-run, duplicates skipped)...")
        
        crops_data = [
            ('Rice',      'Cereal',    'Oryza sativa',          'Cereals',    'Kharif',    120, 'Staple food crop'),
            ('Wheat',     'Cereal',    'Triticum aestivum',     'Cereals',    'Rabi',      125, 'Winter cereal crop'),
            ('Cotton',    'Fiber',     'Gossypium',             'Cash Crops', 'Kharif',    180, 'Commercial fiber crop'),
            ('Sugarcane', 'Cash Crop', 'Saccharum officinarum', 'Cash Crops', 'Perennial', 365, 'Sugar production crop'),
        ]
        self.cursor.executemany("""
            INSERT IGNORE INTO crops 
            (crop_name, crop_type, botanical_name, category, season, duration_days, description)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, crops_data)

        prices_data = [
            ('2024-01-15','Karnataka',    'Bangalore','APMC Bangalore','Rice',     'Basmati',       2800,3200,3000,2930,'per quintal'),
            ('2024-01-15','Karnataka',    'Mysore',   'APMC Mysore',   'Wheat',    'Lokwan',        2300,2500,2400,2275,'per quintal'),
            ('2024-01-15','Maharashtra',  'Pune',     'APMC Pune',     'Cotton',   'Medium Staple', 6200,6800,6500,6620,'per quintal'),
            ('2024-01-15','Uttar Pradesh','Lucknow',  'APMC Lucknow',  'Sugarcane','Co-86032',       350, 400, 375, 315,'per quintal'),
        ]
        self.cursor.executemany("""
            INSERT IGNORE INTO market_prices 
            (date,state,district,market,crop_name,variety,min_price,max_price,modal_price,msp,unit)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, prices_data)

        production_data = [
            ('2023-24','Kharif','Karnataka',  'Bangalore','Rice',   45000, 180000,4.00),
            ('2023-24','Rabi',  'Punjab',     'Ludhiana', 'Wheat', 120000, 600000,5.00),
            ('2023-24','Kharif','Maharashtra','Nagpur',   'Cotton', 85000, 255000,3.00),
        ]
        self.cursor.executemany("""
            INSERT IGNORE INTO crop_production 
            (year,season,state,district,crop_name,area_hectares,production_tonnes,yield_per_hectare)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, production_data)

        schemes_data = [
            ('PM-KISAN','Direct Benefit Transfer','All India','2019-02-01',None,
             750000000000,110000000,
             'Income support to farmer families',
             'All landholding farmer families',
             'Rs. 6000 per year in three installments',
             'Online registration through PM-KISAN portal',
             '1800-180-1551',True),
            ('Pradhan Mantri Fasal Bima Yojana','Crop Insurance','All India','2016-02-18',None,
             130000000000,55000000,
             'Crop insurance scheme for farmers',
             'All farmers growing notified crops',
             'Financial support in case of crop loss',
             'Register through banks or CSCs',
             '1800-180-1111',True),
        ]
        self.cursor.executemany("""
            INSERT IGNORE INTO government_schemes 
            (scheme_name,scheme_type,state,start_date,end_date,budget_amount,beneficiaries,
             description,eligibility,benefits,application_process,contact_info,is_active)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, schemes_data)

        pest_data = [
            ('Brown Plant Hopper','Pest','Rice, Wheat',
             'Yellowing and drying of leaves, hopper burn',
             'High humidity, dense planting',
             'Proper spacing, resistant varieties',
             'Neem-based pesticides, Imidacloprid','High','Monsoon'),
            ('Leaf Blight','Disease','Rice',
             'Brown spots on leaves, reduced yield',
             'Fungal infection in humid conditions',
             'Crop rotation, resistant varieties',
             'Fungicides like Mancozeb','Medium','Kharif'),
        ]
        self.cursor.executemany("""
            INSERT IGNORE INTO pest_diseases 
            (name,type,affected_crops,symptoms,causes,prevention,treatment,severity,season)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, pest_data)
        
        self.conn.commit()
        print("   ✅ Sample data inserted")
    
    def test_queries(self):
        print("\n🧪 Row counts after setup:\n")
        for table in ['crops','market_prices','crop_production','government_schemes','pest_diseases']:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"   {table}: {self.cursor.fetchone()[0]} rows")

        self.cursor.execute("""
            SELECT crop_name, state, modal_price, msp
            FROM market_prices
            ORDER BY crop_name, state
        """)
        print("\n   📊 Market Prices:")
        print("   " + "-"*55)
        for row in self.cursor.fetchall():
            crop, state, modal, msp = row
            print(f"   {crop} ({state}): ₹{float(modal):.2f}  (MSP: ₹{float(msp):.2f})")
    
    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn:   self.conn.close()
        print("\n✅ Database connection closed")


def main():
    print("🚀 Setting up Agriculture Database\n")
    print("="*60)
    db = AgricultureDBSetup()
    try:
        db.create_database()
        db.connect()
        print("\n📋 Creating / verifying tables...")
        db.create_tables()
        db.add_unique_constraints_to_existing_tables()
        db.deduplicate_existing_data()
        db.insert_sample_data()
        db.test_queries()
        print("\n" + "="*60)
        print("✅ Agriculture Database Setup Complete!")
        print("   Now safe to re-run — no more duplicate rows.")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()