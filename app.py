from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from texasholdem.game.game import TexasHoldEm
from texasholdem.agents import random_agent

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Initialize a TexasHoldEm game with 2 players
game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=2)
game.start_hand()

# Emit game information to all connected clients
def emit_game_info():
    game_info = {
        'hand_phase': str(game.hand_phase),
        'current_player': game.current_player,
        'chips_to_call': game.chips_to_call(game.current_player),
        'hand_cards': [str(card) for card in game.get_hand(game.current_player)],
    }
    print("Game Info:", game_info)  # Print game information to the console
    socketio.emit('game_info', game_info)

# Endpoint to take a random action for the current player
@app.route('/api/take_random_action', methods=['POST'])
def take_random_action():
    if game.is_hand_running():
        action, total = random_agent(game)
        game.take_action(action, total=total)
        print(f"Player {game.current_player} took action: {action}, total: {total}")
        emit_game_info()  # Emit updated game information after the action
        return jsonify({'action': str(action), 'total': total})
    else:
        return jsonify({'message': 'Hand is not running'})

# Endpoint to reset the game for a new hand
@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    game.start_hand()
    print("Game reset for a new hand")
    emit_game_info()  # Emit updated game information after the reset
    return jsonify({'message': 'Game reset for a new hand'})

# Socket.io connection event
@socketio.on('connect')
def handle_connect():
    emit_game_info()  # Emit initial game information when a client connects

if __name__ == '__main__':
    socketio.run(app, debug=True)
