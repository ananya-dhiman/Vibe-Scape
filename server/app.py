from flask import Flask, request
from flask_pymongo import PyMongo
from config import Config
from datetime import datetime
from flask_cors import CORS
from Auth.firebase_admin import initialize_firebase

# Initialize PyMongo
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Initialize Firebase Admin SDK
    initialize_firebase()
    
    # Make mongo available to routes
    app.mongo = mongo
    # CORS: allow all origins and credentials for dev
    CORS(app, supports_credentials=True, origins=["*"])
    
    # Allow OPTIONS requests through (for CORS preflight)
    @app.before_request
    def handle_options():
        if request.method == 'OPTIONS':
            return '', 200
    
    # Register blueprints
    from routes.user_routes import user_bp
    from routes.place_routes import place_bp
    from routes.tomtom_routes import tomtom_bp
    from routes.fallback_routes import fallback_bp
    from routes.rag_routes import rag_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(place_bp, url_prefix='/api/places')
    app.register_blueprint(tomtom_bp, url_prefix='/api/tomtom')
    app.register_blueprint(fallback_bp, url_prefix='/api/fallback')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')
    
    # Create indexes for better performance
    with app.app_context():
        try:
            # Create geospatial index for places
            mongo.db.places.create_index([("original.coordinates", "2dsphere")])
            # Create indexes for common queries
            mongo.db.users.create_index("email")
            mongo.db.places.create_index("original.fsq_id")
            mongo.db.places.create_index("original.city")
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    @app.route('/')
    def home():
        return {
            "message": "Vibe-Scape API",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "database": "connected" if mongo.db is not None else "disconnected"
        }
    
    return app

if __name__ == "__main__":
    app = create_app()
    # No HTTP->HTTPS redirect logic for dev
    app.run(debug=True, host='0.0.0.0', port=5000) 