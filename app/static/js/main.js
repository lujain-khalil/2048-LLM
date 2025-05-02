// Import the grid update function
import { updateGrid } from './grid.js';

// Import game control functions
import { 
    startGame, 
    pauseGame, 
    resumeGame, 
    restartGame, 
    changeSpeed, 
    changeAgent 
} from './controls.js';

// Algorithm explanations
const algorithmExplanations = {
    'random': `
        <strong>Random Agent</strong>: The simplest approach that randomly selects a move (UP, DOWN, LEFT, RIGHT) 
        at each step. Serves as a baseline for comparing more complex algorithms.
    `,
    'greedy_bfs': `
        <strong>Greedy Best-First Search</strong>: Looks ahead one move and selects the option that yields
        the best immediate outcome based on a heuristic function. It's fast but lacks long-term planning.
    `,
    'a_star': `
        <strong>A* Search</strong>: A path-finding algorithm that evaluates moves using a combination of
        current position quality and estimated future value. It explores multiple moves ahead but is limited
        by a depth limit to avoid excessive computation.
    `,
    'ida_star': `
        <strong>Iterative Deepening A*</strong>: An enhancement of A* that manages memory better by incrementally
        increasing the search depth. It combines depth-first and breadth-first properties, finding optimal
        paths within each increasing depth limit.
    `,
    'expectimax': `
        <strong>Expectimax</strong>: A decision algorithm designed for chance-based games. It evaluates moves by
        considering both player decisions and the random tile placements. Creates a game tree with "expectation"
        nodes to model randomness.
    `,
    'mcts': `
        <strong>Monte Carlo Tree Search</strong>: Builds a search tree through repeated random simulations (rollouts).
        It balances exploration of new moves and exploitation of promising strategies using the UCB1 selection
        formula, making it particularly effective for games with large state spaces.
    `,
    'td_learning': `
        <strong>Temporal Difference Learning</strong>: A reinforcement learning approach that learns a value function
        through gameplay experience. It updates its understanding of board positions by comparing consecutive states,
        gradually improving its evaluation function through self-play.
    `,
    'loop': `
        <strong>Loop Agent</strong>: A simple deterministic agent that follows a fixed pattern of moves 
        (typically cycling through UP, RIGHT, DOWN, LEFT). It's predictable but can sometimes achieve 
        decent scores through consistent merging patterns.
    `
};

// Track simulation status
let simulationRunning = false;
let simulationStatusInterval = null;

// Main entry point for the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the grid with data from server
    if (window.initialGrid) {
        updateGrid(window.initialGrid);
    } else {
        console.error("Initial grid data not available");
    }

    // Initialize score and move display
    if (window.initialScore) {
        document.getElementById('score-container').textContent = window.initialScore;
    }
    if (window.initialMove) {
        document.getElementById('last-move-container').textContent = window.initialMove;
    }

    // Set up game controls
    const pauseBtn = document.getElementById('pause-btn');
    const resumeBtn = document.getElementById('resume-btn');
    const restartBtn = document.getElementById('restart-btn');
    const speedSelect = document.getElementById('speed-select');
    const agentSelect = document.getElementById('agent-select');

    pauseBtn.addEventListener('click', pauseGame);
    resumeBtn.addEventListener('click', resumeGame);
    restartBtn.addEventListener('click', restartGame);
    speedSelect.addEventListener('change', function() {
        changeSpeed(this.value);
    });
    agentSelect.addEventListener('change', function() {
        changeAgent(this.value);
    });

    // Start the game immediately
    startGame();

    // Set up simulation controls
    const agentSelectSim = document.getElementById('agent-select-sim');
    const runSimulationBtn = document.getElementById('run-simulation-btn');
    const stopSimulationBtn = document.getElementById('stop-simulation-btn');
    const numGamesInput = document.getElementById('num-games');
    const algorithmExplanationDiv = document.getElementById('algorithm-explanation');

    // Display initial algorithm explanation
    updateAlgorithmExplanation(agentSelectSim.value);

    // Add event listeners for algorithm parameter visibility and explanations
    agentSelectSim.addEventListener('change', function() {
        showAlgorithmParams(this.value);
        updateAlgorithmExplanation(this.value);
    });

    runSimulationBtn.addEventListener('click', function() {
        runSimulation();
    });

    stopSimulationBtn.addEventListener('click', function() {
        stopSimulation();
    });

    // Show initial algorithm params based on default selection
    showAlgorithmParams(agentSelectSim.value);
});

// Function to update algorithm explanation
function updateAlgorithmExplanation(algorithm) {
    const explanationDiv = document.getElementById('algorithm-explanation');
    explanationDiv.innerHTML = algorithmExplanations[algorithm] || 
        '<p>No explanation available for this algorithm.</p>';
}

