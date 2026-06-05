from flask import Flask, request, jsonify, render_template_string
import time
import uuid

app = Flask(__name__)

# ==========================================
# 1. إعدادات السيرفر والذاكرة العشوائية (النظام الخفيف)
# ==========================================
ADMIN_PASSWORD = "@#₹%@#₹%@#₹%@#₹%@#₹%"

# خلايا الذاكرة (قواميس بايثون فائقة السرعة)
waiting_players = {}  # {player_id: timestamp}
active_rooms = {}     # {room_id: {'p1': id, 'p2': id, 'last_active': timestamp}}
pending_moves = {}    # {room_id: {'move': text, 'sender': id, 'timestamp': timestamp}}

# ==========================================
# 2. نظام التنظيف الصارم (Strict Cleanup) - يمسح أي شيء يتجاوز 50 ثانية
# ==========================================
def cleanup_dead_connections():
    current_time = time.time()
    
    # تنظيف قائمة الانتظار
    dead_waiters = [pid for pid, t in waiting_players.items() if current_time - t > 50]
    for pid in dead_waiters:
        del waiting_players[pid]
        
    # تنظيف الغرف الميتة (التي لم يحدث فيها أي تحرك لـ 50 ثانية)
    dead_rooms = [rid for rid, data in active_rooms.items() if current_time - data['last_active'] > 50]
    for rid in dead_rooms:
        del active_rooms[rid]
        if rid in pending_moves:
            del pending_moves[rid] # حذف أي حركة عالقة لتفريغ الذاكرة 100%

# ==========================================
# 3. واجهة المشرف (Admin Dashboard)
# ==========================================
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>AL0 99 - لوحة التحكم</title>
    <style>
        body { background-color: #1a1a1a; color: #00ffcc; font-family: monospace; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #00ffcc; padding: 10px; text-align: center; }
        .box { background: #222; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        input[type="password"] { padding: 10px; width: 300px; background: #000; color: #00ffcc; border: 1px solid #00ffcc; }
        button { padding: 10px 20px; background: #00ffcc; color: #000; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <h2>🚀 غرفة التحكم المركزية - النظام 99</h2>
    
    {% if not logged_in %}
        <div class="box">
            <form method="POST">
                <p>أدخل كلمة السر المشفرة:</p>
                <input type="password" name="password" required>
                <button type="submit">دخول</button>
            </form>
        </div>
    {% else %}
        <div class="box">
            <h3>اللاعبون في الانتظار (خلية البحث): {{ wait_count }}</h3>
            <table>
                <tr><th>معرف اللاعب</th><th>وقت الانتظار</th></tr>
                {% for pid, t in waiting.items() %}
                <tr><td>{{ pid }}</td><td>يبحث الآن...</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="box">
            <h3>الغرف النشطة الآن (خلية اللعب): {{ room_count }}</h3>
            <table>
                <tr><th>رقم الغرفة</th><th>اللاعب الأول (أبيض)</th><th>اللاعب الثاني (أسود)</th></tr>
                {% for rid, data in rooms.items() %}
                <tr><td>{{ rid }}</td><td>{{ data.p1 }}</td><td>{{ data.p2 }}</td></tr>
                {% endfor %}
            </table>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    cleanup_dead_connections()
    logged_in = False
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            logged_in = True
            
    return render_template_string(HTML_DASHBOARD, 
                                  logged_in=logged_in, 
                                  waiting=waiting_players, 
                                  rooms=active_rooms,
                                  wait_count=len(waiting_players),
                                  room_count=len(active_rooms))

# ==========================================
# 4. مسار البحث عن غرف (Matchmaking API)
# ==========================================
@app.route('/matchmake', methods=['POST'])
def matchmake():
    cleanup_dead_connections()
    player_id = request.json.get('player_id')
    current_time = time.time()
    
    # إذا كان هناك شخص ينتظر، اسحبه وأنشئ غرفة فوراً
    if waiting_players:
        opponent_id, _ = waiting_players.popitem() # مسح الخصم من قائمة الانتظار (لا تكرار للبيانات)
        room_id = str(uuid.uuid4())[:8] # توليد ID خفيف للغرفة
        
        # وضعهم في خلية اللعب الآن
        active_rooms[room_id] = {'p1': opponent_id, 'p2': player_id, 'last_active': current_time}
        return jsonify({"status": "play", "room_id": room_id, "role": "player2", "opponent": opponent_id})
    else:
        # إذا لم يوجد أحد، ضعه في خلية الانتظار
        waiting_players[player_id] = current_time
        return jsonify({"status": "wait", "message": "يبحث عن خصم..."})

# ==========================================
# 5. مسار استقبال وإرسال الحركة (Core Logic 100% Delete)
# ==========================================
@app.route('/sync_move', methods=['POST'])
def sync_move():
    cleanup_dead_connections()
    data = request.json
    room_id = data.get('room_id')
    player_id = data.get('player_id')
    
    if room_id not in active_rooms:
        return jsonify({"status": "error", "message": "Connection Lost - 50s Timeout"}), 404
        
    # تحديث وقت نشاط الغرفة لكي لا تُمسح
    active_rooms[room_id]['last_active'] = time.time()

    # إذا اللاعب أرسل حركة جديدة
    if 'move' in data:
        pending_moves[room_id] = {
            'move': data['move'],
            'sender': player_id,
            'timestamp': time.time()
        }
        return jsonify({"status": "sent"})
        
    # إذا اللاعب يطلب تحديثاً (هل الخصم تحرك؟)
    if room_id in pending_moves:
        move_data = pending_moves[room_id]
        # إذا كانت الحركة قادمة من الخصم (وليست حركتي أنا)
        if move_data['sender'] != player_id:
            fetched_move = move_data['move']
            # الحذف الصارم الفوري (100% مسح من الذاكرة بمجرد الاستلام)
            del pending_moves[room_id]
            return jsonify({"status": "new_move", "move": fetched_move})
            
    return jsonify({"status": "no_move"})

if __name__ == '__main__':
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=5000)
