# file location: backend/services/game_service.py

import json
from pathlib import Path
from loguru import logger
import random
from typing import Dict, List

class GameService:
    def __init__(self, word_service):
        self.data_file = Path('data/game_state.json')
        self.words_file = Path('data/word_list.json')
        self.word_service = word_service
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Initialize game state file if it doesn't exist."""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(exist_ok=True)
            self._save_state(self._create_initial_state())

    def _create_initial_state(self) -> Dict:
        """Create a new game state with default values from config."""
        from config.game_config import GAME_CONFIG, CURRENT_DIFFICULTY
        difficulty_config = GAME_CONFIG["difficulty"][CURRENT_DIFFICULTY]
        
        return {
            'target_word': self._get_random_word(),
            'attempts': [],
            'word_found': False,
            'similar_words': [],
            'jokers': {
                'high_similarity': {
                    'remaining': difficulty_config['jokers_high_similarity'],
                    'words_per_use': difficulty_config['words_per_joker']
                },
                'medium_similarity': {
                    'remaining': difficulty_config['jokers_medium_similarity'],
                    'words_per_use': difficulty_config['words_per_joker']
                }
            }
        }

    def reset_game(self) -> Dict:
        """Reset the game with a new random word and fresh jokers."""
        try:
            new_state = self._create_initial_state()
            self._save_state(new_state)
            return new_state
        except Exception:
            logger.exception("Error resetting game")
            raise

    def use_joker(self, joker_type: str) -> Dict:
        """Use a joker to get words within a specific similarity range."""
        try:
            logger.info(f"Using joker of type: {joker_type}")
            state = self._load_state()

            # Validate joker type and availability
            if joker_type not in ['high_similarity', 'medium_similarity']:
                logger.error(f"Invalid joker type: {joker_type}")
                raise ValueError("Invalid joker type")
                
            joker = state['jokers'][joker_type]
            if joker['remaining'] <= 0:
                logger.warning(f"No {joker_type} jokers remaining")
                raise ValueError("No jokers remaining of this type")
                
            # Similarity range
            sim_range = {
                'high_similarity': (0.7, 0.8),
                'medium_similarity': (0.6, 0.7)
            }[joker_type]

            target = state['target_word']
            logger.info(f"Target word: {target}, range: {sim_range}")
            
            # Get words in range
            similar_words = self.word_service.get_words_in_range(
                target,
                sim_range[0],
                sim_range[1],
                n=joker['words_per_use']
            )
            
            # Log the results
            logger.info(f"Found {len(similar_words)} words using joker:")
            for w in similar_words:
                logger.info(f"- {w['word']} (similarity: {w['similarity']:.3f})")

            # Update joker count
            joker['remaining'] -= 1
            self._save_state(state)
            
            logger.info(f"Remaining {joker_type} jokers: {joker['remaining']}")
            
            return {'joker_words': similar_words, 'jokers': state['jokers']}

        except Exception:
            logger.exception("Error using joker")
            raise
    
    def get_center_word_power(self, chosen_words: List[str]) -> Dict[str, float]:
        """
        Compute and return the “center word” based on the user’s chosen words
        and the current target word. 
        """
        try:
            # Load current state to get the target word
            state = self._load_state()
            target_word = state['target_word']

            result = self.word_service.get_center_word(chosen_words, target_word)
            if not result:
                logger.warning("Center word power returned no result.")
                return {}
            
            logger.info(f"Center word found: {result['word']} (sim={result['similarity']:.3f})")
            return result

        except Exception:
            logger.exception("Error computing center word power")
            return {}

    def _get_random_word(self) -> str:
        """Get a random word from the game's word list."""
        try:
            with open(self.words_file, 'r', encoding='utf-8') as f:
                words_data = json.load(f)
                return random.choice(words_data['words'])
        except Exception:
            logger.exception("Error loading word list")
            return "mathématiques"  # fallback word

    def save_attempt(self, word: str, similarity: float) -> Dict:
        """Save a word attempt and update game state."""
        try:
            if not word or similarity <= 0:
                return self._load_state()
                
            state = self._load_state()
            state['attempts'].append({'word': word, 'similarity': similarity})
            
            # Check if word is found (similarity > 0.99)
            if similarity > 0.99:
                state['word_found'] = True
                # Get similar words when the target is found
                state['similar_words'] = self.word_service.get_most_similar_words(
                    state['target_word'], n=100
                )
                
            self._save_state(state)
            return state
        except Exception:
            logger.exception("Error saving attempt")
            raise

    def _save_state(self, state: Dict) -> None:
        """Save game state to file."""
        try:
            self.data_file.parent.mkdir(exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("Error saving game state")
            raise

    def _load_state(self) -> Dict:
        """Load game state from file."""
        try:
            if not self.data_file.exists():
                self._ensure_data_file()
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            logger.exception("Error loading game state")
            raise

    def get_state(self) -> Dict:
        """Get current game state."""
        try:
            return self._load_state()
        except Exception:
            logger.exception("Error getting game state")
            raise

    def get_history(self) -> List[Dict]:
        """Get history of attempts."""
        try:
            state = self._load_state()
            return state['attempts']
        except Exception:
            logger.exception("Error getting history")
            return []

