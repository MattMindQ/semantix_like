// file location: src/main.ts

import { checkWord, getGameState, getVisualizationData, resetGame, useJoker, getCenterWord } from './services/api';
import { CenterWordResponse, GameResponse, GameState, JokerResponse } from './types';
import { create3DVisualization } from './utils/visualization';
import * as UI from './utils/ui-updates';
import { initializeWordFilters } from './utils/word-list-updates';

let gameState: GameState;
let isSelectingCenterWords = false;
let selectedWordsForCenter: string[] = [];

// Initialize Elements
const form = document.getElementById('guessForm') as HTMLFormElement;
const input = document.getElementById('wordInput') as HTMLInputElement;
const result = document.getElementById('result') as HTMLDivElement;
const targetWordDisplay = document.getElementById('targetWord') as HTMLElement;
const visualizationSection = document.getElementById('visualizationSection') as HTMLDivElement;
const gameplaySection = document.getElementById('gameplaySection') as HTMLDivElement;
const similarWordsSection = document.getElementById('similarWordsSection') as HTMLDivElement;

// Initialize Buttons
const resetButton = document.getElementById('resetButton') as HTMLButtonElement;
const toggleVisualizationBtn = document.getElementById('toggleVisualization') as HTMLButtonElement;
const closeVisualizationBtn = document.getElementById('closeVisualization') as HTMLButtonElement;
const highSimilarityJokerBtn = document.getElementById('highSimilarityJoker') as HTMLButtonElement;
const mediumSimilarityJokerBtn = document.getElementById('mediumSimilarityJoker') as HTMLButtonElement;

// The new button for the center-word power:
const centerWordPowerBtn = document.getElementById('centerWordPowerBtn') as HTMLButtonElement;
centerWordPowerBtn.addEventListener('click', () => {
    // Toggle selection mode
    isSelectingCenterWords = !isSelectingCenterWords;
    selectedWordsForCenter = [];

    if (isSelectingCenterWords) {
        centerWordPowerBtn.textContent = 'Choisissez 3 mots';
        centerWordPowerBtn.classList.add('bg-pink-700');
    } else {
        centerWordPowerBtn.textContent = 'Joker Triangulation';
        centerWordPowerBtn.classList.remove('bg-pink-700');
    }
});

// Listen for clicks on guessed words via event delegation
const guessedWordsList = document.getElementById('guessedWordsList');
if (guessedWordsList) {
    guessedWordsList.addEventListener('click', async (e) => {
        if (!isSelectingCenterWords) return;

        const target = e.target as HTMLElement;
        // The user might click a child node; find the parent with the guessed-word-item class
        const item = target.closest('.guessed-word-item') as HTMLDivElement | null;
        if (!item) return; 

        const word = item.dataset['word']; 
        if (!word) return;
        
        // Toggle highlight and selection
        if (selectedWordsForCenter.includes(word)) {
            // Already selected, remove it
            selectedWordsForCenter = selectedWordsForCenter.filter(w => w !== word);
            item.classList.remove('ring-2', 'ring-pink-500');
        } else if (selectedWordsForCenter.length < 3) {
            // Add selection
            selectedWordsForCenter.push(word);
            item.classList.add('ring-2', 'ring-pink-500');
        }

        // Once we have 3 words, call the backend
        if (selectedWordsForCenter.length === 3) {
            try {
                // Exit selection mode
                isSelectingCenterWords = false;
                centerWordPowerBtn.textContent = 'Joker Triangulation';
                centerWordPowerBtn.classList.remove('bg-pink-700');

                const centerResult: CenterWordResponse = await getCenterWord(selectedWordsForCenter);
                console.log('Center word response:', centerResult);

                // Remove highlights
                const selectedItems = guessedWordsList.querySelectorAll('.ring-2.ring-pink-500');
                selectedItems.forEach(el => el.classList.remove('ring-2', 'ring-pink-500'));

                // Insert the new word into attempts
                gameState.attempts.push({
                    word: centerResult.word,
                    similarity: centerResult.similarity
                });

                // Optionally, you could also call checkWord(centerResult.word) if you want the server
                // to confirm similarity to the target. But here we just manually add it to attempts.

                // Update the UI
                UI.updateGameDisplay(gameState);
            } catch (err) {
                console.error('Error fetching center word:', err);
            } finally {
                // Reset selection
                selectedWordsForCenter = [];
            }
        }
    });
}

async function initGame() {
    try {
        const state = await getGameState();
        gameState = state;
        UI.updateGameDisplay(gameState);
        await updateVisualization();
        if (targetWordDisplay) {
            targetWordDisplay.textContent = gameState.targetWord;
        }
        if (similarWordsSection) {
            similarWordsSection.classList.add('hidden');
        }
        UI.updateJokerCounts(gameState.jokers);
        initializeWordFilters();
    } catch (error) {
        console.error('Error initializing game:', error);
    }
}

async function handleReset() {
    try {
        const newState = await resetGame();
        gameState = newState;
        
        // Reset UI
        input.value = '';
        result.classList.add('hidden');
        targetWordDisplay.textContent = gameState.targetWord;
        similarWordsSection?.classList.add('hidden');
        
        // Hide joker words sections
        document.querySelectorAll('.joker-words').forEach(el => el.classList.add('hidden'));
        
        UI.updateGameDisplay(gameState);
        await updateVisualization();
        UI.updateJokerCounts(gameState.jokers);
        
    } catch (error) {
        console.error('Error resetting game:', error);
    }
}

async function updateVisualization() {
    try {
        const vizData = await getVisualizationData();
        if (vizData) {
            create3DVisualization(vizData, 'visualization');
        }
    } catch (error) {
        console.error('Error updating visualization:', error);
    }
}

async function handleJokerUse(type: 'high_similarity' | 'medium_similarity') {
    try {
        console.log(`Using joker of type: ${type}`);
        const response: JokerResponse = await useJoker(type);
        console.log('Joker response:', response);
        
        if (response.joker_words && response.joker_words.length > 0) {
            gameState.jokers = response.jokers;
            UI.updateJokerCounts(gameState.jokers);
            UI.showJokerWords(response.joker_words, type);
        } else {
            console.warn('No joker words received');
        }
    } catch (error) {
        console.error('Error using joker:', error);
    }
}

// Handle guess submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const guess = input.value.trim().toLowerCase();
    if (!guess) return;

    try {
        const response: GameResponse = await checkWord(guess);
        gameState.attempts = response.history;
        gameState.word_found = response.word_found;
        
        UI.showResult(response.similarity);
        UI.updateGameDisplay(gameState);
        await updateVisualization();
        
        if (response.word_found && response.similar_words) {
            gameState.similar_words = response.similar_words;
            UI.showSimilarWords(response.similar_words);
        }
        
        input.value = '';
    } catch (error) {
        console.error('Error checking word:', error);
    }
});

// Hook up event listeners
resetButton.addEventListener('click', handleReset);
toggleVisualizationBtn.addEventListener('click', () => {
    visualizationSection?.classList.remove('hidden');
    gameplaySection?.classList.add('hidden');
});
closeVisualizationBtn.addEventListener('click', () => {
    visualizationSection?.classList.add('hidden');
    gameplaySection?.classList.remove('hidden');
});
highSimilarityJokerBtn.addEventListener('click', () => handleJokerUse('high_similarity'));
mediumSimilarityJokerBtn.addEventListener('click', () => handleJokerUse('medium_similarity'));

// Start the game on load
initGame();
