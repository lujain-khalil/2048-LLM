// Import the grid update function
import { updateGrid } from './grid.js';

// Game control state
let gameInterval;
let isPaused = false;

// Speed settings in milliseconds
const SPEEDS = {
    slow: 1200,
    normal: 500,
    fast: 100
};

// Current update speed
let updateDelay = SPEEDS.normal;

// Function to update the game state
export function updateGame() {
    fetch('/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update UI with new data
        document.getElementById('last-move-container').textContent = data.move || '';
        document.getElementById('score-container').textContent = data.score;
        
        // Update grid
        updateGrid(data.grid);
        
        // Check for game over
        if (data.game_over) {
            pauseGame();
            document.getElementById('game-over-message').style.display = 'block';
        }
    })
    .catch(error => console.error('Error updating game:', error));
}

// Start the game with automatic moves
export function startGame() {
    gameInterval = setInterval(updateGame, updateDelay);
    isPaused = false;
    document.getElementById('pause-btn').disabled = false;
    document.getElementById('resume-btn').disabled = true;
}

// Pause the game
export function pauseGame() {
    clearInterval(gameInterval);
    isPaused = true;
    document.getElementById('pause-btn').disabled = true;
    document.getElementById('resume-btn').disabled = false;
}

// Resume the game
export function resumeGame() {
    gameInterval = setInterval(updateGame, updateDelay);
    isPaused = false;
    document.getElementById('pause-btn').disabled = false;
    document.getElementById('resume-btn').disabled = true;
}

// Restart the game
export function restartGame() {
    // Clear game over message if visible
    document.getElementById('game-over-message').style.display = 'none';
    
    // Request restart from server
    fetch('/restart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update UI with new game state
        document.getElementById('score-container').textContent = data.score;
        document.getElementById('last-move-container').textContent = '';
        updateGrid(data.grid);
        
        // Restart the game interval if it was paused
        if (isPaused) {
            resumeGame();
        }
    })
    .catch(error => console.error('Error restarting game:', error));
}

// Change the game speed
export function changeSpeed(speed) {
    updateDelay = SPEEDS[speed] || SPEEDS.normal;
    
    // Restart interval with new speed if game is running
    if (!isPaused) {
        clearInterval(gameInterval);
        gameInterval = setInterval(updateGame, updateDelay);
    }
}

// Change the AI agent
export function changeAgent(agentName) {
    fetch('/set_agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ agent_name: agentName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            // Update grid and score
            document.getElementById('score-container').textContent = data.score;
            document.getElementById('last-move-container').textContent = '';
            updateGrid(data.grid);
            
            // Clear game over message if shown
            document.getElementById('game-over-message').style.display = 'none';
            
            // Restart the game if paused
            if (isPaused) {
                resumeGame();
            }
        } else {
            console.error('Error changing agent:', data.message);
        }
    })
    .catch(error => console.error('Error changing agent:', error));
}