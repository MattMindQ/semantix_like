# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from loguru import logger
import os
import sys
import time
from typing import Dict, Tuple
app = Flask(__name__)
CORS(app)

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")
if not os.getenv('VERCEL_ENV'):
    logger.add("app.log", rotation="500 MB", level="INFO")

# Get the Model API URL from environment variables
MODEL_API_URL = os.getenv('MODEL_API_URL', 'https://miroir-semantix-api.hf.space')


import os
from urllib.parse import urlparse, urlunparse

def get_local_api_url() -> str:
    """Get the local API URL with correct port"""
    return "http://localhost:8000"  # FastAPI development server port

def is_local_url(url: str) -> bool:
    """Check if URL is local (localhost or 127.0.0.1)"""
    parsed = urlparse(url)
    return parsed.hostname in ('localhost', '127.0.0.1', '0.0.0.0')

def check_huggingface_connection() -> Tuple[bool, str, float]:
    """
    Check connection to Hugging Face service.
    Falls back to local check if MODEL_API_URL is local.
    Returns: (success, message, response_time)
    """
    try:
        start_time = time.time()
        
        # Check if we're in local development
        if is_local_url(MODEL_API_URL):
            local_url = get_local_api_url()
            logger.info(f"Local environment detected, checking FastAPI service at {local_url}")
            try:
                response = requests.get(f"{local_url}/")
                response_time = time.time() - start_time
                return True, "Connected to local FastAPI service", response_time
            except requests.RequestException as e:
                logger.warning(f"Local service not responding: {str(e)}")
                return False, "Local FastAPI service not available", 0.0
        
        # Production Hugging Face check
        api_url = f"{MODEL_API_URL}/api/health"
        logger.info(f"Checking Hugging Face service at: {api_url}")
        
        response = requests.get(api_url)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            return True, "Connected to Hugging Face service", response_time
        else:
            return False, f"Hugging Face service returned status {response.status_code}", response_time
            
    except requests.RequestException as e:
        logger.error(f"Connection error: {str(e)}")
        return False, f"Failed to connect to service: {str(e)}", 0.0

@app.route('/api/system-health', methods=['GET'])
def system_health():
    """
    Comprehensive health check endpoint with local environment support.
    """
    try:
        actual_url = get_local_api_url() if is_local_url(MODEL_API_URL) else MODEL_API_URL
        logger.info(f"Performing system health check for: {actual_url}")
        
        # Check service connection
        healthy, message, response_time = check_huggingface_connection()
        
        # Determine environment
        environment = "local" if is_local_url(MODEL_API_URL) else "production"
        
        health_status = {
            "status": "healthy" if healthy else "degraded",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "environment": environment,
            "services": {
                "proxy": {
                    "status": "running",
                    "message": "Proxy server is running"
                },
                "api": {
                    "status": "healthy" if healthy else "error",
                    "message": message,
                    "response_time": f"{response_time:.3f}s",
                    "endpoint": actual_url
                }
            }
        }
        
        logger.info(f"Health check results: {health_status}")
        
        # In local development, return 200 even if service is down
        status_code = 200 if environment == "local" or healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        error_response = {
            "status": "error",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Health check failed: {str(e)}"
        }
        logger.exception("Health check failed")
        return jsonify(error_response), 500
    
@app.route('/api/visualization', methods=['GET'])
def get_visualization():
    try:
        response = requests.get(f"{MODEL_API_URL}/api/visualization")
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error getting visualization")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-game', methods=['POST'])
def reset_game():
    try:
        response = requests.post(f"{MODEL_API_URL}/api/reset-game")
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error resetting game")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-word', methods=['POST'])
def check_word():
    try:
        data = request.get_json()
        response = requests.post(f"{MODEL_API_URL}/api/check-word", json=data)
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error checking word")
        return jsonify({'error': str(e)}), 500

@app.route('/api/use-joker', methods=['POST', 'OPTIONS'])
def use_joker():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        response = requests.post(f"{MODEL_API_URL}/api/use-joker", json=data)
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error using joker")
        return jsonify({'error': str(e)}), 500

@app.route('/api/game-state', methods=['GET'])
def get_game_state():
    try:
        logger.info(f"Fetching game state from {MODEL_API_URL}/api/game-state")
        response = requests.get(f"{MODEL_API_URL}/api/game-state")
        logger.info(f"Response status: {response.status_code}")
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error getting game state")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        response = requests.get(f"{MODEL_API_URL}/api/health")
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error checking health")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-center-word', methods=['POST'])
def get_center_word():
    try:
        data = request.get_json()
        response = requests.post(f"{MODEL_API_URL}/api/get-center-word", json=data)
        return jsonify(response.json())
    except Exception as e:
        logger.exception("Error getting center word")
        return jsonify({'error': str(e)}), 500

# Only use this for Vercel
if os.getenv('VERCEL_ENV'):
    app = app.wsgi_app
else:
    # For local development
    if __name__ == '__main__':
        logger.info(f"Starting Flask app with MODEL_API_URL: {MODEL_API_URL}")
        app.run(host='0.0.0.0', port=5000, debug=True)