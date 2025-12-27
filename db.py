from pymongo import MongoClient
import os

# Récupère l'URI MongoDB depuis une variable d'environnement pour plus de sécurité
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://")

# Créer le client MongoDB
client = MongoClient(MONGO_URI)

# Sélection de la base de données
db = client["webscraper"]

# Sélection de la collection
collection = db["scraped_data"]

print("✅ Connected to MongoDB Atlas")
