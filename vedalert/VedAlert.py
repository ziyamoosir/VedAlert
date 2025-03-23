import time
import logging
import sqlite3
import requests
import pandas as pd
import random
from pytrends.request import TrendReq
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
import os
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse
import aiohttp 
ALLOWED_KEYWORDS = [
    "ayush", "ayush center", "ayush ministry", "ayush hospital", "ayurveda", 
    "yoga", "unani", "siddha", "homeopathy", "natural healing", 
    "immunity booster", "holistic well-being", "herbal medicine", "medicinal plants",
    "ayurvedic herbs", "siddha herbs", "unani medicine", "homeopathic remedies", 
    "tulsi", "neem", "ashwagandha", "brahmi", "shatavari", "amla", "giloy", "moringa",
    "turmeric", "ginger", "garlic", "black pepper", "cinnamon", "cardamom",
    "clove", "fenugreek", "coriander", "fennel", "licorice", "aloe vera", "basil",
    "ginseng", "saffron", "nutmeg", "oregano", "thyme", "rosemary", "lavender",
    "peppermint", "lemongrass", "hibiscus", "chamomile", "calendula", "gokshura",
    "bhumi amla", "manjistha", "arjuna", "jatamansi", "shankhpushpi", "kundru",
    "bala", "punarnava", "vacha", "daruharidra", "vidarikand", "bakuchi", 
    "kasturi", "kesar", "mahua", "haritaki", "bibhitaki", "triphala", "kapikachhu",
    "pippali", "mulethi", "kasturi manjal", "noni", "karela", "asparagus",
    "dandelion", "sarsaparilla", "guduchi", "kasturi bhindi", "jasmine",
    "bamboo shoots", "curry leaves", "betel leaves", "sarpagandha", "nagarmotha",
    "tankan bhasma", "ras sindoor", "swarn bhasma", "loh bhasma", 
    "Tuberculosis", "Malaria", "Dengue fever", "Cholera", "Hepatitis A", 
    "Hepatitis B", "Hepatitis C", "Hepatitis D", "Hepatitis E", "Influenza", 
    "COVID-19", "HIV/AIDS", "Typhoid fever", "Leptospirosis", "Rabies", 
    "Chickenpox", "Measles", "Mumps", "Rubella", "Whooping cough", 
    "Zika virus", "Ebola", "Asthma", "Chronic Obstructive Pulmonary Disease (COPD)", 
    "Pneumonia", "Bronchitis", "Emphysema", "Pulmonary fibrosis", 
    "Alzheimer's disease", "Parkinson’s disease", "Epilepsy", "Multiple sclerosis (MS)", 
    "Stroke", "Migraine", "Huntington’s disease", "Amyotrophic lateral sclerosis (ALS)", 
    "Hypertension", "Coronary artery disease (CAD)", "Heart attack", 
    "Arrhythmia", "Congestive heart failure", "Aneurysm", "Rheumatoid arthritis", 
    "Lupus", "Type 1 diabetes", "Psoriasis", "Celiac disease", 
    "Hashimoto's thyroiditis", "Diabetes Type 1", "Diabetes Type 2", 
    "Hypothyroidism", "Hyperthyroidism", "Polycystic Ovary Syndrome (PCOS)", 
    "Cushing’s syndrome", "Addison’s disease", "Gastritis", "Peptic ulcer disease", 
    "Crohn’s disease", "Ulcerative colitis", "Irritable Bowel Syndrome (IBS)", 
    "Gallstones", "Eczema", "Acne", "Vitiligo", "Melanoma", "Ringworm", 
    "Athlete’s foot", "Osteoporosis", "Osteoarthritis", "Gout", 
    "Ankylosing spondylitis", "Down syndrome", "Cystic fibrosis", 
    "Sickle cell anemia", "Thalassemia", "Marfan syndrome"
]
# Bot Token
TOKEN = "7652457274:AAHTTU4iGQeRegEbZWnFt_wYOQPohK7e7p0"  # Replace with your actual token
MAPBOX_API_KEY = "pk.eyJ1IjoibmV4Zm9yeiIsImEiOiJjbTZpMzkycHEwNGdoMmtzNzlmcTlod2g3In0.v7CGHvZ7KsrT_WhV2BBHcA"
# Initialize Pytrends
pytrends = TrendReq(hl='en-US', tz=360)
time.sleep(5)

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Database Setup
DB_PATH = "AyurvedicDB.db"

