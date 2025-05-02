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
    return jsonify(move=game_instance.last_move, grid=game_instance.grid, score=game_instance.score, game_over=game_over)

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

simulation_status = {
    "running": False,
    "progress": 0,
    "total_games": 0,
    "results": None,
    "error": None,
    "terminated": False
}
simulation_thread = None

def run_simulation_worker(agent_name, num_games, wandb_project, wandb_entity, agent_params=None):
    global simulation_status
    run = None # Initialize wandb run object
    try:
        simulation_status["running"] = True
        simulation_status["progress"] = 0
        simulation_status["total_games"] = num_games
        simulation_status["results"] = None
        simulation_status["error"] = None
        simulation_status["terminated"] = False

        # Validate WandB entity if project is specified
        if wandb_project and not wandb_entity:
             # Attempt to get entity from environment variable
             wandb_entity = os.getenv("WANDB_ENTITY")
             if not wandb_entity:
                  print("Warning: WandB project specified but no entity provided or found in WANDB_ENTITY env var. Disabling WandB logging.")
                  wandb_project = None # Disable logging if entity missing

        # Initialize WandB run if project and entity are valid
        if wandb_project and wandb_entity:
            try:
                # Include agent parameters in WandB config
                config = {
                    "agent": agent_name,
                    "num_games": num_games,
                }
                if agent_params:
                    for key, value in agent_params.items():
                        config[key] = value
                
                run = wandb.init(
                            project=wandb_project,
                            entity=wandb_entity,
                            reinit="create_new",
                            config=config,
                            )
                print(f"WandB logging initialized for project '{wandb_project}', entity '{wandb_entity}'. Run: {run.name}")
            except Exception as e:
                print(f"Error initializing WandB: {e}. Disabling logging.")
                run = None # Ensure run is None if init fails
        else:
             print("WandB project or entity not provided. Skipping WandB logging.")

        sim_game = Game()
        if not sim_game.set_agent(agent_name):
             raise ValueError(f"Agent '{agent_name}' not found for simulation.")
        
        # Apply agent-specific parameters if provided
        if agent_params and hasattr(sim_game.agent, '__dict__'):
            for key, value in agent_params.items():
                if hasattr(sim_game.agent, key):
                    setattr(sim_game.agent, key, value)
                    print(f"Set agent parameter {key} = {value}")

        all_scores = []
        all_max_tiles = []
        win_count = 0
        all_moves = []
        all_decision_times = []
        all_game_times = []
        all_memory_usages = []  # Track memory usage across games
        peak_memory_usage = 0   # Track peak memory usage

        WIN_TILE = 2048

        process = psutil.Process(os.getpid())
        total_system_memory = psutil.virtual_memory().total

        for i in range(num_games):
            # Check for termination request
            if simulation_status["terminated"]:
                print(f"Simulation terminated after {i} games by user request.")
                break
                
            sim_game.reset_grid()
            start_time = time.perf_counter()
            start_cpu_time = process.cpu_times()
            start_memory = process.memory_info().rss

            game_over = False
            moves_count = 0
            decision_times_this_game = []
            memory_samples = []

            while not game_over:
                # Also check for termination during a game
                if simulation_status["terminated"]:
                    break
                    
                decision_start_time = time.perf_counter()
                _, moved, game_over, _ = sim_game.simulate_move()
                decision_end_time = time.perf_counter()
                decision_times_this_game.append(decision_end_time - decision_start_time)

                # Sample memory usage periodically during the game
                if moves_count % 10 == 0:
                    current_memory = process.memory_info().rss
                    memory_samples.append(current_memory)
                    peak_memory_usage = max(peak_memory_usage, current_memory)

                if moved:
                    moves_count += 1
                if moves_count > 5000:
                    print(f"Warning: Game {i+1} exceeded 5000 moves. Terminating.")
                    break

            # If terminated during the game, break the outer loop too
            if simulation_status["terminated"]:
                print(f"Simulation terminated during game {i+1} by user request.")
                break
                
            end_time = time.perf_counter()
            end_cpu_time = process.cpu_times()
            end_memory = process.memory_info().rss
            memory_samples.append(end_memory)
            peak_memory_usage = max(peak_memory_usage, end_memory)

            game_time = end_time - start_time
            cpu_time_used = (end_cpu_time.user - start_cpu_time.user) + (end_cpu_time.system - start_cpu_time.system)
            avg_mem_used = sum(memory_samples) / len(memory_samples) if memory_samples else end_memory
            mem_used_percent = (avg_mem_used / total_system_memory) * 100

            final_score = sim_game.score
            max_tile = sim_game.get_max_tile()
            is_win = max_tile >= WIN_TILE

            all_scores.append(final_score)
            all_max_tiles.append(max_tile)
            if is_win:
                win_count += 1
            all_moves.append(moves_count)
            all_decision_times.extend(decision_times_this_game)
            all_game_times.append(game_time)
            all_memory_usages.append(avg_mem_used)

            simulation_status["progress"] = i + 1

            # Log per-game results to WandB (only if run was initialized)
            if run:
                log_data = {
                    "game_index": i,
                    "final_score": final_score,
                    "max_tile": max_tile,
                    "moves": moves_count,
                    "win": is_win,
                    "game_time_s": game_time,
                    "cpu_time_s": cpu_time_used,
                    "avg_memory_bytes": avg_mem_used,
                    "avg_memory_mb": avg_mem_used / (1024 * 1024),
                    "memory_percent": mem_used_percent,
                    "avg_decision_time_s": sum(decision_times_this_game) / len(decision_times_this_game) if decision_times_this_game else 0
                }
                run.log(log_data)

        # Only calculate results if we have at least one completed game
        if all_scores:
            mean_score = sum(all_scores) / len(all_scores)
            max_score = max(all_scores)
            min_score = min(all_scores)
            score_variance = sum([(s - mean_score) ** 2 for s in all_scores]) / len(all_scores)
            win_rate = win_count / len(all_scores)
            mean_moves = sum(all_moves) / len(all_scores)
            mean_decision_time = sum(all_decision_times) / len(all_decision_times) if all_decision_times else 0
            mean_game_time = sum(all_game_times) / len(all_scores)
            mean_memory_usage = sum(all_memory_usages) / len(all_memory_usages) if all_memory_usages else 0
            peak_memory_mb = peak_memory_usage / (1024 * 1024)

            results = {
                "agent": agent_name,
                "num_games": len(all_scores),
                "mean_score": mean_score,
                "max_score": max_score,
                "min_score": min_score,
                "score_variance": score_variance,
                "mean_max_tile": sum(all_max_tiles) / len(all_scores),
                "max_max_tile": max(all_max_tiles),
                "win_rate": win_rate,
                "mean_moves_to_game_over": mean_moves,
                "mean_decision_time_s": mean_decision_time,
                "mean_game_time_s": mean_game_time,
                "mean_memory_usage_mb": mean_memory_usage / (1024 * 1024),
                "peak_memory_usage_mb": peak_memory_mb,
            }

            # If terminated early, note this in the results
            if simulation_status["terminated"]:
                results["terminated_early"] = True
                results["completed_games"] = len(all_scores)
                results["total_games"] = num_games
                
            simulation_status["results"] = results
            
            if run:
                try:
                    # Log final results to WandB
                    run.summary.update(results)
                    
                    # Upload agent parameters as a config table
                    if agent_params:
                        param_data = [[key, str(value)] for key, value in agent_params.items()]
                        run.log({"hyperparameters": wandb.Table(
                            columns=["Parameter", "Value"],
                            data=param_data
                        )})
                        
                    run.finish()
                except Exception as e:
                    print(f"Error updating WandB summary: {e}")
        else:
            # No games completed but terminated by user
            if simulation_status["terminated"]:
                simulation_status["results"] = {
                    "terminated_early": True,
                    "completed_games": 0,
                    "total_games": num_games
                }
            
    except Exception as e:
        print(f"Simulation failed: {e}")
        simulation_status["error"] = str(e)
        if run: run.finish(exit_code=1) # Mark run as failed if exception occurred
    finally:
        simulation_status["running"] = False
        simulation_status["terminated"] = False
        # Ensure run is finished even if loop finished normally but logging was enabled
        # if run and run.sweep_id is None: # Check if it's part of a sweep? Avoid double finish?
        #      try:
        #          if run.state == "running": run.finish()
        #      except Exception as finish_e:
        #          print(f"Error finishing wandb run: {finish_e}")

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

