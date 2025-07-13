from flask_pymongo import PyMongo
from datetime import datetime, timezone

# This is a schema representation for reference; PyMongo does not require explicit schemas like Mongoose.
# You can use this as a helper for validation or documentation.

place_schema = {
    "original": {
        "fsq_id": str,
        "name": str,
        "category": str,
        "address": str,
        "locality": str,
        "city": str,
        "country": str,
        "photo_url": str,
        "coordinates": {
            "type": str,  # 'Point'
            "coordinates": list  # [lng, lat]
        }
    },
    "processed": {
        "vibe_tags": list,
        "emojis": list,
        "summary": str,
        "citations": [
            {
                "text": str,
                "source": str,
                "link": str
            }
        ]
    },
    "reviews": [
        {
            "source": str,  # 'TripAdvisor', 'Yelp', 'User'
            "text": str,
            "timestamp": datetime,
            "anonymous": bool
        }
    ],
    "created_at": datetime,
    "updated_at": datetime
}

# Example helper for inserting a place (to be used in your controller or route):
def create_place(mongo: PyMongo, place_data: dict):
    place_doc = {
        "original": {
            "fsq_id": place_data.get("original", {}).get("fsq_id"),
            "name": place_data.get("original", {}).get("name"),
            "category": place_data.get("original", {}).get("category"),
            "address": place_data.get("original", {}).get("address"),
            "locality": place_data.get("original", {}).get("locality"),
            "city": place_data.get("original", {}).get("city"),
            "country": place_data.get("original", {}).get("country"),
            "photo_url": place_data.get("original", {}).get("photo_url"),
            "coordinates": {
                "type": "Point",
                "coordinates": place_data.get("original", {}).get("coordinates", [])
            }
        },
        "processed": {
            "vibe_tags": place_data.get("processed", {}).get("vibe_tags", []),
            "emojis": place_data.get("processed", {}).get("emojis", []),
            "summary": place_data.get("processed", {}).get("summary"),
            "citations": place_data.get("processed", {}).get("citations", [])
        },
        "reviews": place_data.get("reviews", []),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    return mongo.db.places.insert_one(place_doc) 