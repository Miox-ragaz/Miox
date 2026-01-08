from flask import Flask, render_template_string, request, jsonify
import threading
import time
import uuid
from datetime import datetime

app = Flask(__name__)

# هياكل البيانات
players = {}
games = {}
waiting_list = []
lock = threading.Lock()

# الصفحة الرئيسية
html_main = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>XO - لعبة متعددة اللاعبين</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { width: 100%; max-width: 400px; }
        .login-box { background: white; padding: 30px; border-radius: 15px; text-align: center; }
        h1 { color: #333; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h1>🎮 XO متعدد اللاعبين</h1>
            <input type="text" id="playerName" placeholder="اسمك" maxlength="15">
            <button onclick="registerPlayer()">بدء اللعب</button>
            <div id="errorMsg" class="error"></div>
        </div>
    </div>
    <script>
        function generatePlayerId() {
            return 'player_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        function registerPlayer() {
            const name = document.getElementById('playerName').value.trim();
            const errorDiv = document.getElementById('errorMsg');
            
            if (!name) {
                errorDiv.textContent = '⚠️ أدخل اسمك';
                return;
            }
            
            const playerId = generatePlayerId();
            
            fetch('/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    player_id: playerId,
                    player_name: name
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    localStorage.setItem('xo_player_id', playerId);
                    localStorage.setItem('xo_player_name', name);
                    window.location.href = '/waiting';
                } else {
                    errorDiv.textContent = '❌ ' + (data.error || 'فشل التسجيل');
                }
            });
        }
        
        document.getElementById('playerName').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') registerPlayer();
        });
    </script>
</body>
</html>
"""

# صفحة الانتظار
html_waiting = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>جاري البحث عن خصم</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        .waiting-box { background: white; padding: 30px; border-radius: 15px; text-align: center; }
        .loader { margin: 20px auto; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        button { padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 8px; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="waiting-box">
        <h1>🔍 جاري البحث عن خصم...</h1>
        <div class="loader"></div>
        <div id="waitTime">0s</div>
        <button onclick="cancelSearch()">❌ إلغاء</button>
    </div>
    <script>
        let waitStart = Date.now();
        
        function updateWaitTime() {
            const waitSeconds = Math.floor((Date.now() - waitStart) / 1000);
            document.getElementById('waitTime').textContent = waitSeconds + 's';
        }
        
        function checkForGame() {
            const playerId = localStorage.getItem('xo_player_id');
            if (!playerId) return;
            
            fetch('/check_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ player_id: playerId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.game_id) {
                    window.location.href = '/game/' + data.game_id;
                }
            });
        }
        
        function cancelSearch() {
            const playerId = localStorage.getItem('xo_player_id');
            if (playerId) {
                fetch('/cancel_wait', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ player_id: playerId })
                });
            }
            localStorage.clear();
            window.location.href = '/';
        }
        
        updateWaitTime();
        checkForGame();
        setInterval(checkForGame, 2000);
        setInterval(updateWaitTime, 1000);
    </script>
</body>
</html>
"""

# صفحة اللعبة
html_game = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>لعبة XO</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        .game-container { background: white; padding: 20px; border-radius: 15px; text-align: center; }
        .game-board { display: grid; grid-template-columns: repeat(3, 100px); gap: 10px; margin: 20px auto; }
        .cell { width: 100px; height: 100px; background: #eee; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 40px; cursor: pointer; }
        .cell.x { color: #667eea; }
        .cell.o { color: #f5576c; }
        .status { margin: 15px 0; font-size: 20px; font-weight: bold; }
        button { padding: 10px 20px; margin: 5px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>🎮 لعبة XO</h1>
        <div id="status" class="status">⏳ جاري تحميل...</div>
        <div class="game-board" id="board"></div>
        <div>
            <button onclick="location.reload()">🔄 تحديث</button>
            <button onclick="quitGame()">🚪 خروج</button>
        </div>
    </div>
    <script>
        const gameId = '{{game_id}}';
        const playerId = localStorage.getItem('xo_player_id');
        
        function updateBoard(board) {
            const boardElement = document.getElementById('board');
            boardElement.innerHTML = '';
            
            board.forEach((cell, index) => {
                const cellDiv = document.createElement('div');
                cellDiv.className = 'cell';
                cellDiv.textContent = cell || '';
                if (cell) {
                    cellDiv.classList.add(cell.toLowerCase());
                    cellDiv.style.cursor = 'default';
                } else {
                    cellDiv.onclick = () => makeMove(index);
                }
                boardElement.appendChild(cellDiv);
            });
        }
        
        function updateGame() {
            if (!playerId) {
                window.location.href = '/';
                return;
            }
            
            fetch('/game_state/' + gameId, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ player_id: playerId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('status').textContent = data.turn === (data.player_symbol === 'X' ? 'X' : 'O') ? '✅ دورك!' : '⏳ دور الخصم';
                    updateBoard(data.board);
                    
                    if (data.winner) {
                        document.getElementById('status').textContent = '🎉 الفائز: ' + data.winner;
                    } else if (data.is_draw) {
                        document.getElementById('status').textContent = '🤝 تعادل';
                    }
                }
            });
        }
        
        function makeMove(index) {
            fetch('/move/' + gameId, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    player_id: playerId,
                    index: index
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateGame();
                }
            });
        }
        
        function quitGame() {
            if (confirm('هل تريد الخروج؟')) {
                localStorage.clear();
                window.location.href = '/';
            }
        }
        
        updateGame();
        setInterval(updateGame, 1000);
    </script>
