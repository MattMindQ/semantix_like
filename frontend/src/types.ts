// src/types.ts
export interface GameState {
    targetWord: string;
    attempts: Array<{
        word: string;
        similarity: number;
    }>;
    word_found?: boolean;
    similar_words?: Array<{
        word: string;
        similarity: number;
    }>;
    jokers: {
        high_similarity: {
            remaining: number;
            words_per_use: number;
        };
        medium_similarity: {
            remaining: number;
            words_per_use: number;
        };
    };
}

export interface GameResponse {
    similarity: number;
    history: Array<{
        word: string;
        similarity: number;
    }>;
    word_found: boolean;
    similar_words: Array<{
        word: string;
        similarity: number;
    }>;
}

export interface JokerResponse {
    joker_words: Array<{
        word: string;
        similarity: number;
    }>;
    jokers: GameState['jokers'];
}

// file location: frontend/src/types.ts

export interface CenterWordResponse {
    word: string;
    similarity: number;
}

