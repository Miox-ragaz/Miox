from flask import Flask, render_template_string, request, jsonify
import threading, time, uuid, os
from datetime import datetime

app = Flask(__name__)

# ======== بيانات اللعبة ========
players = {}       # {player_id: {name, game_id, last_seen}}
games = {}         # {game_id: {player1_id, player2_id, board, turn, winner, etc.}}
waiting_list = []  # قائمة الانتظار
lock = threading.Lock()

# ======== HTML كما هو من كودك ========
# html_main, html_waiting, html_game ... (انسخ نفس الكود هنا بدون تعديل)

# ======== Routes ========
@app.route('/')
def index():
    return render_template_string(html_main)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    player_id = data.get('player_id')
    player_name = data.get('player_name')

    if not player_id or not player_name:
        return jsonify({'success': False, 'error': 'بيانات غير مكتملة'})

    with lock:
        # منع الاسم المكرر في اللعبة الحالية
        for pid, info in players.items():
            if info['name'] == player_name and info.get('game_id'):
                return jsonify({'success': False, 'error': 'الاسم مستخدم في لعبة حالية'})

        players[player_id] = {'name': player_name, 'last_seen': datetime.now().isoformat(), 'game_id': None}
        if player_id not in waiting_list:
            waiting_list.append(player_id)

    return jsonify({'success': True})

@app.route('/reconnect', methods=['POST'])
def reconnect():
    data = request.get_json()
    player_id = data.get('player_id')
    if not player_id:
        return jsonify({'success': False})
    with lock:
        if player_id in players:
            player_info = players[player_id]
            player_info['last_seen'] = datetime.now().isoformat()
            if player_info.get('game_id'):
                return jsonify({'success': True, 'game_id': player_info['game_id']})
            elif player_id in waiting_list:
                return jsonify({'success': True, 'in_waiting': True})
    return jsonify({'success': False})

# البقية من Routes كما هي (check_game, stats, cancel_wait, game_page, game_state, make_move, quit, heartbeat, check_player)
# انسخ كل Routes كما في الكود الأصلي بدون تعديل أي وظيفة اللعبة

# ======== وظائف داخلية ========
def check_winner(board):
    win_lines = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for line in win_lines:
        a,b,c = line
        if board[a] and board[a] == board[b] == board[c]:
            return line
    return None

# ======== خيوط اللعبة ========
def matchmaking_thread():
    while True:
        with lock:
            if len(waiting_list) >= 2:
                p1 = waiting_list.pop(0)
                p2 = waiting_list.pop(0)
                if p1 not in players or p2 not in players:
                    continue
                game_id = str(uuid.uuid4())[:6]
                games[game_id] = {
                    'player1_id': p1,
                    'player2_id': p2,
                    'board': [""]*9,
                    'turn': 'X',
                    'winner': None,
                    'win_line': None,
                    'is_draw': False,
                    'created_at': datetime.now().isoformat(),
                    'last_update': datetime.now().isoformat()
                }
                players[p1]['game_id'] = game_id
                players[p2]['game_id'] = game_id
        time.sleep(1)

def cleanup_thread():
    while True:
        current_time = datetime.now()
        with lock:
            # تنظيف اللاعبين غير النشطين
            inactive = []
            for pid, info in list(players.items()):
                try:
                    last_seen = datetime.fromisoformat(info['last_seen'])
                    if (current_time - last_seen).total_seconds() > 300:
                        inactive.append(pid)
                except:
                    inactive.append(pid)
            for pid in inactive:
                if pid in waiting_list: waiting_list.remove(pid)
                game_id = players[pid].get('game_id')
                if game_id and game_id in games:
                    game = games[game_id]
                    other = game['player2_id'] if pid == game['player1_id'] else game['player1_id']
                    game['winner'] = 'O' if pid == game['player1_id'] else 'X'
                    if other in players: players[other]['game_id'] = None
                del players[pid]
            # تنظيف الألعاب القديمة
            expired = []
            for gid, game in list(games.items()):
                try:
                    last_update = datetime.fromisoformat(game['last_update'])
                    if (current_time - last_update).total_seconds() > 3600:
                        expired.append(gid)
                except:
                    expired.append(gid)
            for gid in expired:
                game = games[gid]
                if game['player1_id'] in players: players[game['player1_id']]['game_id'] = None
                if game['player2_id'] in players: players[game['player2_id']]['game_id'] = None
                del games[gid]
        time.sleep(60)

# ======== بدء الخيوط ========
# للتأكد أنها تعمل مرة واحدة فقط
if not hasattr(app, 'threads_started'):
    threading.Thread(target=matchmaking_thread, daemon=True).start()
    threading.Thread(target=cleanup_thread, daemon=True).start()
    app.threads_started = True

# ======== تشغيل التطبيق ========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 خادم XO جاهز على PORT: {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)