import os
import requests
import yaml
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.yaml
with open ('src/config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Get API key from environment variables
API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = config["api"]["base_url"]
LANG = config["api"]["language"]
REGION = config["api"]["region"]
ITEMS_PER_PAGE = config["request"]["items_per_page"]
TOTAL_PAGES = config["request"]["total_pages"]
RAW_DATA_PATH = config["paths"]["raw_data"]
BACKUP_DIR = config["paths"].get("backup_dir", "data/raw/backups/")

# Load existing movies if available
existing_movies = []
existing_ids = set()

if os.path.exists(RAW_DATA_PATH):
    print("📂 Loading existing movies...")
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        existing_movies = json.load(f)
        existing_ids = {movie['id'] for movie in existing_movies}

    # Backup existing data
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"movies_backup_{timestamp}.json")
    with open(backup_file, 'w', encoding='utf-8') as backup_f:
        json.dump(existing_movies, backup_f, ensure_ascii=False, indent=4)
    print(f"📦 Backed up existing movies to {backup_file}")

# Fetch new movies from TMDB API
print(f"🌐 Fetching new movies from TMDB API (up to {TOTAL_PAGES} pages)...")
new_movies = []
for page in range(1, TOTAL_PAGES + 1):
    url = f"{BASE_URL}/movie/popular"
    params = {
        'api_key': API_KEY,
        'language': LANG,
        'region': REGION,
        'page': page
    }
    response = requests.get(url, params=params)
    data = response.json()

    for movie in data.get('results', []):
        if movie['id'] not in existing_ids:
            new_movies.append(movie)
            existing_ids.add(movie['id'])

print(f"✅ {len(new_movies)} new movies added.")
total = len(existing_movies) + len(new_movies)

# Combine and Save
combined_movies = existing_movies + new_movies
os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)

# Save raw data to JSON file
with open(RAW_DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(combined_movies, f, ensure_ascii=False, indent=4)

print(f"💾 Total movies in dataset: {total}")
print(f"📁 Saved to: {RAW_DATA_PATH}")