def setup_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        print("Current working directory:", os.getcwd())
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS DisorderCategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Disorders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES DisorderCategories(id)
            );
            CREATE TABLE IF NOT EXISTS AyurvedicManagement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disorder_id INTEGER,
                herb TEXT NOT NULL,
                benefits TEXT,
                FOREIGN KEY (disorder_id) REFERENCES Disorders(id)
            );
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

setup_database()
# Set up Gemini API
GEMINI_API_KEY = "AIzaSyAjuOpYW_YQgBHh6K1tBUwCZv2n96MlViI"  
genai.configure(api_key=GEMINI_API_KEY)

# Function to call Gemini with restrictions
def ask_gemini(prompt):
    if any(keyword in prompt.lower() for keyword in ALLOWED_KEYWORDS):
        model = genai.GenerativeModel("gemini-1.5-pro")  # Initialize the Gemini model
        response = model.generate_content(prompt)  # Generate response
        return response.text  # Extract and return text
    else:
        return "I can't help with that."
async def help(update: Update, context: CallbackContext):
    help_text = (
        "🌿 *Welcome to the AYUSH Health Bot!*\n"
        "I can assist you with Ayurvedic remedies, immunity boosters, and trending health concerns.\n\n"
        "📌 *Commands you can use:*\n"
        "• /start - Begin using the bot and share your location\n"
        "• /simulate - Simulate disease outbreaks & Ayurvedic management\n"
        "• /chat - Ask me anything about Ayurveda & natural healing\n"
        "• /help - Get help on how to use the bot\n\n"
        "📍 *Find AYUSH Clinics:*\n"
        "Send your location to receive nearby AYUSH clinics (Ayurveda, Yoga, Homeopathy, etc.)."
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")

async def get_ayush_clinics(latitude, longitude):
    """Fetch clinics in Thiruvananthapuram with 5 results limit"""
    # Hardcode Thiruvananthapuram coordinates (8.5241° N, 76.9366° E)
    TVM_LAT = 8.5241
    TVM_LON = 76.9366
    
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoibmV4Zm9yeiIsImEiOiJjbTZpMzkycHEwNGdoMmtzNzlmcTlod2g3In0.v7CGHvZ7KsrT_WhV2BBHcA"
    search_queries = [
        "ayurveda", "yoga", "homeopathy", 
        "unani", "siddha", "ayush hospital"
    ]
    
    clinics = set()
    
    async with aiohttp.ClientSession() as session:
        for query in search_queries:
            try:
                encoded_query = urllib.parse.quote(f"{query} Thiruvananthapuram")
                url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_query}.json"
                
                params = {
                    "proximity": f"{TVM_LON},{TVM_LAT}",
                    "access_token": MAPBOX_ACCESS_TOKEN,
                    "types": "poi,address",
                    "limit": 5,  # Reduced limit per query
                    "country": "IN",
                    "bbox": "76.8,8.4,77.0,8.7"  # Bounding box around TVM
                }

                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    for feature in data.get("features", []):
                        # Extract name and address
                        name = feature.get('text', 'AYUSH Center')
                        place_name = feature.get('place_name', '')
                        
                        if "Thiruvananthapuram" not in place_name:
                            continue  # Skip results outside TVM
                            
                        # Address formatting
                        address = place_name.replace(f"{name}, ", "").strip()
                        clinics.add(f"🏥 *{name}*\n📍 {address}")

            except Exception as e:
                logging.error(f"Mapbox error: {e}")
                continue

    # TVM-specific fallbacks
    clinic_list = list(clinics)
    if len(clinic_list) < 5:
        clinic_list.extend([
            "🏥 *Government Ayurveda Hospital*\n📍 Poojappura, Thiruvananthapuram",
            "🏥 *Siddha Regional Research Institute*\n📍 Thiruvananthapuram",
            "🏥 *Yoga Centre, Kovalam*\n📍 Thiruvananthapuram",
            "🏥 *National Homoeopathy Research Institute*\n📍 Thiruvananthapuram",
            "🏥 *AYUSH Wellness Center*\n📍 Kazhakootam, Thiruvananthapuram"
        ])
    
    return sorted(clinic_list, key=lambda x: "Thiruvananthapuram" in x)[:5]  # Strict 5 results
    
    return sorted(clinic_list, key=lambda x: "not available" not in x)[:10]  # Prioritize entries with addresses

