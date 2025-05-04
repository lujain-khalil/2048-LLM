from simulation.game import Game
import time
import psutil
import wandb
import os

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
        
        # Apply agent-specific parameters by using the centralized approach
        # rather than setting them directly
        if agent_params:
            # Reset the grid with the agent parameters
            if not sim_game.set_agent(agent_name, agent_params):
                raise ValueError(f"Failed to set agent '{agent_name}' with params {agent_params}")
            sim_game.reset_grid()  # Instantiate the agent with the parameters

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
                move, moved, game_over, _ = sim_game.simulate_move()
                decision_end_time = time.perf_counter()
                decision_times_this_game.append(decision_end_time - decision_start_time)

                # If the agent encountered an error (move is None), terminate this game
                if move is None:
                    print(f"Agent error in game {i+1}: {sim_game.last_move}")
                    game_over = True
                    continue

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
