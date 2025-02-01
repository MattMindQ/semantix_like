// src/utils/ui-updates.ts
import { GameState } from '../types';
import { updateWordList, showJokerWords as showJokerWordsInList } from './word-list-updates';

// src/utils/ui-updates.ts
export function updateStats(gameState: GameState) {
    if (!gameState || !gameState.attempts) {
        console.warn('Invalid game state or missing attempts');
        return;
    }

    const attempts = gameState.attempts;
    const attemptCount = document.getElementById('attemptCount');
    const bestScore = document.getElementById('bestScore');
    const averageScore = document.getElementById('averageScore');
    
    if (!attemptCount || !bestScore || !averageScore) {
        console.warn('Required DOM elements not found');
        return;
    }

    const count = attempts.length;
    attemptCount.textContent = count.toString();
    
    if (count === 0) {
        bestScore.textContent = '0%';
        averageScore.textContent = '0%';
        return;
    }

    const scores = attempts.map(a => a.similarity);
    const maxScore = Math.max(...scores);
    const avgScore = scores.reduce((a, b) => a + b) / count;
    
    bestScore.textContent = `${(maxScore * 100).toFixed(1)}%`;
    averageScore.textContent = `${(avgScore * 100).toFixed(1)}%`;
}

export function updateJokerCounts(jokers: GameState['jokers']) {
    const highCount = document.getElementById('highSimilarityCount');
    const mediumCount = document.getElementById('mediumSimilarityCount');
    const highButton = document.getElementById('highSimilarityJoker');
    const mediumButton = document.getElementById('mediumSimilarityJoker');
    
    if (highCount) {
        highCount.textContent = jokers.high_similarity.remaining.toString();
        highButton?.toggleAttribute('disabled', jokers.high_similarity.remaining <= 0);
    }
    if (mediumCount) {
        mediumCount.textContent = jokers.medium_similarity.remaining.toString();
        mediumButton?.toggleAttribute('disabled', jokers.medium_similarity.remaining <= 0);
    }
}

export function showResult(similarity: number) {
    const result = document.getElementById('result');
    const similarityScore = document.getElementById('similarityScore');
    const similarityBar = document.getElementById('similarityBar');
    
    if (!result || !similarityScore || !similarityBar) return;
    
    result.classList.remove('hidden');
    similarityScore.textContent = `${(similarity * 100).toFixed(1)}%`;
    similarityBar.style.width = `${similarity * 100}%`;
}

export function showSimilarWords(similarWords: Array<{word: string; similarity: number}>) {
    const section = document.getElementById('similarWordsSection');
    const list = document.getElementById('similarWordsList');
    if (!section || !list) return;

    section.classList.remove('hidden');
    list.innerHTML = similarWords.map(item => `
        <div class="p-3 border rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors">
            <div class="font-medium">${item.word}</div>
            <div class="text-sm text-slate-600">${(item.similarity * 100).toFixed(1)}%</div>
        </div>
    `).join('');
}

// src/utils/ui-updates.ts
export function showJokerWords(words: Array<{word: string; similarity: number}>, type: 'high_similarity' | 'medium_similarity') {
    console.log('Showing joker words:', words); // Debug log
    showJokerWordsInList(words, type);
}

// Remove updateGameDisplay since it's causing issues with gameState access
export function updateGameDisplay(gameState: GameState) {
    updateStats(gameState);
    updateWordList(gameState);
}