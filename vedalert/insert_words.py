import sqlite3

conn = sqlite3.connect("Ayurvedha.db")
cursor = conn.cursor()

# Insert Disorder Categories
disorder_categories = [
    ('Respiratory Disorders'), ('Digestive Disorders'), ('Joint & Bone Disorders'), 
    ('Skin Disorders'), ('Diabetes'), ('Liver Disorders'), ('Cardiovascular Disorders'), 
    ('Stress, Anxiety & Insomnia'), ('Urinary Tract Infections & Kidney Disorders'),
    ('Thyroid Disorders'), ('Fever & Viral Infections'), ('Obesity & Metabolic Disorders')
]
cursor.executemany("INSERT OR IGNORE INTO DisorderCategories (name) VALUES (?)", [(cat,) for cat in disorder_categories])

# Insert Disorders
disorders = [
    (1, 'Asthma'), (1, 'Bronchitis'), (1, 'Sinusitis'),
    (2, 'Acid Reflux'), (2, 'IBS'), (2, 'Constipation'), (2, 'Indigestion'),
    (3, 'Arthritis'), (3, 'Osteoporosis'), (3, 'Gout'),
    (4, 'Eczema'), (4, 'Psoriasis'), (4, 'Acne'), (4, 'Dermatitis'),
    (5, 'Madhumeha'),
    (6, 'Fatty Liver'), (6, 'Jaundice'), (6, 'Hepatitis'),
    (7, 'Hypertension'), (7, 'High Cholesterol'), (7, 'Heart Weakness'),
    (8, 'Stress'), (8, 'Anxiety'), (8, 'Insomnia'),
    (9, 'Urinary Tract Infection'), (9, 'Kidney Disorders'),
    (10, 'Hypothyroidism'), (10, 'Hyperthyroidism'),
    (11, 'Common Cold'), (11, 'Flu'), (11, 'Dengue'), (11, 'COVID-19 Recovery'),
    (12, 'Obesity'), (12, 'Metabolic Disorders')
]
cursor.executemany("INSERT OR IGNORE INTO Disorders (category_id, name) VALUES (?, ?)", disorders)

# Insert Ayurvedic Management Data
ayurvedic_management = [
    (1, 'Tulsi', 'Supports respiratory health and reduces inflammation'),
    (1, 'Licorice', 'Soothes the respiratory tract'),
    (1, 'Pippali', 'Boosts lung function and clears mucus'),
    (2, 'Triphala', 'Improves digestion and detoxifies the gut'),
    (3, 'Guggulu', 'Reduces joint inflammation and supports bone health'),
    (4, 'Neem', 'Cleanses the blood and improves skin conditions'),
    (5, 'Gudmar', 'Helps regulate blood sugar levels'),
    (6, 'Bhumyamalaki', 'Supports liver detoxification and function')
]
cursor.executemany("INSERT OR IGNORE INTO AyurvedicManagement (disorder_id, herb, benefits) VALUES (?, ?, ?)", ayurvedic_management)

# Insert Immunity Boosters
immunity_boosters = [
    (1, 'Chyawanprash', 'Rich in Vitamin C and strengthens the immune system'),
    (2, 'Amla juice', 'Boosts digestion and enhances immunity'),
    (3, 'Giloy', 'Acts as an anti-inflammatory and immunity booster'),
    (4, 'Turmeric', 'Reduces inflammation and supports skin health'),
    (5, 'Neem', 'Purifies blood and regulates blood sugar levels'),
    (6, 'Tulsi', 'Enhances immune response and fights infections')
]
cursor.executemany("INSERT OR IGNORE INTO ImmunityBoosters (disorder_id, booster, benefits) VALUES (?, ?, ?)", immunity_boosters)

# Insert Key Immunity Boosters
key_immunity_boosters = [
    ('Chyawanprash', 'A rejuvenating herbal jam rich in Vitamin C'),
    ('Amla', 'Strengthens immunity and digestion'),
    ('Giloy', 'Powerful immunity modulator'),
    ('Tulsi', 'Supports respiratory and immune health'),
    ('Turmeric', 'Anti-inflammatory and immune-enhancing'),
    ('Ashwagandha', 'Reduces stress and boosts resilience'),
    ('Shatavari', 'Strengthens immunity, especially in women'),
    ('Triphala', 'Aids digestion and detoxification')
]
cursor.executemany("INSERT OR IGNORE INTO KeyImmunityBoosters (name, benefits) VALUES (?, ?)", key_immunity_boosters)

conn.commit()
conn.close()

print("✅ Data inserted successfully into Ayurvedha.db!")