</body>
</html>
"""

# ========== Routes ==========
@app.route('/')
def index():
    return render_template_string(html_main)

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        player_name = data.get('player_name')
        
        with lock:
            players[player_id] = {
                'name': player_name,
                'last_seen': datetime.now().isoformat()
            }
            waiting_list.append(player_id)
        
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@app.route('/waiting')
def waiting():
    return render_template_string(html_waiting)

@app.route('/check_game', methods=['POST'])
def check_game():
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        with lock:
            if player_id in players:
                players[player_id]['last_seen'] = datetime.now().isoformat()
                
                for game_id, game in games.items():
                    if player_id in [game['player1_id'], game['player2_id']]:
                        return jsonify({'success': True, 'game_id': game_id})
        
        return jsonify({'success': True, 'waiting': True})
    except:
        return jsonify({'success': False})

@app.route('/cancel_wait', methods=['POST'])
def cancel_wait():
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        with lock:
            if player_id in waiting_list:
                waiting_list.remove(player_id)
            if player_id in players:
                del players[player_id]
        
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@app.route('/game/<game_id>')
def game_page(game_id):
    with lock:
        if game_id not in games:
            return "اللعبة غير موجودة", 404
        return render_template_string(html_game, game_id=game_id)

@app.route('/game_state/<game_id>', methods=['POST'])
def game_state(game_id):
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        with lock:
            if game_id not in games:
                return jsonify({'success': False}), 404
            
            game = games[game_id]
            
            if player_id not in [game['player1_id'], game['player2_id']]:
                return jsonify({'success': False}), 403
            
            player_symbol = 'X' if player_id == game['player1_id'] else 'O'
            
            return jsonify({
                'success': True,
                'board': game['board'],
                'turn': game['turn'],
                'winner': game.get('winner'),
                'is_draw': game.get('is_draw', False),
                'player_symbol': player_symbol
            })
    except:
        return jsonify({'success': False})

@app.route('/move/<game_id>', methods=['POST'])
def make_move(game_id):
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        index = data.get('index')
        
        with lock:
            if game_id not in games:
                return jsonify({'success': False}), 404
            
            game = games[game_id]
            
            if player_id not in [game['player1_id'], game['player2_id']]:
                return jsonify({'success': False}), 403
            
            player_symbol = 'X' if player_id == game['player1_id'] else 'O'
            
            if game['turn'] != player_symbol:
                return jsonify({'success': False}), 403
            
            if game['board'][index]:
                return jsonify({'success': False}), 400
            
            game['board'][index] = player_symbol
            
            # Check win
            win_lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
            for line in win_lines:
                a,b,c = line
                if game['board'][a] and game['board'][a] == game['board'][b] == game['board'][c]:
                    game['winner'] = player_symbol
                    break
            
            if not game['winner'] and "" not in game['board']:
                game['is_draw'] = True
            
            game['turn'] = 'O' if game['turn'] == 'X' else 'X'
            
            return jsonify({'success': True})
    except:
        return jsonify({'success': False})

def check_winner(board):
    win_lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for line in win_lines:
        a,b,c = line
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def matchmaking():
    while True:
        try:
            with lock:
                if len(waiting_list) >= 2:
                    p1 = waiting_list.pop(0)
                    p2 = waiting_list.pop(0)
                    
                    if p1 in players and p2 in players:
                        game_id = str(uuid.uuid4())[:6]
                        games[game_id] = {
                            'player1_id': p1,
                            'player2_id': p2,
                            'board': [""]*9,
                            'turn': 'X',
                            'winner': None,
                            'is_draw': False
                        }
        except:
            pass
        time.sleep(1)

def cleanup():
    while True:
        try:
            current_time = datetime.now()
            with lock:
                # Clean old players
                expired = []
                for pid, info in list(players.items()):
                    try:
                        last_seen = datetime.fromisoformat(info['last_seen'])
                        if (current_time - last_seen).total_seconds() > 300:
                            expired.append(pid)
                    except:
                        expired.append(pid)
                
                for pid in expired:
                    if pid in waiting_list:
                        waiting_list.remove(pid)
                    del players[pid]
        except:
            pass
        time.sleep(60)

# Start background threads
threading.Thread(target=matchmaking, daemon=True).start()
threading.Thread(target=cleanup, daemon=True).start()

# لا تضيف app.run هنا - Render يستخدم gunicorn