// Handle showing/hiding algorithm-specific parameter inputs
function showAlgorithmParams(algorithm) {
    // Hide all param sections first
    const paramSections = document.querySelectorAll('.algo-params');
    paramSections.forEach(section => {
        section.style.display = 'none';
    });

    // Show specific parameters based on selected algorithm
    if (algorithm === 'a_star' || algorithm === 'ida_star') {
        document.getElementById('a_star-params').style.display = 'block';
    } else if (algorithm === 'expectimax') {
        document.getElementById('expectimax-params').style.display = 'block';
    } else if (algorithm === 'mcts') {
        document.getElementById('mcts-params').style.display = 'block';
    } else if (algorithm === 'td_learning') {
        document.getElementById('td_learning-params').style.display = 'block';
    }
}

// Function to run simulations with the selected agent
function runSimulation() {
    const agentName = document.getElementById('agent-select-sim').value;
    const numGames = document.getElementById('num-games').value;
    
    // Collect algorithm-specific parameters
    let params = {
        agent_name: agentName,
        num_games: numGames
    };
    
    // Add specific parameters based on the algorithm
    if (agentName === 'a_star' || agentName === 'ida_star') {
        params.depth_limit = document.getElementById('depth-limit').value;
    } else if (agentName === 'expectimax') {
        params.depth = document.getElementById('depth').value;
    } else if (agentName === 'mcts') {
        params.iterations = document.getElementById('iterations').value;
        params.rollout_depth = document.getElementById('rollout-depth').value;
    } else if (agentName === 'td_learning') {
        params.learning_rate = document.getElementById('learning-rate').value;
        params.discount_factor = document.getElementById('discount-factor').value;
        params.epsilon = document.getElementById('epsilon').value;
    }
    
    // Update status
    const statusDisplay = document.getElementById('simulation-status-display');
    statusDisplay.textContent = 'Running simulation...';
    
    // Update button states
    document.getElementById('run-simulation-btn').disabled = true;
    document.getElementById('stop-simulation-btn').disabled = false;
    simulationRunning = true;
    
    // Send simulation request
    fetch('/run_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            // Start checking for updates
            checkSimulationStatus();
        } else {
            statusDisplay.textContent = `Error: ${data.message}`;
            // Reset button states
            simulationRunning = false;
            document.getElementById('run-simulation-btn').disabled = false;
            document.getElementById('stop-simulation-btn').disabled = true;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        statusDisplay.textContent = 'Error starting simulation';
        // Reset button states
        simulationRunning = false;
        document.getElementById('run-simulation-btn').disabled = false;
        document.getElementById('stop-simulation-btn').disabled = true;
    });
}

// Function to stop a running simulation
function stopSimulation() {
    if (!simulationRunning) return;
    
    fetch('/stop_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const statusDisplay = document.getElementById('simulation-status-display');
        if (data.status === 'ok') {
            statusDisplay.textContent = 'Simulation stopped by user.';
        } else {
            statusDisplay.textContent = `Error stopping simulation: ${data.message}`;
        }
        
        // Reset button states
        simulationRunning = false;
        document.getElementById('run-simulation-btn').disabled = false;
        document.getElementById('stop-simulation-btn').disabled = true;
        
        // Clear status check interval
        if (simulationStatusInterval) {
            clearInterval(simulationStatusInterval);
            simulationStatusInterval = null;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('simulation-status-display').textContent = 'Error stopping simulation';
        
        // Reset button states
        simulationRunning = false;
        document.getElementById('run-simulation-btn').disabled = false;
        document.getElementById('stop-simulation-btn').disabled = true;
    });
}

// Function to periodically check simulation status
function checkSimulationStatus() {
    if (simulationStatusInterval) {
        clearInterval(simulationStatusInterval);
    }
    
    simulationStatusInterval = setInterval(() => {
        if (!simulationRunning) {
            clearInterval(simulationStatusInterval);
            return;
        }
        
        fetch('/simulation_status')
            .then(response => response.json())
            .then(data => {
                const statusDisplay = document.getElementById('simulation-status-display');
                const resultsDisplay = document.getElementById('simulation-results-display');
                
                if (data.running) {
                    statusDisplay.textContent = `Running: ${data.progress}/${data.total_games} games completed`;
                } else {
                    clearInterval(simulationStatusInterval);
                    simulationRunning = false;
                    document.getElementById('run-simulation-btn').disabled = false;
                    document.getElementById('stop-simulation-btn').disabled = true;
                    
                    if (data.error) {
                        statusDisplay.textContent = `Error: ${data.error}`;
                    } else if (data.results) {
                        statusDisplay.textContent = 'Completed';
                        resultsDisplay.textContent = JSON.stringify(data.results, null, 2);
                    } else {
                        statusDisplay.textContent = 'Completed with no results';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                clearInterval(simulationStatusInterval);
                simulationRunning = false;
                document.getElementById('run-simulation-btn').disabled = false;
                document.getElementById('stop-simulation-btn').disabled = true;
                document.getElementById('simulation-status-display').textContent = 'Error checking status';
            });
    }, 1000);
}