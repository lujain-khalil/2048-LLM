from app import app
from flask import render_template, jsonify
from simulation.game import Game
from agents.registry import get_agent, list_agents

game = None

@app.route('/')
def index():
    global game
    game = Game()
    return render_template('index.html', grid=game.grid, move=game.last_move)

@app.route('/update')
def update():
    global game
    move = game.simulate_move()
    return jsonify(move=game.last_move, grid=game.grid)

@app.route('/restart')
def restart():
    global game
    game = Game()  # Replace the current game with a new one
    return jsonify(grid=game.grid)

@app.route('/set_agent/<agent_name>')
def set_agent(agent_name):
    global game
    agent = get_agent(agent_name)
    if agent:
        game.set_agent(agent)
        return jsonify(status="ok", agent=agent_name)
    else:
        return jsonify(status="error", message="Unknown agent"), 400

@app.route('/agents')
def agents():
    return jsonify(agents=list_agents())

if __name__ == '__main__':
    game = Game()
    app.run(debug=True)