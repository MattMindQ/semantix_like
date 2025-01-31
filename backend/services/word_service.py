from loguru import logger
import numpy as np
from typing import List, Dict
import random
from gensim.models import KeyedVectors

class WordEmbeddingService:
    def __init__(self, fasttext_path='data/cc.fr.300.vec'):
        """
        Initialize the service by loading pre-trained FastText embeddings from .vec file.
        
        :param fasttext_path: Path to the FastText .vec file
        """
        try:
            logger.info("Loading FastText embeddings from .vec file...")
            self.model = KeyedVectors.load_word2vec_format(fasttext_path)
            
            # Build a quick-access dictionary {word: vector}
            self.vocab_vectors = {
                word: self.model[word]
                for word in self.model.index_to_key
            }
            logger.info(f"FastText model loaded successfully with "
                       f"{len(self.vocab_vectors)} words in the vocabulary.")
        except Exception:
            logger.exception("Failed to load FastText model from path: "
                           f"{fasttext_path}")
            raise

    def calculate_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate semantic similarity between two words using FastText vectors.
        Returns 0.0 if either word is missing from the vocabulary.
        """
        try:
            w1, w2 = word1.lower(), word2.lower()
            if w1 not in self.model or w2 not in self.model:
                logger.warning(f"One or both words not in FastText vocab: '{word1}', '{word2}'")
                return 0.0
            return float(self.model.similarity(w1, w2))
        except Exception:
            logger.exception(f"Error calculating similarity between '{word1}' and '{word2}'")
            return 0.0

    def get_vector(self, word: str) -> np.ndarray:
        """
        Retrieve the vector representation of a word.
        Returns None if the word is not found in the FastText vocabulary.
        """
        try:
            w = word.lower()
            if w not in self.model:
                logger.warning(f"No vector found for word: {word}")
                return None
            return self.model[w]
        except Exception:
            logger.exception(f"Error getting vector for word: {word}")
            return None

    def get_most_similar_words(self, target_word: str, n: int = 100) -> List[Dict[str, float]]:
        """
        Return the `n` most similar words to `target_word`.
        An empty list is returned if `target_word` is out of vocabulary.
        """
        try:
            w = target_word.lower()
            if w not in self.model:
                logger.warning(f"Target word not found in vocab: {target_word}")
                return []
            similar = self.model.most_similar(w, topn=n)
            return [{'word': word, 'similarity': float(sim)} for word, sim in similar]
        except Exception:
            logger.exception(f"Error finding similar words for: {target_word}")
            return []

    def get_words_in_range(self, target_word: str, min_similarity: float,
                          max_similarity: float, n: int = 5) -> List[Dict[str, float]]:
        """
        Retrieve up to `n` words whose similarity to `target_word` 
        lies within [min_similarity, max_similarity].
        The results are randomly sampled from all words meeting the criterion.
        """
        try:
            logger.info(f"Finding words for '{target_word}' in range "
                       f"[{min_similarity}, {max_similarity}]")
            target_vec = self.get_vector(target_word)
            if target_vec is None:
                logger.warning(f"No vector for target word: {target_word}")
                return []

            similarities = []
            norm_target = np.linalg.norm(target_vec)

            # Sample from vocabulary to improve performance
            sample_size = min(100000, len(self.vocab_vectors))
            sampled_words = random.sample(list(self.vocab_vectors.keys()), sample_size)

            for vocab_word in sampled_words:
                if vocab_word == target_word.lower():
                    continue
                
                vector = self.vocab_vectors[vocab_word]
                sim = float(np.dot(vector, target_vec) /
                          (np.linalg.norm(vector) * norm_target))
                
                if min_similarity <= sim <= max_similarity:
                    similarities.append({'word': vocab_word, 'similarity': sim})

            logger.info(f"Found {len(similarities)} words in the range.")
            if not similarities:
                return []

            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            selected_words = random.sample(similarities, min(n, len(similarities)))
            
            for w in selected_words:
                logger.debug(f"Selected: {w['word']} (sim={w['similarity']:.3f})")
            return selected_words

        except Exception:
            logger.exception(f"Error finding words in range for: {target_word}")
            return []

    def get_center_word(self, chosen_words: List[str], target_word: str) -> Dict[str, float]:
        """
        Compute the centroid of (chosen_words + target_word) vectors, 
        then find the single word in the vocabulary whose vector is closest 
        to that centroid (in cosine similarity).
        """
        if not chosen_words:
            logger.warning("No chosen words provided.")
            return {}

        vectors = []
        for w in chosen_words:
            vec = self.get_vector(w)
            if vec is not None:
                vectors.append(vec)

        target_vec = self.get_vector(target_word)
        if target_vec is not None:
            vectors.append(target_vec)

        if not vectors:
            logger.warning("No valid vectors found among chosen or target words.")
            return {}

        centroid = np.mean(vectors, axis=0)
        best_word = None
        best_similarity = -1.0

        # Sample from vocabulary to improve performance
        sample_size = min(100000, len(self.vocab_vectors))
        sampled_words = random.sample(list(self.vocab_vectors.keys()), sample_size)

        for vocab_word in sampled_words:
            if vocab_word == target_word.lower() or vocab_word in [cw.lower() for cw in chosen_words]:
                continue

            vector = self.vocab_vectors[vocab_word]
            sim = float(np.dot(vector, centroid) / 
                       (np.linalg.norm(vector) * np.linalg.norm(centroid)))
            
            if sim > best_similarity:
                best_similarity = sim
                best_word = vocab_word

        if best_word is None:
            logger.warning("Could not find a center word.")
            return {}

        return {"word": best_word, "similarity": best_similarity}