from flask import Blueprint, request, jsonify, current_app
from controllers.place_controller import add_place, find_places, update_place, fetch_all_places, bulk_insert_places
from datetime import datetime
from bson import ObjectId

place_bp = Blueprint('place_bp', __name__)

@place_bp.route('/', methods=['POST'])
def create_place():
    """Create a new place"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get("original", {}).get("fsq_id"):
            return jsonify({"error": "Missing required field: original.fsq_id"}), 400
        if not data.get("original", {}).get("name"):
            return jsonify({"error": "Missing required field: original.name"}), 400
        
        # Add place using controller
        place_id = add_place(current_app.mongo, data)
        
        if place_id is None:
            return jsonify({"error": "Place already exists"}), 409
        
        return jsonify({
            "message": "Place created successfully",
            "place_id": str(place_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@place_bp.route('/bulk', methods=['POST'])
def create_places_bulk():
    """Create multiple places at once"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({"error": "Data must be an array of places"}), 400
        
        # Validate required fields for each place
        for i, place_data in enumerate(data):
            if not place_data.get("original", {}).get("fsq_id"):
                return jsonify({"error": f"Missing fsq_id for place at index {i}"}), 400
            if not place_data.get("original", {}).get("name"):
                return jsonify({"error": f"Missing name for place at index {i}"}), 400
        
        # Bulk insert places
        inserted_ids = bulk_insert_places(current_app.mongo, data)
        
        return jsonify({
            "message": f"Successfully inserted {len(inserted_ids)} places",
            "inserted_count": len(inserted_ids),
            "place_ids": inserted_ids
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@place_bp.route('/', methods=['GET'])
def get_all_places():
    """Fetch all places"""
    try:
        places = fetch_all_places(current_app.mongo)
        for place in places:
            if '_id' in place:
                place['_id'] = str(place['_id'])
        return jsonify({"places": places, "count": len(places)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@place_bp.route('/search', methods=['GET'])
def search_places():
    """Search places by vibe tags, category, or city"""
    try:
        vibe_tags = request.args.get('vibe_tags')
        category = request.args.get('category')
        city = request.args.get('city')
        
        # Convert vibe_tags from comma-separated string to list
        if vibe_tags:
            vibe_tags = vibe_tags.split(',')
        
        places = find_places(current_app.mongo, vibe_tags, category, city)
        
        # Convert ObjectIds to strings for JSON serialization
        for place in places:
            if '_id' in place:
                place['_id'] = str(place['_id'])
        
        return jsonify({
            "places": places,
            "count": len(places)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@place_bp.route('/<place_id>', methods=['GET'])
def get_place_by_id(place_id):
    """Fetch a single place by its ID"""
    try:
        place = current_app.mongo.db.places.find_one({"_id": ObjectId(place_id)})
        if not place:
            return jsonify({"error": "Place not found"}), 404
        if '_id' in place:
            place['_id'] = str(place['_id'])
        return jsonify(place), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@place_bp.route('/<place_id>', methods=['PUT'])
def update_place_route(place_id):
    """Update place data"""
    try:
        data = request.get_json()
        
        # Remove _id from update data if present
        data.pop('_id', None)
        
        success = update_place(current_app.mongo, place_id, data)
        if success:
            return jsonify({"message": "Place updated successfully"}), 200
        return jsonify({"error": "Place not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

 