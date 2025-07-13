from flask_pymongo import PyMongo
from datetime import datetime, timezone

# This is a schema representation for reference; PyMongo does not require explicit schemas like Mongoose.
# You can use this as a helper for validation or documentation.

user_schema = {
    "_id": str,  # Firebase UID
    "name": str,
    "email": str,
    "location": str,
    "persona": str,  # e.g., 'adventurous', 'aesthetic', etc.
    "preferences": {
        "vibe": list,  # e.g., ['cozy', 'quiet']
        "category": list  # e.g., ['cafe', 'park']
    },
    "wishlist": list,  # Array of ObjectIds for places the user has added to wishlist
    "created_at": datetime,
    "updated_at": datetime
}

# Example helper for inserting a user (to be used in your controller or route):
def create_user(mongo: PyMongo, user_data: dict):
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
    return mongo.db.users.insert_one(user_doc)
