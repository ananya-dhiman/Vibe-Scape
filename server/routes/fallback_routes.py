from flask import Blueprint, request, jsonify, current_app
from services.fallback_service import FallbackService

fallback_bp = Blueprint('fallback', __name__)

@fallback_bp.route('/search', methods=['POST'])
def search_with_fallback():
    """
    Search for places with fallback logic:
    - First check database for existing matches
    - If < 5 results, fetch from TomTom and scrape Reddit reviews
    - Store new places with reviews in database
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Extract parameters
        city = data.get('city', '')
        category = data.get('category', '')
        vibe_tags = data.get('vibe_tags', [])
        min_results = data.get('min_results', 5)
        
        # Validate required parameters
        if not city or not category:
            return jsonify({
                'error': 'Missing required parameters: city and category'
            }), 400
        
        # Ensure vibe_tags is a list
        if isinstance(vibe_tags, str):
            vibe_tags = [vibe_tags]
        
        print(f"🔍 Search request: city={city}, category={category}, vibe_tags={vibe_tags}")
        
        # Initialize fallback service
        fallback_service = FallbackService(current_app.mongo)
        
        # Perform search with fallback
        result = fallback_service.search_places_with_fallback(
            city=city,
            category=category,
            vibe_tags=vibe_tags,
            min_results=min_results
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Found {result['count']} places",
                'source': result['source'],
                'places': result['places'],
                'count': result['count'],
                'fallback_used': result.get('fallback_used', False),
                'tomtom_fetched': result.get('tomtom_fetched', 0),
                'reviews_scraped': result.get('reviews_scraped', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'places': [],
                'count': 0
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'places': [],
            'count': 0
        }), 500

@fallback_bp.route('/test', methods=['GET'])
def test_fallback():
    """
    Test endpoint for fallback service
    """
    try:
        # Test with sample data
        test_data = {
            'city': 'Delhi',
            'category': 'cafe',
            'vibe_tags': ['aesthetic'],
            'min_results': 3
        }
        
        fallback_service = FallbackService(current_app.mongo)
        result = fallback_service.search_places_with_fallback(
            city=test_data['city'],
            category=test_data['category'],
            vibe_tags=test_data['vibe_tags'],
            min_results=test_data['min_results']
        )
        
        return jsonify({
            'success': True,
            'message': 'Fallback service test completed',
            'test_data': test_data,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500 