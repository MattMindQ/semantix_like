# backend/routes.py
from flask import jsonify, request
from loguru import logger

def register_routes(app, game_service, word_service, visualization_service):
    """Register all routes for the application."""
    
    @app.route('/api/visualization', methods=['GET'])
    def get_visualization():
        try:
            game_state = game_service.get_state()
            target_word = game_state['target_word']
            guessed_words = [attempt['word'] for attempt in game_state['attempts']]
            
            viz_data = visualization_service.prepare_3d_visualization(
                target_word, 
                guessed_words
            )
            
            return jsonify(viz_data)
        except Exception as e:
            logger.exception("Error getting visualization")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/reset-game', methods=['POST'])
    def reset_game():
        try:
            new_state = game_service.reset_game()
            logger.info(f"Game reset with new state: {new_state}")
            return jsonify(new_state)
        except Exception as e:
            logger.exception("Error resetting game")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/check-word', methods=['POST'])
    def check_word():
        try:
            data = request.get_json()
            guess_word = data.get('word', '').lower().strip()
            
            if not guess_word:
                return jsonify({'error': 'Le mot ne peut pas être vide'}), 400
            
            state = game_service.get_state()
            target_word = state['target_word']
            
            similarity = word_service.calculate_similarity(target_word, guess_word)
            
            if similarity > 0:
                updated_state = game_service.save_attempt(guess_word, similarity)
                response = {
                    'similarity': similarity,
                    'history': updated_state['attempts'],
                    'word_found': updated_state.get('word_found', False),
                    'similar_words': updated_state.get('similar_words', []) 
                                   if updated_state.get('word_found', False) else []
                }
            else:
                response = {
                    'error': 'Le mot n\'a pas été trouvé dans le dictionnaire',
                    'similarity': 0,
                    'history': state['attempts']
                }
            
            logger.info(f"Word check response: {response}")
            return jsonify(response)
            
        except Exception as e:
            logger.exception("Error checking word")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/use-joker', methods=['POST', 'OPTIONS'])
    def use_joker():
        if request.method == 'OPTIONS':
            return '', 204
            
        try:
            data = request.get_json()
            joker_type = data.get('joker_type')
            
            logger.info(f"Received joker request with type: {joker_type}")
            
            if not joker_type:
                logger.error("No joker type provided")
                return jsonify({'error': 'Joker type is required'}), 400
                
            result = game_service.use_joker(joker_type)
            
            logger.info("Joker response:")
            logger.info(f"Words: {[w['word'] for w in result['joker_words']]}")
            logger.info(f"Remaining jokers: {result['jokers']}")
            
            return jsonify(result)
            
        except ValueError as e:
            logger.error(f"ValueError in use_joker: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception("Error using joker")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/game-state', methods=['GET'])
    def get_game_state():
        try:
            state = game_service.get_state()
            logger.info(f"Retrieved game state: {state}")
            return jsonify(state)
        except Exception as e:
            logger.exception("Error getting game state")
            return jsonify({'error': str(e)}), 500

    # Add a health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify API is running."""
        return jsonify({
            'status': 'healthy',
            'services': {
                'game_service': game_service is not None,
                'word_service': word_service is not None,
                'visualization_service': visualization_service is not None
            }
        })
    
    @app.route('/api/get-center-word', methods=['POST'])
    def get_center_word():
        """Compute and return a new 'center word' from chosen words + target word."""
        data = request.get_json()
        chosen_words = data.get('chosen_words', [])
        logger.info(f"Received chosen words: {chosen_words}")
        
        center_word_info = game_service.get_center_word_power(chosen_words)
        if not center_word_info:
            return jsonify({"error": "No center word found."}), 400
        
        return jsonify(center_word_info)