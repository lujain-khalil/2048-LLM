// controls.js

let gameInterval;
let isPaused = false;

let fastSpeed = 500
let normalSpeed = 1000
let slowSpeed = 1500

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
export function changeSpeed(activeBtnID) {
    if (activeBtnID == "slow-btn") {
        updateDelay = slowSpeed;
    } else if (activeBtnID == "fast-btn") {
        updateDelay = fastSpeed;
    } else {
        updateDelay = normalSpeed
    }
    
    if (!isPaused) {
        clearInterval(gameInterval);
        startGame();
    }
    updateSpeedButtons(activeBtnID);
}

export function updateSpeedButtons(activeBtnID) {
    const slowBtn = document.getElementById("slow-btn");
    const normalBtn = document.getElementById("normal-btn");
    const fastBtn = document.getElementById("fast-btn");

    slowBtn.disabled = (activeBtnID === "slow-btn");
    normalBtn.disabled = (activeBtnID === "normal-btn");
    fastBtn.disabled = (activeBtnID === "fast-btn");
}

// Agent control buttons
export function changeAgent(activeAgent) {

    fetch(`/set_agent/${activeAgent}`)
        .then(response => response.json())
        .then(data => updateAgentButtons(activeAgent))
        .catch(error => console.error('Error:', error));
}


function updateAgentButtons(activeAgent) {
    const randomBtn = document.getElementById("random-agent-btn");
    const loopBtn = document.getElementById("loop-agent-btn");

    randomBtn.disabled = (activeAgent === "random");
    loopBtn.disabled = (activeAgent === "loop");
}