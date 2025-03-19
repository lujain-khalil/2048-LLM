import { updateGrid } from './grid.js';
import { startGame, pauseGame, resumeGame, restartGame, changeSpeed, changeAgent} from './controls.js';

// Expose updateGrid globally if needed by controls.js or other scripts.
window.updateGrid = updateGrid;

// Render initial grid and set up event listeners once the page loads.
window.addEventListener("load", function() {
    if (window.initialGrid) {
        updateGrid(window.initialGrid);
    } else {
        console.error("Initial grid is not defined!");
    }
    startGame();
    
    // Simulation control buttons.
    document.getElementById("resume-btn").disabled = true;
    document.getElementById("pause-btn").addEventListener("click", pauseGame);
    document.getElementById("resume-btn").addEventListener("click", resumeGame);
    document.getElementById("restart-btn").addEventListener("click", restartGame);
    
    // Speed control buttons.
    document.getElementById("normal-btn").disabled = true;
    document.getElementById("slow-btn").addEventListener("click", () => changeSpeed("slow-btn"));
    document.getElementById("normal-btn").addEventListener("click", () => changeSpeed("normal-btn"));
    document.getElementById("fast-btn").addEventListener("click", () => changeSpeed("fast-btn"));
    
    // Agent control buttons
    document.getElementById("random-agent-btn").disabled = true;
    document.getElementById("random-agent-btn").addEventListener("click", () => changeAgent("random"));
    document.getElementById("loop-agent-btn").addEventListener("click", () => changeAgent("loop"));
});