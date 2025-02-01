from flask import Flask
from flask_cors import CORS
from flask import request
from loguru import logger
import os
import sys
from services.word_service import WordEmbeddingService
from services.game_service import GameService
from services.visualization_service import VisualizationService
from routes import register_routes

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configure CORS for all origins in production
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "https://*.vercel.app", "https://*.now.sh"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    })

    # Configure logger to work both locally and on Vercel
    logger.remove()  # Remove default handler
    logger.add(sys.stdout, level="INFO")  # Add stdout handler
    if not os.getenv('VERCEL_ENV'):
        # Add file logging only in local development
        logger.add("app.log", rotation="500 MB", level="INFO")

    @app.after_request
    def after_request(response):
        # Allow requests from Vercel frontend
        allowed_origins = [
            'http://localhost:5173',  # Development
            'https://*.vercel.app',   # Vercel deployment
            'https://*.now.sh'        # Vercel deployment (alternative domain)
        ]
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
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
        
        if not os.getenv('VERCEL_ENV'):
            # Only run validation in development
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

# Create the app instance
app = create_app()

if __name__ == '__main__':
    logger.info("Starting Flask application in development mode")
    app.run(debug=True)

# For Vercel deployment
app = app.wsgi_app