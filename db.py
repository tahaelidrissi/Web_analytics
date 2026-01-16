from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Récupère l'URI MongoDB depuis une variable d'environnement pour plus de sécurité
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set. Please set it in .env file.")

# Créer le client MongoDB
client = MongoClient(MONGO_URI)

# Sélection de la base de données
db = client["webscraper"]

# Sélection de la collection
collection = db["scraped_data"]
sources_collection = db["sources"]


print("✅ Connected to MongoDB Atlas")
