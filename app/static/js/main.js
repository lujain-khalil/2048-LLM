import { updateGrid } from './grid.js';
import { startGame, pauseGame, resumeGame, restartGame, changeSpeed, changeAgent} from './controls.js';

// Expose updateGrid globally if needed by controls.js or other scripts.
window.updateGrid = updateGrid;

// Render initial grid and set up event listeners once the page loads.
window.addEventListener("load", function() {
    if (window.initialGrid) {
        updateGrid(window.initialGrid, window.initialGrid, null);
    } else {
        console.error("Initial grid is not defined!");
    }
    startGame();
    
    // Simulation control buttons.
    document.getElementById("resume-btn").disabled = true;
    document.getElementById("pause-btn").addEventListener("click", pauseGame);
    document.getElementById("resume-btn").addEventListener("click", resumeGame);
    document.getElementById("restart-btn").addEventListener("click", restartGame);
    
    // Speed control dropdown.
    document.getElementById("speed-select").addEventListener("change", function() {
        changeSpeed(this.value);
    });

    // Agent control dropdown.
    document.getElementById("agent-select").addEventListener("change", function() {
        changeAgent(this.value);
    });
});