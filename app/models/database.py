from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import asyncio
from app.utils.config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def get_database() -> AsyncIOMotorDatabase:
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

# Test connection
async def test_connection():
    try:
        await db.client.admin.command('ping')
        print("MongoDB connection successful")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False
