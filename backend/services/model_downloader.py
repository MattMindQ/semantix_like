import os
import requests
from loguru import logger
from pathlib import Path

def download_model(url: str, model_path: str):
    """Download the model file if it doesn't exist."""
    if os.path.exists(model_path):
        logger.info(f"Model file already exists at {model_path}")
        return

    logger.info(f"Downloading model from {url}")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        with open(model_path, 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)
                
        logger.info(f"Model downloaded successfully to {model_path}")
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise