"""
WordVerse Game Configuration
This file contains all configurable parameters for the WordVerse game.
"""
from typing import Dict, Any

# Main configuration dictionary
GAME_CONFIG: Dict[str, Any] = {
    # Difficulty Settings
    "difficulty": {
        "easy": {
            "jokers_high_similarity": 3,
            "jokers_medium_similarity": 3,
            "words_per_joker": 5,
            "similarity_threshold": 0.99,  # Threshold to find the word
            "time_limit": 300,  # in seconds
        },
        "medium": {
            "jokers_high_similarity": 2,
            "jokers_medium_similarity": 2,
            "words_per_joker": 3,
            "similarity_threshold": 0.995,
            "time_limit": 240,
        },
        "hard": {
            "jokers_high_similarity": 1,
            "jokers_medium_similarity": 1,
            "words_per_joker": 2,
            "similarity_threshold": 0.998,
            "time_limit": 180,
        }
    },

    # Joker System
    "jokers": {
        "similarity_ranges": {
            "high": {
                "min": 0.7,
                "max": 0.8
            },
            "medium": {
                "min": 0.6,
                "max": 0.7
            }
        },
        "cooldown": 3,  # Number of guesses required between joker uses
    },

    # Scoring System
    "scoring": {
        "base_points": 1000,
        "time_bonus": {
            "enabled": True,
            "points_per_second": 10,
        },
        "joker_penalty": {
            "high_similarity": -100,
            "medium_similarity": -50,
        },
        "streak_bonus": {
            "enabled": True,
            "threshold": 0.8,  # Similarity threshold for streak
            "multiplier": 1.5,
        }
    },

    # Game Rules
    "rules": {
        "max_attempts": 0,  # 0 for unlimited
        "min_word_length": 3,
        "show_target_word": False,  # If false, target word is hidden until found
        "allow_partial_matches": True,
    },

    # UI/UX
    "interface": {
        "history_size": 50,  # Number of words to show in history
        "visualization_auto_toggle": True,  # Auto show visualization on key moments
        "visualization_moments": ["word_found", "joker_used"],
        "feedback_levels": ["very_cold", "cold", "warm", "hot", "very_hot"],
    },

    # Word Selection
    "word_selection": {
        "categories": ["general", "science", "nature", "technology"],
        "difficulty_weights": {
            "easy": {"common": 0.8, "uncommon": 0.2},
            "medium": {"common": 0.5, "uncommon": 0.5},
            "hard": {"common": 0.2, "uncommon": 0.8}
        },
    },

    # Player Progression
    "progression": {
        "levels_enabled": True,
        "xp_per_game": 100,
        "level_thresholds": [0, 1000, 2500, 5000, 10000],
        "rewards": {
            "level_2": {"bonus_joker": "high_similarity"},
            "level_3": {"bonus_time": 60},
            "level_4": {"bonus_joker": "medium_similarity"},
            "level_5": {"unlimited_time": True}
        }
    }
}

# Current active difficulty level
CURRENT_DIFFICULTY = "medium"

def get_current_config() -> Dict[str, Any]:
    """Get the current game configuration based on difficulty."""
    base_config = GAME_CONFIG.copy()
    difficulty_config = base_config["difficulty"][CURRENT_DIFFICULTY]
    
    # Merge difficulty-specific settings into base config
    for key, value in difficulty_config.items():
        if key in base_config:
            base_config[key] = value
            
    return base_config