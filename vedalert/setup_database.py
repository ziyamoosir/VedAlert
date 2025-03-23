import sqlite3

# Connect to SQLite database (creates Ayurvedha.db if not exists)
conn = sqlite3.connect("Ayurvedha.db")
cursor = conn.cursor()

# Create DisorderCategories Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS DisorderCategories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')

# Create Disorders Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Disorders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES DisorderCategories(id)
    )
''')

# Create AyurvedicManagement Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS AyurvedicManagement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disorder_id INTEGER,
        herb TEXT NOT NULL,
        benefits TEXT,
        FOREIGN KEY (disorder_id) REFERENCES Disorders(id)
    )
''')

# Create ImmunityBoosters Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ImmunityBoosters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disorder_id INTEGER,
        booster TEXT NOT NULL,
        benefits TEXT,
        FOREIGN KEY (disorder_id) REFERENCES Disorders(id)
    )
''')

# Create KeyImmunityBoosters Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS KeyImmunityBoosters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        benefits TEXT
    )
''')
# Create DiseaseReports Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS DiseaseReports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    location TEXT,
    disorder TEXT,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
# Create UserLocation Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserLocation (
    user_id INTEGER PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    timezone TEXT
)
''')

# Commit and close connection
conn.commit()
conn.close()

print("✅ Ayurvedha.db and tables created successfully!")
