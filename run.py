from app import app
from flask import Flask, render_template, jsonify, request
from simulation.game import Game
from agents.registry import list_agents, get_agent
from agents.td_learning_agent import TDLearningAgent
import threading
import time
import psutil
import wandb
import os
import numpy as np
from dotenv import load_dotenv
from simulation.simulation_worker import run_simulation_worker, simulation_status, simulation_thread
from simulation.training_td_worker import train_td_worker, training_status, training_thread

load_dotenv()
# Ensure WANDB_API_KEY is set as an environment variable
wandb.login(key=os.getenv("WANDB_API_KEY"))

game_instance = Game()

@app.route('/')
def index():
    game_instance.reset_grid()
    return render_template('index.html', grid=game_instance.grid, score=game_instance.score, move=game_instance.last_move, agents=list_agents(), current_agent=game_instance.agent_class.__name__)

@app.route('/update', methods=['GET', 'POST'])
def update():
    move, moved, game_over, score = game_instance.simulate_move()
    # Check if there was an error (move will be None)
    if move is None:
        # The error message is already set in game_instance.last_move
        return jsonify(
            move=game_instance.last_move, 
            grid=game_instance.grid, 
            score=game_instance.score, 
            game_over=game_over,
            error=True
        )
    return jsonify(
        move=game_instance.last_move, 
        grid=game_instance.grid, 
        score=game_instance.score, 
        game_over=game_over
    )

@app.route('/restart', methods=['GET', 'POST'])
def restart():
    game_instance.reset_grid()
    return jsonify(grid=game_instance.grid, score=game_instance.score, game_over=False)

@app.route('/set_agent', methods=['POST'])
def set_agent():
    data = request.get_json()
    agent_name = data.get('agent_name')
    if game_instance.set_agent(agent_name):
        game_instance.reset_grid()
        return jsonify(status="ok", agent=agent_name, grid=game_instance.grid, score=game_instance.score)
    else:
        return jsonify(status="error", message="Unknown agent"), 400

@app.route('/agents')
def agents():
    return jsonify(agents=list_agents())


@app.route('/run_simulation', methods=['POST'])
def run_simulation_endpoint():
    global simulation_thread, simulation_status
    if simulation_status["running"]:
        return jsonify(status="error", message="Simulation already running."), 400

    data = request.get_json()
    agent_name = data.get('agent_name')
    num_games = data.get('num_games', 10)
    wandb_project = data.get('wandb_project') or os.getenv("WANDB_PROJECT")
    wandb_entity = data.get('wandb_entity') or os.getenv("WANDB_ENTITY")

    # Get algorithm-specific parameters
    agent_params = {}
    
    # A* and IDA* parameters
    if agent_name in ['a_star', 'ida_star']:
        depth_limit = data.get('depth_limit')
        if depth_limit:
            agent_params['depth_limit'] = int(depth_limit)
    
    # MCTS parameters
    elif agent_name == 'mcts':
        iterations = data.get('iterations')
        rollout_depth = data.get('rollout_depth')
        if iterations:
            agent_params['iterations'] = int(iterations)
        if rollout_depth:
            agent_params['rollout_depth'] = int(rollout_depth)
    
    # Expectimax parameters
    elif agent_name == 'expectimax':
        depth = data.get('depth')
        if depth:
            agent_params['search_depth'] = int(depth)
    
    # TD Learning parameters
    elif agent_name == 'td_learning':
        learning_rate = data.get('learning_rate')
        discount_factor = data.get('discount_factor')
        epsilon = data.get('epsilon')
        if learning_rate:
            agent_params['learning_rate'] = float(learning_rate)
        if discount_factor:
            agent_params['discount_factor'] = float(discount_factor)
        if epsilon:
            agent_params['epsilon'] = float(epsilon)

    if not agent_name or agent_name not in list_agents():
        return jsonify(status="error", message="Invalid agent name provided."), 400
    try:
        num_games = int(num_games)
        if num_games <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify(status="error", message="Invalid number of games provided."), 400

    # Pass the agent parameters to the simulation worker
    simulation_thread = threading.Thread(
        target=run_simulation_worker, 
        args=(agent_name, num_games, wandb_project, wandb_entity),
        kwargs={'agent_params': agent_params}
    )
    simulation_thread.start()

    return jsonify(status="ok", message="Simulation started.")

@app.route('/simulation_status')
def get_simulation_status():
    return jsonify(simulation_status)

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    global simulation_status, simulation_thread
    
    if not simulation_status["running"]:
        return jsonify(status="error", message="No simulation is currently running."), 400
    
    try:
        # Set a flag that will be checked by the simulation worker
        simulation_status["terminated"] = True
        # Note: this doesn't immediately stop the simulation thread, but the worker will check this flag
        return jsonify(status="ok", message="Simulation termination requested.")
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

# --- TD Training Route --- #

@app.route('/train_td_agent', methods=['POST'])
def train_td_agent_endpoint():
    global training_thread, training_status
    if training_status["running"]:
        return jsonify(status="error", message="TD Training already running."), 400
    if simulation_status["running"]:
         return jsonify(status="error", message="Simulation is running. Cannot start training."), 400

    data = request.get_json()
    try:
        num_episodes = int(data.get('num_episodes', 1000))
        save_interval = int(data.get('save_interval', 100))
        if num_episodes <= 0 or save_interval <= 0:
             raise ValueError()
    except (TypeError, ValueError):
        return jsonify(status="error", message="Invalid number of episodes or save interval."), 400

    training_thread = threading.Thread(target=train_td_worker, args=(num_episodes, save_interval))
    training_thread.start()

    return jsonify(status="ok", message=f"TD Training started for {num_episodes} episodes.")

@app.route('/training_status')
def get_training_status():
    # Returns the current status of the background TD training.
    return jsonify(training_status)

if __name__ == '__main__':
    list_agents()
    app.run(debug=True, host='0.0.0.0', port=5001)