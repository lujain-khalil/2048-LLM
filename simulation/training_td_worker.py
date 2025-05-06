from simulation.game import Game
from agents.registry import get_agent
from agents.td_learning_agent import TDLearningAgent

training_status = {
    "running": False,
    "progress": 0,
    "total_episodes": 0,
    "current_avg_score": 0,
    "error": None
}
training_thread = None

# --- Helper function for TD training ---
def train_td_worker(num_episodes, save_interval=100, training=True):
    global training_status
    try:
        training_status.update({
            "running": True,
            "progress": 0,
            "total_episodes": num_episodes,
            "current_avg_score": 0,
            "error": None
        })

        train_game = Game() 
        td_agent_class = get_agent('td_learning')
        if not td_agent_class or not issubclass(td_agent_class, TDLearningAgent):
            raise ValueError("TD Learning Agent not found or invalid.")
        
        # Instantiate agent - loads existing weights if available
        td_agent = td_agent_class(train_game)
        train_game.agent = td_agent # Assign agent instance to game

        scores = []
        print(f"Starting TD Learning training for {num_episodes} episodes...")

        for ep in range(num_episodes):
            train_game.reset_grid()
            game_over = False
            
            features_s = td_agent._extract_features(train_game.grid)

            while not game_over:
                # 1. Choose action using epsilon-greedy (get_move handles this)
                #    get_move also stores expected next state features/value for update
                # move = td_agent.get_move(is_training=True)
                move = td_agent.get_move(is_training=training)
                
                # 2. Take action in the environment (game)
                #    The game state is updated internally by move_grid
                moved = train_game.move_grid(move)
                reward = td_agent.last_reward # Get reward stored by get_move

                if moved:
                    train_game.add_random_tile()
                
                if training:
                    # 3. Perform TD Update
                    features_s_prime = td_agent._extract_features(train_game.grid)
                    td_agent.last_state_features = features_s_prime
                    td_agent.last_state_value    = td_agent._get_value(train_game.grid)
                    # td_agent.last_reward         = reward

                    # 4. Update current state features for the next iteration
                    td_agent.update_weights(features_s)
                    features_s = features_s_prime

                game_over = train_game.is_game_over()

            # --- End of Episode --- #
            final_score = train_game.score
            scores.append(final_score)
            last_100_scores = scores[-100:]
            avg_score = sum(last_100_scores) / len(last_100_scores)
            training_status["progress"] = ep + 1
            training_status["current_avg_score"] = avg_score

            if (ep + 1) % 10 == 0:
                 print(f"Episode {ep+1}/{num_episodes} | Score: {final_score} | Avg Score (last 100): {avg_score:.2f}")

            # Save weights periodically
            if training and (ep + 1) % save_interval == 0:
                td_agent.save_weights()

        if training:
            # Final save after training completes
            td_agent.save_weights()
            print("TD Learning training finished.")
        else:
            print("Evaluation run complete (no weights updated).")

    except Exception as e:
        print(f"TD Training failed: {e}")
        training_status["error"] = str(e)
    finally:
        training_status["running"] = False