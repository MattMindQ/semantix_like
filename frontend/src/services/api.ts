// frontend/src/services/api.ts
const API_URL = 'http://localhost:5000/api';

export async function checkWord(guessWord: string) {
    const response = await fetch(`${API_URL}/check-word`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            word: guessWord  // Changed from guess_word to word to match backend
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Network response was not ok');
    }

    return response.json();
}

export async function getGameState() {
    const response = await fetch(`${API_URL}/game-state`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
}

export async function getVisualizationData() {
    const response = await fetch(`${API_URL}/visualization`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
}

export async function resetGame() {
    const response = await fetch(`${API_URL}/reset-game`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return response.json();
}


export async function getCenterWord(chosenWords: string[]): Promise<{word: string; similarity: number}> {
    const response = await fetch(`${API_URL}/get-center-word`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chosen_words: chosenWords })
    });

    if (!response.ok) {
        // Could be a 400 if center word not found or some other error
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Error fetching center word');
    }

    return response.json();
}

export async function useJoker(jokerType: 'high_similarity' | 'medium_similarity') {
    console.log(`Sending joker request for type: ${jokerType}`); // Debug log
    
    const response = await fetch(`${API_URL}/use-joker`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            joker_type: jokerType
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Network response was not ok');
    }

    const data = await response.json();
    console.log('Joker response data:', data); // Debug log
    return data;
}