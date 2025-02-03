from flask import Flask, render_template, request, jsonify
import random
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key

# Global game state
rooms = {}  # Stores game states for each room
lock = threading.Lock()  # Ensures thread-safe operations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room_id = str(random.randint(1000, 9999))
    with lock:
        rooms[room_id] = {
            'players': [],
            'board': ['' for _ in range(9)],
            'turn': 'X',
            'game_over': False,
            'winner': None
        }
    return jsonify({'room': room_id})

@app.route('/join_room', methods=['POST'])
def join_room():
    data = request.get_json()
    room_id = data['room']
    username = data['username']
    with lock:
        if room_id in rooms:
            room = rooms[room_id]
            if len(room['players']) < 2:
                room['players'].append(username)
                symbol = 'X' if len(room['players']) == 1 else 'O'
                return jsonify({'success': True, 'symbol': symbol})
            else:
                return jsonify({'success': False, 'message': 'Room is full.'})
        else:
            return jsonify({'success': False, 'message': 'Room does not exist.'})

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.get_json()
    room_id = data['room']
    index = data['index']
    symbol = data['symbol']
    with lock:
        room = rooms.get(room_id)
        if room and not room['game_over']:
            if room['board'][index] == '':
                if room['turn'] == symbol:
                    room['board'][index] = symbol
                    winning_combination = check_win(room['board'], symbol)
                    if winning_combination:
                        room['game_over'] = True
                        room['winner'] = symbol
                        room['winning_combination'] = winning_combination
                    elif '' not in room['board']:
                        room['game_over'] = True
                        room['winner'] = 'Tie'
                    else:
                        room['turn'] = 'O' if room['turn'] == 'X' else 'X'
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'message': 'Not your turn.'})
            else:
                return jsonify({'success': False, 'message': 'Cell already taken.'})
        else:
            return jsonify({'success': False, 'message': 'Invalid game or game over.'})

@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    room_id = request.args.get('room')
    with lock:
        room = rooms.get(room_id)
        if room:
            return jsonify({
                'board': room['board'],
                'turn': room['turn'],
                'game_over': room['game_over'],
                'winner': room['winner'],
                'winning_combination': room.get('winning_combination', [])
            })
        else:
            return jsonify({'message': 'Room does not exist.'}), 404

def check_win(board, symbol):
    win_conditions = [
        [0, 1, 2],  # Rows
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],  # Columns
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],  # Diagonals
        [2, 4, 6]
    ]
    for condition in win_conditions:
        if all(board[i] == symbol for i in condition):
            return condition
    return None

if __name__ == '__main__':
    app.run(debug=True)
