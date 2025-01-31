# file location: backend/services/visualization_service.py

import numpy as np
import umap  # pip install umap-learn
from loguru import logger

class VisualizationService:
    def __init__(self, word_service):
        self.word_service = word_service

    def _compute_color(self, similarity: float) -> str:
        """
        Given a similarity in [0,1], return an RGB color from blue (0) to red (1).
        """
        # Clamp similarity to [0,1] just in case
        sim = max(0.0, min(1.0, similarity))
        # Simple gradient from blue (0,0,255) to red (255,0,0)
        r = int(sim * 255)
        g = 0
        b = int((1.0 - sim) * 255)
        return f"rgb({r}, {g}, {b})"

    def prepare_3d_visualization(self, target_word: str, guessed_words: list[str]):
        try:
            embeddings = []
            valid_words = []

            target_embedding = self.word_service.get_vector(target_word)
            if target_embedding is None:
                return [{
                    'word': "???",
                    'coordinates': [0, 0, 0],
                    'is_target': True,
                    'similarity': 1.0,
                    'color': 'rgb(255, 0, 0)'
                }]

            embeddings.append(target_embedding)
            valid_words.append(target_word)

            for word in guessed_words:
                vec = self.word_service.get_vector(word)
                if vec is not None and not np.all(vec == 0):
                    embeddings.append(vec)
                    valid_words.append(word)

            # if there's only 1 or 2 embeddings total, no manifold can form
            if len(embeddings) < 3:
                return self._simple_fallback(target_word, valid_words, embeddings)

            # Otherwise, do UMAP
            embeddings_array = np.array(embeddings)
            neighbors = min(5, len(embeddings) - 1)

            import umap
            reducer = umap.UMAP(
                n_components=3,
                n_neighbors=neighbors,
                min_dist=0.1,
                metric='cosine',
                random_state=42
            )
            embedding_3d = reducer.fit_transform(embeddings_array)

            # Re-center target at (0,0,0)
            target_coords = embedding_3d[0]
            embedding_3d -= target_coords

            result = []
            for i, word in enumerate(valid_words):
                if i == 0:
                    # target
                    result.append({
                        'word': "???",
                        'coordinates': embedding_3d[i].tolist(),
                        'is_target': True,
                        'similarity': 1.0,
                        'color': 'rgb(255, 0, 0)'
                    })
                else:
                    sim = self.word_service.calculate_similarity(target_word, word)
                    color = self._compute_color(sim)
                    result.append({
                        'word': word,
                        'coordinates': embedding_3d[i].tolist(),
                        'is_target': False,
                        'similarity': sim,
                        'color': color
                    })
            return result

        except Exception:
            logger.exception("Error preparing 3D visualization with UMAP")
            return [{
                'word': "???",
                'coordinates': [0, 0, 0],
                'is_target': True,
                'similarity': 1.0,
                'color': 'rgb(255, 0, 0)'
            }]

    def _simple_fallback(self, target_word: str, valid_words: list[str], embeddings: list[np.ndarray]):
        """
        Return a minimal 3D layout without UMAP
        when the dataset is too small to form a manifold.
        """
        # If there's only the target, just place it at the origin.
        if len(embeddings) <= 1:
            return [{
                'word': "???",
                'coordinates': [0, 0, 0],
                'is_target': True,
                'similarity': 1.0,
                'color': 'rgb(255, 0, 0)'
            }]

        # We have at least 2 points (target + 1 guess)
        coords = np.random.randn(len(embeddings), 3) * 0.1
        coords[0] = [0, 0, 0]  # target at origin

        result = []
        for i, word in enumerate(valid_words):
            if i == 0:
                # target
                result.append({
                    'word': "???",
                    'coordinates': coords[i].tolist(),
                    'is_target': True,
                    'similarity': 1.0,
                    'color': 'rgb(255, 0, 0)'
                })
            else:
                sim = self.word_service.calculate_similarity(target_word, word)
                color = self._compute_color(sim)
                result.append({
                    'word': word,
                    'coordinates': coords[i].tolist(),
                    'is_target': False,
                    'similarity': sim,
                    'color': color
                })

        return result
