from app import app
from flask import render_template, jsonify
from simulation.game import Game

game = None

@app.route('/')
def index():
    global game
    game = Game()  # Create a new game with 2 random tiles
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
    if agent_name == 'random':
        from agents import random_agent
        game.set_agent(random_agent)
        
    elif agent_name == 'loop':
        from agents import loop_agent
        game.set_agent(loop_agent)

    return jsonify(status="ok", agent=agent_name)

if __name__ == '__main__':
    game = Game()
    app.run(debug=True)