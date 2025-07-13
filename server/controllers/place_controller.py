from flask_pymongo import PyMongo
from datetime import datetime, timezone
from typing import List, Optional

def add_place(mongo: PyMongo, place_data: dict):
    """
    Add a new place to the database. Returns inserted_id or None if fsq_id already exists.
    """
    fsq_id = place_data.get("original", {}).get("fsq_id")
    if not fsq_id:
        return None  # fsq_id is required
    if mongo.db.places.find_one({"original.fsq_id": fsq_id}):
        return None  # Place already exists
    place_doc = {
        "original": {
            "fsq_id": fsq_id,
            "name": place_data.get("original", {}).get("name"),
            "category": place_data.get("original", {}).get("category"),
            "address": place_data.get("original", {}).get("address"),
            "locality": place_data.get("original", {}).get("locality"),
            "city": place_data.get("original", {}).get("city"),
            "country": place_data.get("original", {}).get("country"),
            "photo_url": place_data.get("original", {}).get("photo_url"),
            "coordinates": place_data.get("original", {}).get("coordinates", {})
        },
        "processed": place_data.get("processed", {}),
        "reviews": place_data.get("reviews", []),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    result = mongo.db.places.insert_one(place_doc)
    return result.inserted_id

def bulk_insert_places(mongo: PyMongo, places_data: List[dict]):
    """
    Insert multiple places at once. Returns list of inserted_ids.
    Skips places that already exist (by fsq_id).
    """
    place_docs = []
    for place_data in places_data:
        fsq_id = place_data.get("original", {}).get("fsq_id")
        if not fsq_id:
            continue  # Skip if no fsq_id
        
        # Check if place already exists
        if mongo.db.places.find_one({"original.fsq_id": fsq_id}):
            continue  # Skip if already exists
        
        place_doc = {
            "original": {
                "fsq_id": fsq_id,
                "name": place_data.get("original", {}).get("name"),
                "category": place_data.get("original", {}).get("category"),
                "address": place_data.get("original", {}).get("address"),
                "locality": place_data.get("original", {}).get("locality"),
                "city": place_data.get("original", {}).get("city"),
                "country": place_data.get("original", {}).get("country"),
                "photo_url": place_data.get("original", {}).get("photo_url"),
                "coordinates": place_data.get("original", {}).get("coordinates", {})
            },
            "processed": place_data.get("processed", {}),
            "reviews": place_data.get("reviews", []),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        place_docs.append(place_doc)
    
    if place_docs:
        result = mongo.db.places.insert_many(place_docs)
        return [str(id) for id in result.inserted_ids]
    return []

def find_places(mongo: PyMongo, vibe_tags: Optional[List[str]] = None, category: Optional[str] = None, city: Optional[str] = None):
    """
    Find places by vibe tags, category, city, or any combination. All parameters are optional.
    Returns a list of matching places.
    """
    query = {}
    if vibe_tags:
        query["processed.vibe_tags"] = {"$in": vibe_tags}
    if category:
        query["original.category"] = category
    if city:
        query["original.city"] = city
    return list(mongo.db.places.find(query))

def fetch_all_places(mongo: PyMongo):
    """
    Fetch all places from the database.
    Returns a list of all place documents.
    """
    return list(mongo.db.places.find())

def update_place(mongo: PyMongo, place_id: str, update_data: dict):
    """
    Update an existing place by _id. Returns True if updated, False if not found.
    """
    update_data["updated_at"] = datetime.now(timezone.utc)
    result = mongo.db.places.update_one(
        {"_id": place_id},
        {"$set": update_data}
    )
    return result.modified_count > 0 