# backend/test_config.py
"""Test configuration with dummy services for route validation."""

class DummyWordService:
    def calculate_similarity(self, word1, word2):
        return 0.5
        
    def get_most_similar_words(self, target_word, n=100):
        return [{'word': f'similar_{i}', 'similarity': 0.9 - (i * 0.1)} for i in range(n)]
        
    def get_words_in_range(self, target_word, min_sim, max_sim, n=5):
        return [{'word': f'range_{i}', 'similarity': (min_sim + max_sim)/2} for i in range(n)]

class DummyGameService:
    def get_state(self):
        return {
            'target_word': 'test',
            'attempts': [],
            'word_found': False,
            'similar_words': [],
            'jokers': {
                'high_similarity': {'remaining': 3, 'words_per_use': 5},
                'medium_similarity': {'remaining': 3, 'words_per_use': 5}
            }
        }
        
    def reset_game(self):
        return self.get_state()
        
    def save_attempt(self, word, similarity):
        state = self.get_state()
        state['attempts'].append({'word': word, 'similarity': similarity})
        return state
        
    def use_joker(self, joker_type):
        return {
            'joker_words': [{'word': f'joker_{i}', 'similarity': 0.75} for i in range(5)],
            'jokers': {
                'high_similarity': {'remaining': 2, 'words_per_use': 5},
                'medium_similarity': {'remaining': 3, 'words_per_use': 5}
            }
        }

class DummyVisualizationService:
    def prepare_3d_visualization(self, target_word, guessed_words):
        return [{
            'word': word,
            'coordinates': [0.0, 0.0, 0.0],
            'is_target': word == target_word,
            'similarity': 0.5
        } for word in [target_word] + guessed_words]

TEST_CONFIG = {
    'word_service': DummyWordService(),
    'game_service': DummyGameService(),
    'visualization_service': DummyVisualizationService()
}