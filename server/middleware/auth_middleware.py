from functools import wraps
from flask import request, jsonify, current_app
from Auth.firebase_admin import verify_firebase_token

def require_auth(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        # Check if it's a Bearer token
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Extract the token
        token = auth_header.split('Bearer ')[1]
        
        # Verify the Firebase token
        result = verify_firebase_token(token)
        
        if not result['success']:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Add user info to request
        request.user = {
            'uid': result['uid'],
            'email': result['email'],
            'name': result['name'],
            'picture': result['picture']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            # Extract the token
            token = auth_header.split('Bearer ')[1]
            
            # Verify the Firebase token
            result = verify_firebase_token(token)
            
            if result['success']:
                # Add user info to request
                request.user = {
                    'uid': result['uid'],
                    'email': result['email'],
                    'name': result['name'],
                    'picture': result['picture']
                }
            else:
                request.user = None
        else:
            request.user = None
        
        return f(*args, **kwargs)
    
    return decorated_function 