training_status = {
    "running": False,
    "progress": 0,
    "total_episodes": 0,
    "current_avg_score": 0,
    "error": None
}
training_thread = None

# --- Helper function for TD training ---
def train_td_worker(num_episodes, save_interval=100):
    global training_status
    try:
        training_status["running"] = True
        training_status["progress"] = 0
        training_status["total_episodes"] = num_episodes
        training_status["error"] = None
        training_status["current_avg_score"] = 0

        train_game = Game() 
        td_agent_class = get_agent('td_learning')
        if not td_agent_class or not issubclass(td_agent_class, TDLearningAgent):
            raise ValueError("TD Learning Agent not found or invalid.")
        
        # Instantiate agent - loads existing weights if available
        td_agent = td_agent_class(train_game)
        train_game.agent = td_agent # Assign agent instance to game

        scores = []
        print(f"Starting TD Learning training for {num_episodes} episodes...")

        for episode in range(num_episodes):
            train_game.reset_grid() # Resets grid and score
            game_over = False
            last_100_scores = []
            
            # Store features of the very first state
            features_s = td_agent._extract_features(train_game.grid)

            while not game_over:
                # 1. Choose action using epsilon-greedy (get_move handles this)
                #    get_move also stores expected next state features/value for update
                move = td_agent.get_move(is_training=True)
                
                # 2. Take action in the environment (game)
                #    The game state is updated internally by move_grid
                moved = train_game.move_grid(move)
                reward = td_agent.last_reward # Get reward stored by get_move

                if moved:
                    train_game.add_random_tile()
                else:
                    # Agent chose an invalid move - potentially penalize?
                    # For now, the state doesn't change, reward is likely 0
                    pass
                    
                game_over = train_game.is_game_over()

                # 3. Perform TD Update
                #    We need features from state s (before move) and reward/value from s' (after move)
                td_agent.update_weights(features_s) 

                # 4. Update current state features for the next iteration
                #    Use the features stored by get_move as the features for the *current* state (s)
                #    in the next step's update.
                features_s = td_agent.last_state_features if td_agent.last_state_features is not None else td_agent._extract_features(train_game.grid)

            # --- End of Episode --- #
            final_score = train_game.score
            scores.append(final_score)
            last_100_scores = scores[-100:]
            avg_score = sum(last_100_scores) / len(last_100_scores)
            training_status["progress"] = episode + 1
            training_status["current_avg_score"] = avg_score

            if (episode + 1) % 10 == 0:
                 print(f"Episode {episode+1}/{num_episodes} | Score: {final_score} | Avg Score (last 100): {avg_score:.2f}")

            # Save weights periodically
            if (episode + 1) % save_interval == 0:
                td_agent.save_weights()

        # Final save after training completes
        td_agent.save_weights()
        print("TD Learning training finished.")

    except Exception as e:
        print(f"TD Training failed: {e}")
        training_status["error"] = str(e)
    finally:
        training_status["running"] = False

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