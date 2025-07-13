from flask import Blueprint, request, jsonify, current_app
from RAG.flow_controller import FlowController
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
rag_bp = Blueprint('rag', __name__)

# Initialize flow controller
flow_controller = FlowController()

@rag_bp.route('/query', methods=['POST'])
def process_query():
    """
    Process natural language queries with intent classification and place search
    """
    try:
        data = request.get_json()
        
        # Extract parameters
        user_query = data.get('query', '')
        user_id = data.get('user_id')
        
        # Validate required parameters
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: query'
            }), 400
        
        # Initialize flow controller with MongoDB connection
        flow_controller = FlowController(current_app.mongo)
        
        # Process the query
        result = flow_controller.process_query(user_query, user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@rag_bp.route('/test', methods=['GET'])
def test_rag_flow():
    """
    Test endpoint for RAG flow controller
    """
    try:
        # Test queries
        test_queries = [
            "Find coffee shops in Delhi",
            "Tell me about Starbucks",
            "Show me aesthetic cafes in Delhi",
            "What are the best restaurants in Delhi?"
        ]
        
        flow_controller = FlowController(current_app.mongo)
        
        test_results = []
        for query in test_queries:
            try:
                result = flow_controller.process_query(query)
                test_results.append({
                    'query': query,
                    'success': result.get('success', False),
                    'intent': result.get('intent'),
                    'response': result.get('response', '')[:100] + '...' if len(result.get('response', '')) > 100 else result.get('response', '')
                })
            except Exception as e:
                test_results.append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': 'RAG flow controller test completed',
            'test_results': test_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500 