import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URL")

client = MongoClient(
    uri,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
    tls=True,
    tlsCAFile=certifi.where(),
)

print(client.admin.command("ping"))
print("MongoDB connected successfully")