# Start command
async def chat(update: Update, context: CallbackContext):
    await update.message.reply_text("🌿 Namaste! I am your AI-powered AYUSH companion, here to guide you with time-tested wisdom from Ayurveda, Yoga, Unani, Siddha, and Homeopathy. Ask me about natural healing, immunity boosters, or holistic well-being! ✨🌱")

# Ayush-specific command
async def ayush_command(update: Update, context: CallbackContext):
    user_input = " ".join(context.args) or "Tell me about Ayush and Ayush centers."
    response = ask_gemini(user_input)
    await update.message.reply_text(response)

# Default message handler
async def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text.lower()
    if any(keyword in user_text for keyword in ALLOWED_KEYWORDS):
        response = ask_gemini(user_text)
    else:
        response = "I can't help with that."
    await update.message.reply_text(response)
# Add this new function
async def simulate(update: Update, context: CallbackContext):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get random disease with Ayurvedic management
        cursor.execute("""
            SELECT d.name, am.herb, am.benefits 
            FROM Disorders d
            JOIN AyurvedicManagement am ON d.id = am.disorder_id
            ORDER BY RANDOM() LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()

        if result:
            disease, herb, benefits = result
            response = (f"🚨 Simulated Outbreak Alert! 🚨\n\n"
                        f"⚠️ Increased cases of {disease.title()} reported in your region\n\n"
                        f"🌿 Recommended Ayurvedic Management:\n"
                        f"• *{herb}*: {benefits}\n"f"🔗 [VedAlert](https://official_vedalert.surge.sh)")
        else:
            response = "⚠️ No disease data available for simulation"

        await update.message.reply_text(response, parse_mode="Markdown")
        
    except sqlite3.Error as e:
        logging.error(f"Database error in simulation: {e}")
        await update.message.reply_text("❌ Error accessing health records")
    response += "🔗 [VedAlert](https://official_vedalert.surge.sh)"

# Add this handler to main()
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("simulate", simulate))
    app.add_handler(CommandHandler("chat", chat))  # Ensure this is registered
    app.add_handler(CommandHandler("help", help))
    app.add_handler(MessageHandler(filters.LOCATION, location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Handle general text
    app.run_polling()

def fetch_diseases_from_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get diseases with their categories
        cursor.execute("""
            SELECT d.name, dc.name
            FROM Disorders d
            JOIN DisorderCategories dc ON d.category_id = dc.id
        """)

        diseases = [row[0].lower() for row in cursor.fetchall()]
        conn.close()

        # Filter unique diseases and limit to 10 for Trends API
        unique_diseases = list(set(diseases))[:10]
        return unique_diseases if unique_diseases else None

    except Exception as e:
        logging.error(f"Database error: {e}")
        return None


def get_weather_and_season(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url).json()

    if "current_weather" in response:
        temp = response["current_weather"]["temperature"]
        condition = response["current_weather"]["weathercode"]
        condition_desc = weather_code_to_description(condition)
        return temp, condition_desc
    return None, None


def weather_code_to_description(code):
    weather_dict = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime Fog", 51: "Light Drizzle", 53: "Moderate Drizzle",
        55: "Heavy Drizzle", 61: "Light Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        71: "Light Snow", 73: "Moderate Snow", 75: "Heavy Snow", 80: "Rain Showers",
        81: "Moderate Showers", 82: "Heavy Showers", 95: "Thunderstorm"
    }
    return weather_dict.get(code, "Unknown Weather")


def get_trending_diseases(region=""):
    try:
        diseases = fetch_diseases_from_db()
        if not diseases:
            return None  # Handle empty DB case

        trends_data = {}
        geo = region.upper() if len(region) == 2 else ""  # ISO country code format

        # Split into chunks of 5 due to Trends API limits
        for i in range(0, len(diseases), 5):
            chunk = diseases[i:i + 5]
            pytrends.build_payload(chunk, cat=0, timeframe="now 7-d", geo=geo)
            trend_data = pytrends.interest_over_time()

            if not trend_data.empty:
                for disease in chunk:
                    avg_interest = trend_data[disease].mean()
                    trends_data[disease] = "❗Rising concerens" if avg_interest > 85 else \
                        "⚠️ Dangerous" if avg_interest > 95 else \
                        "✅ No Concern"

        # Sort by trend intensity
        return dict(sorted(trends_data.items(),
                         key=lambda item: item[1],
                         reverse=True))

    except Exception as e:
        logging.error(f"Trends API error: {e}")
        return None

def get_healthmap_data(lat, lon):
    try:
        url = "https://www.healthmap.org/en/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        outbreaks = []

        # Find outbreak containers - updated selector
        outbreak_cards = soup.select('div.alert-item')
        
        for card in outbreak_cards[:5]:  # Limit to 5 outbreaks
            try:
                # Extract disease name - updated selector
                disease_elem = card.select_one('h4.alert-title')
                disease = disease_elem.text.strip() if disease_elem else "Unknown Disease"
                
                # Extract location - updated selector
                location_elem = card.select_one('div.alert-location')
                location = location_elem.text.strip() if location_elem else "Unknown Location"
                
                # Extract date - new field
                date_elem = card.select_one('div.alert-date')
                date = date_elem.text.strip() if date_elem else "Date not available"
                
                outbreaks.append({
                    "name": disease,
                    "location": location,
                    "date": date
                })
                
            except Exception as card_error:
                logging.warning(f"Error parsing outbreak card: {card_error}")
                continue

        return outbreaks if outbreaks else None

    except requests.exceptions.RequestException as e:
        logging.error(f"HealthMap request failed: {e}")
        return None
    except Exception as e:
        logging.error(f"HealthMap parsing error: {e}")
        return None
def get_immunity_boosters():
    try:
        url = "https://www.healthline.com/nutrition/immune-boosting-foods"
        response = requests.get(url)
        response.raise_for_status() #Check for errors
        soup = BeautifulSoup(response.text, "html.parser")
        boosters = []

        for item in soup.find_all("div", class_="rich-text"): #Inspect the website and change this to the proper div containing relevant text
            header = item.find_previous("h2") #Assumes the title is in the h2 just before the text
            if header:
                booster_name = header.text.strip()
                reasons = item.text.strip()[:200] + "..." #Shorten the reasons
                boosters.append({"name": booster_name, "reasons": reasons})

        return boosters[:3] #Return top 3
    except Exception as e:
        logging.error(f"Error scraping immunity boosters: {e}")
        return [{"name": "Honey", "reasons": "Natural antibacterial and antioxidant properties."},
                {"name": "Lemon", "reasons": "High in Vitamin C, supports immune function."},
                {"name": "Giloy", "reasons": "Traditional Ayurvedic medicine, boosts immunity."}]

async def location(update: Update, context: CallbackContext):
    user_location = update.message.location
    latitude, longitude = user_location.latitude, user_location.longitude
    geolocator = Nominatim(user_agent="AyurvedicHealthBot", timeout=15)
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    location = reverse((latitude, longitude), language="en", exactly_one=True)
    
    if not location:
        await update.message.reply_text("❌ Couldn't determine location details. Try again.")
        return

    address = location.raw.get("address", {})
    country = address.get("country", "Unknown")
    temp, weather_condition = get_weather_and_season(latitude, longitude)
    immunity_boosters = get_immunity_boosters()
    trends = get_trending_diseases(address.get("country_code", ""))
    outbreaks = get_healthmap_data(latitude, longitude)
    ayush_clinics = await get_ayush_clinics(latitude, longitude)

    response = (f"📍 *Location:* {address.get('state', 'Unknown')}, {country}\n"
                f"🌡 *Weather:* {weather_condition}, {temp}°C\n\n"
                "🍵 *Recommended Immunity Boosters:*\n")

    for booster in immunity_boosters:
        response += f"• *{booster['name']}:* {booster['reasons']}\n"

    if trends:
        response += "🌿 *Regional Health Trends:*\n"
        for disease, status in list(trends.items())[:5]:  # Show top 5
            response += f"• {disease.title()}: {status}\n"
    else:
        response += "✅ *No significant trending diseases in your area.*\n"

    if outbreaks:
        response += "\n🚨 *Recent Disease Alerts (via HealthMap):*\n"
        for outbreak in outbreaks:
            response += (
            f"• *{outbreak['name'].title()}*\n"
            f"  📍 {outbreak['location']}\n"
            f"  📅 {outbreak['date']}\n\n"
        )
    else:
        response += "\n✅ No recent HealthMap alerts in your region\n"

    if ayush_clinics:
        response += "\n🏥 *Nearby AYUSH Clinics:*\n"
        response += "\n".join(ayush_clinics)

    await update.message.reply_text(response, parse_mode="Markdown")
async def start(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("📍 Share Location", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "🌿 Welcome! Share your location to get Ayurvedic immunity booster & disease alerts.",
        reply_markup=reply_markup,
    )

if __name__ == "__main__":
    main()
