// frontend/src/services/api.ts

// Get the base URL depending on the environment
const getBaseUrl = () => {
    if (import.meta.env.PROD) {
        // In production, use relative URLs
        return '/api';
    }
    // In development, use localhost
    return 'http://localhost:5000/api';
};

const API_URL = getBaseUrl();


export async function checkSystemHealth() {
    return apiCall('/system-health');
}
// Helper function for API calls
async function apiCall(endpoint: string, options?: RequestInit) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `API call failed: ${response.statusText}`);
        }

        return response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

export async function checkWord(guessWord: string) {
    return apiCall('/check-word', {
        method: 'POST',
        body: JSON.stringify({ word: guessWord })
    });
}

export async function getGameState() {
    return apiCall('/game-state');
}

export async function getVisualizationData() {
    return apiCall('/visualization');
}

export async function resetGame() {
    return apiCall('/reset-game', {
        method: 'POST'
    });
}

export async function getCenterWord(chosenWords: string[]): Promise<{word: string; similarity: number}> {
    return apiCall('/get-center-word', {
        method: 'POST',
        body: JSON.stringify({ chosen_words: chosenWords })
    });
}

export async function useJoker(jokerType: 'high_similarity' | 'medium_similarity') {
    console.log(`Sending joker request for type: ${jokerType}`);
    
    const response = await apiCall('/use-joker', {
        method: 'POST',
        body: JSON.stringify({ joker_type: jokerType })
    });
    
    console.log('Joker response data:', response);
    return response;
}