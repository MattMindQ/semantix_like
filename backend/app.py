# backend/app.py
from flask import Flask
from flask_cors import CORS
from loguru import logger
from services.word_service import WordEmbeddingService
from services.game_service import GameService
from services.visualization_service import VisualizationService
from routes import register_routes

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    })

    # Configure logger
    logger.add("app.log", rotation="500 MB")

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    try:
        # Initialize services
        if test_config is None:
            word_service = WordEmbeddingService()
            game_service = GameService(word_service)
            visualization_service = VisualizationService(word_service)
            logger.info("Services initialized successfully")
        else:
            # Use test configuration
            word_service = test_config.get('word_service')
            game_service = test_config.get('game_service')
            visualization_service = test_config.get('visualization_service')
            logger.info("Test services initialized")

        # Register routes with the services
        register_routes(app, game_service, word_service, visualization_service)
        
        # Validate routes with dummy responses
        validate_routes(app)

    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise e

    return app

def validate_routes(app):
    """Validate all routes return something."""
    with app.test_client() as client:
        # Test GET endpoints
        get_endpoints = ['/api/game-state', '/api/visualization']
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            logger.info(f"Route {endpoint} validation status: {response.status_code}")

        # Test POST endpoints
        post_endpoints = {
            '/api/check-word': {'word': 'test'},
            '/api/use-joker': {'joker_type': 'high_similarity'},
            '/api/reset-game': {}
        }
        for endpoint, data in post_endpoints.items():
            response = client.post(endpoint, json=data)
            logger.info(f"Route {endpoint} validation status: {response.status_code}")

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app = create_app()
    app.run(debug=True)