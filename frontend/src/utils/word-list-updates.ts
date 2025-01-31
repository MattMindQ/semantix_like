// file location: src/utils/word-list-updates.ts

import { GameState } from '../types';

interface WordEntry {
    word: string;
    similarity: number;
    type: 'guess' | 'high_joker' | 'medium_joker';
}

export function updateWordList(gameState: GameState) {
    const wordList = document.getElementById('wordList');
    const guessCount = document.getElementById('guessCount');
    if (!wordList || !guessCount) return;

    // Update guess count
    guessCount.textContent = `${gameState.attempts.length} mot${gameState.attempts.length > 1 ? 's' : ''}`;

    // Update guessed words list
    const guessedWordsList = document.getElementById('guessedWordsList');
    if (guessedWordsList) {
        const sortedAttempts = [...gameState.attempts].sort((a, b) => b.similarity - a.similarity);
        
        // Each guessed word div now has .guessed-word-item and data-word for click handling
        guessedWordsList.innerHTML = sortedAttempts.map(attempt => `
            <div class="guessed-word-item flex justify-between items-center p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
                 data-word="${attempt.word}">
                <span class="font-medium">${attempt.word}</span>
                <span class="${getScoreColorClass(attempt.similarity)}">${(attempt.similarity * 100).toFixed(1)}%</span>
            </div>
        `).join('');
    }
}

export function showJokerWords(words: Array<{word: string; similarity: number}>, type: 'high_similarity' | 'medium_similarity') {
    console.log(`Showing joker words for ${type}:`, words); // Debug log
    
    // Update container class selection
    const containerClass = type === 'high_similarity' ? 'high-similarity' : 'medium-similarity';
    const container = document.querySelector(`.joker-words.${containerClass}`);
    
    if (!container) {
        console.error(`Container not found for ${type}`);
        return;
    }

    // Show the container
    container.classList.remove('hidden');

    // Update words with fixed Tailwind classes
    const wordsContainer = container.querySelector('.bg-amber-50, .bg-orange-50');
    if (wordsContainer) {
        const bgClass = type === 'high_similarity' ? 'bg-amber-50' : 'bg-orange-50';
        const hoverClass = type === 'high_similarity' ? 'hover:bg-amber-100' : 'hover:bg-orange-100';
        
        wordsContainer.innerHTML = words.map(item => `
            <div class="flex justify-between items-center p-2 rounded-lg ${bgClass} ${hoverClass} transition-colors">
                <span class="font-medium">${item.word}</span>
                <span class="${getScoreColorClass(item.similarity)}">${(item.similarity * 100).toFixed(1)}%</span>
            </div>
        `).join('');
    } else {
        console.error('Words container not found');
    }
}

function getScoreColorClass(similarity: number): string {
    const baseClasses = "font-bold";
    if (similarity >= 0.7) return `${baseClasses} text-emerald-600`;
    if (similarity >= 0.5) return `${baseClasses} text-amber-600`;
    return `${baseClasses} text-red-600`;
}

export function initializeWordFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const target = e.currentTarget as HTMLButtonElement;
            const filter = target.dataset.filter;

            // Update button styles
            filterButtons.forEach(btn => {
                btn.classList.remove('bg-indigo-100', 'text-indigo-700');
                btn.classList.add('bg-slate-100', 'text-slate-700');
            });
            target.classList.remove('bg-slate-100', 'text-slate-700');
            target.classList.add('bg-indigo-100', 'text-indigo-700');

            // Apply filter
            const guessedWords = document.querySelector('.guessed-words');
            const jokerWords = document.getElementById('jokerWordsContainer');

            if (filter === 'all') {
                guessedWords?.classList.remove('hidden');
                jokerWords?.classList.remove('hidden');
            } else if (filter === 'guesses') {
                guessedWords?.classList.remove('hidden');
                jokerWords?.classList.add('hidden');
            } else if (filter === 'hints') {
                guessedWords?.classList.add('hidden');
                jokerWords?.classList.remove('hidden');
            }
        });
    });
}
