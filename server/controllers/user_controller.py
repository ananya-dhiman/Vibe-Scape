from flask_pymongo import PyMongo
from datetime import datetime, timezone
from bson import ObjectId
from Auth.firebase_admin import get_user_by_uid, create_user_in_firebase

def add_user(mongo: PyMongo, user_data: dict):
    """
    Add a new user to the database. Assumes user_data contains Firebase UID, name, and email.
    Returns the inserted_id or None if user already exists.
    """
    if mongo.db.users.find_one({"_id": user_data.get("_id")}):
        return None  # User already exists
    
    user_doc = {
        "_id": user_data.get("_id"),  # Firebase UID
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "location": user_data.get("location"),
        "persona": user_data.get("persona", "casual"),
        "preferences": {
            "vibe": user_data.get("preferences", {}).get("vibe", []),
            "category": user_data.get("preferences", {}).get("category", [])
        },
        "wishlist": user_data.get("wishlist", []),  # Initialize empty wishlist
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    result = mongo.db.users.insert_one(user_doc)
    return result.inserted_id

def create_user_with_firebase(mongo: PyMongo, firebase_uid: str, user_data: dict):
    """
    Create a user in both Firebase and our database.
    This is called when a user signs up through Firebase.
    """
    try:
        # Get user info from Firebase
        firebase_result = get_user_by_uid(firebase_uid)
        
        if not firebase_result['success']:
            return None
        
        firebase_user = firebase_result['user']
        
        # Prepare user data for our database
        user_doc = {
            "_id": firebase_uid,  # Use Firebase UID as our user ID
            "name": user_data.get("name") or firebase_user.get('display_name') or firebase_user.get('email'),
            "email": firebase_user.get('email'),
            "location": user_data.get("location"),
            "persona": user_data.get("persona", "casual"),
            "preferences": {
                "vibe": user_data.get("preferences", {}).get("vibe", []),
                "category": user_data.get("preferences", {}).get("category", [])
            },
            "wishlist": [],  # Initialize empty wishlist
            "firebase_user": {
                "display_name": firebase_user.get('display_name'),
                "photo_url": firebase_user.get('photo_url'),
                "email_verified": firebase_user.get('email_verified', False)
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Check if user already exists
        if mongo.db.users.find_one({"_id": firebase_uid}):
            return None  # User already exists
        
        result = mongo.db.users.insert_one(user_doc)
        return result.inserted_id
        
    except Exception as e:
        print(f"Error creating user with Firebase: {e}")
        return None

def update_user(mongo: PyMongo, user_id: str, update_data: dict):
    """
    Update an existing user. Returns True if updated, False if not found.
    """
    update_data["updated_at"] = datetime.now(timezone.utc)
    result = mongo.db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    return result.modified_count > 0

def get_user(mongo: PyMongo, user_id: str):
    """
    Get a user by their Firebase UID. Returns the user document or None if not found.
    """
    return mongo.db.users.find_one({"_id": user_id})

def delete_user(mongo: PyMongo, user_id: str):
    """
    Delete a user by their Firebase UID. Returns True if deleted, False if not found.
    """
    result = mongo.db.users.delete_one({"_id": user_id})
    return result.deleted_count > 0

def add_to_wishlist(mongo: PyMongo, user_id: str, place_id: str):
    """
    Add a place to user's wishlist. Returns True if added, False if user not found or place already in wishlist.
    """
    try:
        # Convert place_id to ObjectId
        place_object_id = ObjectId(place_id)
        
        # Check if place already exists in wishlist
        user = mongo.db.users.find_one({"_id": user_id})
        if not user:
            return False
        
        if place_object_id in user.get("wishlist", []):
            return False  # Place already in wishlist
        
        # Add place to wishlist
        result = mongo.db.users.update_one(
            {"_id": user_id},
            {
                "$push": {"wishlist": place_object_id},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return result.modified_count > 0
    except Exception:
        return False

def remove_from_wishlist(mongo: PyMongo, user_id: str, place_id: str):
    """
    Remove a place from user's wishlist. Returns True if removed, False if user not found.
    """
    try:
        # Convert place_id to ObjectId
        place_object_id = ObjectId(place_id)
        
        # Remove place from wishlist
        result = mongo.db.users.update_one(
            {"_id": user_id},
            {
                "$pull": {"wishlist": place_object_id},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return result.modified_count > 0
    except Exception:
        return False

def get_wishlist(mongo: PyMongo, user_id: str):
    """
    Get user's wishlist with full place details. Returns list of places or empty list if user not found.
    """
    try:
        user = mongo.db.users.find_one({"_id": user_id})
        if not user:
            return []
        
        wishlist_ids = user.get("wishlist", [])
        if not wishlist_ids:
            return []
        
        # Get full place details for each wishlist item
        places = list(mongo.db.places.find({"_id": {"$in": wishlist_ids}}))
        
        # Convert ObjectIds to strings for JSON serialization
        for place in places:
            if '_id' in place:
                place['_id'] = str(place['_id'])
        
        return places
    except Exception:
        return []

def is_in_wishlist(mongo: PyMongo, user_id: str, place_id: str):
    """
    Check if a place is in user's wishlist. Returns True if found, False otherwise.
    """
    try:
        place_object_id = ObjectId(place_id)
        user = mongo.db.users.find_one({"_id": user_id})
        if not user:
            return False
        
        return place_object_id in user.get("wishlist", [])
    except Exception:
        return False 