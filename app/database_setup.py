import sqlite3
import os

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'biomarkers.db')

def initialize_database():
    """Initializes the SQLite database and creates tables if they don't exist."""
    # Ensure the data directory exists
    os.makedirs(DATABASE_DIR, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Create Biomarkers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Biomarkers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                unit TEXT NOT NULL,
                category TEXT
            )
        ''')

        # Create Readings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                biomarker_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL, -- Store as ISO 8601 string
                value REAL NOT NULL,
                FOREIGN KEY (biomarker_id) REFERENCES Biomarkers(id) ON DELETE CASCADE
            )
        ''')

        # Create ReferenceRanges Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ReferenceRanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                biomarker_id INTEGER NOT NULL,
                range_type TEXT NOT NULL, -- 'below', 'above', 'between'
                lower_bound REAL,         -- Used for 'above' and 'between'
                upper_bound REAL,         -- Used for 'below' and 'between'
                FOREIGN KEY (biomarker_id) REFERENCES Biomarkers(id) ON DELETE CASCADE
            )
        ''')

        # Create Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_biomarker_id ON Readings (biomarker_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON Readings (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reference_ranges_biomarker_id ON ReferenceRanges (biomarker_id)')

        conn.commit()

        # Check if we need to seed initial data
        cursor.execute("SELECT COUNT(*) FROM Biomarkers")
        biomarker_count = cursor.fetchone()[0]

        if biomarker_count == 0:
            seed_initial_biomarkers(conn)

        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def seed_initial_biomarkers(conn):
    """Seed the database with initial biomarkers if empty."""
    print("Seeding initial biomarkers...")

    # List of common biomarkers with units and categories
    initial_biomarkers = [
        # Blood biomarkers
        ("Hemoglobin", "g/dL", "Blood"),
        ("Hematocrit", "%", "Blood"),
        ("White Blood Cell Count", "cells/μL", "Blood"),
        ("Platelet Count", "cells/μL", "Blood"),
        ("Red Blood Cell Count", "cells/μL", "Blood"),

        # Lipid biomarkers
        ("Total Cholesterol", "mg/dL", "Lipids"),
        ("HDL Cholesterol", "mg/dL", "Lipids"),
        ("LDL Cholesterol", "mg/dL", "Lipids"),
        ("Triglycerides", "mg/dL", "Lipids"),

        # Metabolic biomarkers
        ("Glucose (Fasting)", "mg/dL", "Metabolic"),
        ("HbA1c", "%", "Metabolic"),
        ("Insulin", "μIU/mL", "Metabolic"),

        # Liver biomarkers
        ("ALT", "U/L", "Liver"),
        ("AST", "U/L", "Liver"),
        ("Alkaline Phosphatase", "U/L", "Liver"),
        ("Total Bilirubin", "mg/dL", "Liver"),

        # Kidney biomarkers
        ("Creatinine", "mg/dL", "Kidney"),
        ("BUN", "mg/dL", "Kidney"),
        ("eGFR", "mL/min/1.73m²", "Kidney"),

        # Electrolytes
        ("Sodium", "mmol/L", "Electrolytes"),
        ("Potassium", "mmol/L", "Electrolytes"),
        ("Chloride", "mmol/L", "Electrolytes"),
        ("Calcium", "mg/dL", "Electrolytes"),

        # Vitamins and Minerals
        ("Vitamin D", "ng/mL", "Vitamins"),
        ("Vitamin B12", "pg/mL", "Vitamins"),
        ("Iron", "μg/dL", "Minerals"),
        ("Ferritin", "ng/mL", "Minerals"),

        # Hormones
        ("TSH", "mIU/L", "Hormones"),
        ("Free T4", "ng/dL", "Hormones"),
        ("Cortisol", "μg/dL", "Hormones"),

        # Inflammatory markers
        ("C-Reactive Protein", "mg/L", "Inflammation"),
        ("ESR", "mm/hr", "Inflammation"),
    ]

    cursor = conn.cursor()

    # Insert biomarkers
    cursor.executemany(
        "INSERT INTO Biomarkers (name, unit, category) VALUES (?, ?, ?)",
        initial_biomarkers
    )

    # Commit changes
    conn.commit()
    print(f"Added {len(initial_biomarkers)} initial biomarkers")

if __name__ == '__main__':
    # Allow running this script directly to initialize the DB
    initialize_database()