from flask import Blueprint, request, jsonify, current_app
from controllers.user_controller import add_user, update_user, get_user, delete_user, add_to_wishlist, remove_from_wishlist, get_wishlist, is_in_wishlist, create_user_with_firebase
from middleware.auth_middleware import require_auth, optional_auth

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['POST'])
@require_auth
def create_user():
    """Create a new user with Firebase authentication"""
    try:
        # User info comes from Firebase token verification
        firebase_uid = request.user['uid']
        
        data = request.get_json() or {}
        
        # Create user in our database
        user_id = create_user_with_firebase(current_app.mongo, firebase_uid, data)
        
        if user_id is None:
            return jsonify({"error": "User already exists"}), 409
        
        return jsonify({
            "message": "User created successfully",
            "user_id": str(user_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user by Firebase UID"""
    try:
        firebase_uid = request.user['uid']
        user = get_user(current_app.mongo, firebase_uid)
        
        if user:
            if '_id' in user:
                user['_id'] = str(user['_id'])
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>', methods=['GET'])
@optional_auth
def get_user_route(user_id):
    """Get user by ID (optional auth)"""
    try:
        user = get_user(current_app.mongo, user_id)
        if user:
            if '_id' in user:
                user['_id'] = str(user['_id'])
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/me', methods=['PUT'])
@require_auth
def update_current_user():
    """Update current user data"""
    try:
        firebase_uid = request.user['uid']
        data = request.get_json()
        
        # Remove _id from update data if present
        data.pop('_id', None)
        
        success = update_user(current_app.mongo, firebase_uid, data)
        if success:
            return jsonify({"message": "User updated successfully"}), 200
        return jsonify({"error": "User not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>', methods=['PUT'])
@require_auth
def update_user_route(user_id):
    """Update user data (requires auth)"""
    try:
        data = request.get_json()
        
        # Remove _id from update data if present
        data.pop('_id', None)
        
        success = update_user(current_app.mongo, user_id, data)
        if success:
            return jsonify({"message": "User updated successfully"}), 200
        return jsonify({"error": "User not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/me', methods=['DELETE'])
@require_auth
def delete_current_user():
    """Delete current user"""
    try:
        firebase_uid = request.user['uid']
        success = delete_user(current_app.mongo, firebase_uid)
        if success:
            return jsonify({"message": "User deleted successfully"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
@require_auth
def delete_user_route(user_id):
    """Delete user by ID (requires auth)"""
    try:
        success = delete_user(current_app.mongo, user_id)
        if success:
            return jsonify({"message": "User deleted successfully"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Wishlist routes
@user_bp.route('/me/wishlist', methods=['GET'])
@require_auth
def get_current_user_wishlist():
    """Get current user's wishlist with full place details"""
    try:
        firebase_uid = request.user['uid']
        places = get_wishlist(current_app.mongo, firebase_uid)
        return jsonify({
            "wishlist": places,
            "count": len(places)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/wishlist', methods=['GET'])
@optional_auth
def get_user_wishlist(user_id):
    """Get user's wishlist with full place details (optional auth)"""
    try:
        places = get_wishlist(current_app.mongo, user_id)
        return jsonify({
            "wishlist": places,
            "count": len(places)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/me/wishlist/<place_id>', methods=['POST'])
@require_auth
def add_place_to_current_user_wishlist(place_id):
    """Add a place to current user's wishlist"""
    try:
        firebase_uid = request.user['uid']
        success = add_to_wishlist(current_app.mongo, firebase_uid, place_id)
        if success:
            return jsonify({
                "message": "Place added to wishlist successfully"
            }), 200
        else:
            # Check if user exists
            user = get_user(current_app.mongo, firebase_uid)
            if not user:
                return jsonify({"error": "User not found"}), 404
            else:
                return jsonify({"error": "Place already in wishlist or invalid place ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/wishlist/<place_id>', methods=['POST'])
@require_auth
def add_place_to_wishlist(user_id, place_id):
    """Add a place to user's wishlist (requires auth)"""
    try:
        success = add_to_wishlist(current_app.mongo, user_id, place_id)
        if success:
            return jsonify({
                "message": "Place added to wishlist successfully"
            }), 200
        else:
            # Check if user exists
            user = get_user(current_app.mongo, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            else:
                return jsonify({"error": "Place already in wishlist or invalid place ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/me/wishlist/<place_id>', methods=['DELETE'])
@require_auth
def remove_place_from_current_user_wishlist(place_id):
    """Remove a place from current user's wishlist"""
    try:
        firebase_uid = request.user['uid']
        success = remove_from_wishlist(current_app.mongo, firebase_uid, place_id)
        if success:
            return jsonify({
                "message": "Place removed from wishlist successfully"
            }), 200
        else:
            # Check if user exists
            user = get_user(current_app.mongo, firebase_uid)
            if not user:
                return jsonify({"error": "User not found"}), 404
            else:
                return jsonify({"error": "Place not found in wishlist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/wishlist/<place_id>', methods=['DELETE'])
@require_auth
def remove_place_from_wishlist(user_id, place_id):
    """Remove a place from user's wishlist (requires auth)"""
    try:
        success = remove_from_wishlist(current_app.mongo, user_id, place_id)
        if success:
            return jsonify({
                "message": "Place removed from wishlist successfully"
            }), 200
        else:
            # Check if user exists
            user = get_user(current_app.mongo, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            else:
                return jsonify({"error": "Place not found in wishlist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/me/wishlist/<place_id>/check', methods=['GET'])
@require_auth
def check_current_user_wishlist_status(place_id):
    """Check if a place is in current user's wishlist"""
    try:
        firebase_uid = request.user['uid']
        is_in_list = is_in_wishlist(current_app.mongo, firebase_uid, place_id)
        return jsonify({
            "is_in_wishlist": is_in_list
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/wishlist/<place_id>/check', methods=['GET'])
@optional_auth
def check_wishlist_status(user_id, place_id):
    """Check if a place is in user's wishlist (optional auth)"""
    try:
        is_in_list = is_in_wishlist(current_app.mongo, user_id, place_id)
        return jsonify({
            "is_in_wishlist": is_in_list
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 