let gameInterval;
let isPaused = false;

let fastSpeed = 200
let normalSpeed = 800
let slowSpeed = 1200

let updateDelay = normalSpeed;

// Fetching the next move
export function updateGame() {
    fetch('/update')
        .then(response => response.json())
        .then(data => {
            document.getElementById("move").innerText = data.move;
            window.updateGrid(data.grid);
        })
        .catch(error => console.error('Error:', error));
}

export function startGame() {
    gameInterval = setInterval(updateGame, updateDelay);
}

// Simulation control buttons
export function pauseGame() {
    if (!isPaused) {
        clearInterval(gameInterval);
        isPaused = true;
        document.getElementById("pause-btn").disabled = true;
        document.getElementById("resume-btn").disabled = false;
    }
}

export function resumeGame() {
    if (isPaused) {
        startGame();
        isPaused = false;
        document.getElementById("pause-btn").disabled = false;
        document.getElementById("resume-btn").disabled = true;
    }
}

export function restartGame() {
    fetch('/restart')
        .then(response => response.json())
        .then(data => {
            window.updateGrid(data.grid);
            document.getElementById("move").innerText = "";
        })
        .catch(error => console.error('Error:', error));
}

// Speed control buttons
export function changeSpeed(speedValue) {
    if (speedValue === "slow") {
        updateDelay = slowSpeed;
    } else if (speedValue === "fast") {
        updateDelay = fastSpeed;
    } else {
        updateDelay = normalSpeed;
    }

    if (!isPaused) {
        clearInterval(gameInterval);
        startGame();
    }
}

// Agent control buttons
export function changeAgent(activeAgent) {
    fetch(`/set_agent/${activeAgent}`)
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
}