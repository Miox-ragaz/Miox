from flask import Flask, render_template_string, request, jsonify
import threading
import time
import uuid
from datetime import datetime

app = Flask(__name__)

# هياكل البيانات المحسنة
players = {}  # {player_id: {name, game_id, last_seen}}
games = {}    # {game_id: {player1_id, player2_id, board, turn, winner, etc.}}
waiting_list = []  # قائمة اللاعبين المنتظرين

# أقفال للأمان
lock = threading.Lock()

html_main = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>XO - متعدد اللاعبين</title>
    <meta charset="UTF-8">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 400px;
        }
        
        .login-box {
            background: white;
            padding: 40px 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 28px;
        }
        
        .logo {
            font-size: 50px;
            margin-bottom: 20px;
            color: #667eea;
        }
        
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            text-align: center;
            transition: all 0.3s;
        }
        
        input:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
        
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .error {
            color: #e74c3c;
            margin-top: 15px;
            font-size: 14px;
            min-height: 20px;
        }
        
        .info {
            color: #7f8c8d;
            margin-top: 25px;
            font-size: 14px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box" id="loginBox">
            <div class="logo">🎮</div>
            <h1>لعبة XO الجماعية</h1>
            <input type="text" id="playerName" placeholder="ادخل اسمك للعب" maxlength="15" autocomplete="off">
            <button onclick="registerPlayer()" id="loginBtn">🚀 ابدأ اللعب</button>
            <div id="errorMsg" class="error"></div>
            <div class="info">
                ✓ العب مع لاعبين آخرين على نفس الشبكة<br>
                ✓ المطابقة التلقائية مع خصم<br>
                ✓ منع التدخل في أدوار الآخرين
            </div>
        </div>
    </div>
    
    <script>
        // توليد معرف فريد للاعب
        function generatePlayerId() {
            return 'player_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        // حفظ بيانات اللاعب في التخزين المحلي
        function savePlayerData(playerId, playerName) {
            localStorage.setItem('xo_player_id', playerId);
            localStorage.setItem('xo_player_name', playerName);
            localStorage.setItem('xo_last_activity', Date.now());
        }
        
        // تسجيل اللاعب
        function registerPlayer() {
            const nameInput = document.getElementById('playerName');
            const button = document.getElementById('loginBtn');
            const errorDiv = document.getElementById('errorMsg');
            const playerName = nameInput.value.trim();
            
            if (!playerName) {
                errorDiv.textContent = '⚠️ يرجى إدخال اسم اللاعب';
                nameInput.focus();
                return;
            }
            
            if (playerName.length < 2) {
                errorDiv.textContent = '⚠️ الاسم يجب أن يكون حرفين على الأقل';
                return;
            }
            
            // تعطيل الزر أثناء التحميل
            button.disabled = true;
            button.textContent = 'جاري التسجيل...';
            errorDiv.textContent = '';
            
            // توليد معرف اللاعب
            const playerId = generatePlayerId();
            
            // إرسال طلب التسجيل
            fetch('/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    player_id: playerId,
                    player_name: playerName
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network error');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // حفظ بيانات اللاعب محلياً
                    savePlayerData(playerId, playerName);
                    
                    // الانتقال لصفحة الانتظار
                    window.location.href = '/waiting';
                } else {
                    errorDiv.textContent = '❌ ' + (data.error || 'فشل التسجيل');
                    button.disabled = false;
                    button.textContent = '🚀 ابدأ اللعب';
                }
            })
            .catch(error => {
                errorDiv.textContent = '❌ خطأ في الاتصال بالخادم';
                button.disabled = false;
                button.textContent = '🚀 ابدأ اللعب';
                console.error('Error:', error);
            });
        }
        
        // السماح بالدخول باستخدام Enter
        document.getElementById('playerName').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                registerPlayer();
            }
        });
        
        // تركيز على حقل الاسم عند التحميل
        window.onload = function() {
            document.getElementById('playerName').focus();
            
            // التحقق إذا كان هناك بيانات لاعب مخزنة
            const savedPlayerId = localStorage.getItem('xo_player_id');
            const savedPlayerName = localStorage.getItem('xo_player_name');
            
            if (savedPlayerId && savedPlayerName) {
                // محاولة إعادة الاتصال
                fetch('/reconnect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        player_id: savedPlayerId,
                        player_name: savedPlayerName
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.game_id) {
                            // الانتقال مباشرة للعبة
                            window.location.href = `/game/${data.game_id}`;
                        } else if (data.in_waiting) {
                            // الانتقال لصفحة الانتظار
                            window.location.href = '/waiting';
                        }
                    }
                });
            }
        };
    </script>
</body>
</html>
"""

html_waiting = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>جاري البحث عن خصم - XO</title>
    <meta charset="UTF-8">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .waiting-container {
            background: white;
            padding: 40px 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            text-align: center;
            width: 100%;
            max-width: 500px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 28px;
        }
        
        .player-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            font-size: 20px;
            font-weight: bold;
        }
        
        .loader {
            margin: 40px auto;
            width: 60px;
            height: 60px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 40px 0;
            gap: 15px;
        }
        
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            flex: 1;
            border: 2px solid #e9ecef;
        }
        
        .stat-box div:first-child {
            color: #6c757d;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .stat-box div:last-child {
            color: #333;
            font-size: 24px;
            font-weight: bold;
        }
        
        button {
            padding: 15px 40px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        button:hover {
            background: #c0392b;
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .instructions {
            margin-top: 30px;
            color: #6c757d;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .network-info {
            background: #e9ecef;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 12px;
            color: #495057;
        }
    </style>
</head>
<body>
    <div class="waiting-container">
        <h1>🔍 جاري البحث عن خصم...</h1>
        
        <div class="player-card" id="playerInfo">
            <!-- يتم تعبئته بالجافاسكريبت -->
        </div>
        
        <div class="loader"></div>
        
        <div class="stats">
            <div class="stat-box">
                <div>👥 في الانتظار</div>
                <div id="waitingCount">0</div>
            </div>
            <div class="stat-box">
                <div>🎮 ألعاب نشطة</div>
                <div id="activeGames">0</div>
            </div>
            <div class="stat-box">
                <div>⏱️ وقت الانتظار</div>
                <div id="waitTime">0s</div>
            </div>
        </div>
        
        <button onclick="cancelSearch()">❌ إلغاء البحث</button>
        
        <div class="instructions">
            <strong>معلومات مهمة:</strong><br>
            ✓ انتظر حتى يجد النظام خصم مناسب<br>
            ✓ يمكن أن يستغرق الأمر بضع ثوانٍ<br>
            ✓ تأكد من أن الجهاز الآخر على نفس الشبكة
        </div>
        
        <div class="network-info" id="networkInfo">
            <!-- معلومات الشبكة -->
        </div>
    </div>
    
    <script>
        // الحصول على بيانات اللاعب من التخزين المحلي
        const playerId = localStorage.getItem('xo_player_id');
        const playerName = localStorage.getItem('xo_player_name');
        
        let waitStartTime = Date.now();
        let checkInterval;
        let statsInterval;
        
        // تحديث معلومات اللاعب
        function updatePlayerInfo() {
            if (playerName) {
                document.getElementById('playerInfo').textContent = `👤 اللاعب: ${playerName}`;
            }
        }
        
        // تحديث وقت الانتظار
        function updateWaitTime() {
            const waitTime = Math.floor((Date.now() - waitStartTime) / 1000);
            document.getElementById('waitTime').textContent = waitTime + 's';
        }
        
        // التحقق من وجود لعبة
        function checkForGame() {
            if (!playerId) {
                alert('❌ لم يتم العثور على بيانات اللاعب');
                window.location.href = '/';
                return;
            }
            
            fetch('/check_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ player_id: playerId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network error');
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.game_id) {
                    // تم العثور على لعبة، الانتقال إليها
                    window.location.href = `/game/${data.game_id}`;
                } else if (data.error) {
                    if (data.error === 'player_not_found') {
                        alert('❌ تم إزالة اللاعب من النظام');
                        localStorage.clear();
                        window.location.href = '/';
                    }
                }
            })
            .catch(error => {
                console.error('Error checking game:', error);
            });
        }
        
        // تحديث الإحصائيات
        function updateStats() {
            fetch('/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('waitingCount').textContent = data.waiting;
                    document.getElementById('activeGames').textContent = data.active_games;
                });
        }
        
        // إلغاء البحث
        function cancelSearch() {
            if (!playerId) {
                window.location.href = '/';
                return;
            }
            
            fetch('/cancel_wait', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ player_id: playerId })
            })
            .then(() => {
                localStorage.removeItem('xo_player_id');
                localStorage.removeItem('xo_player_name');
                window.location.href = '/';
            });
        }
        
        // عرض معلومات الشبكة
        function showNetworkInfo() {
            const networkInfo = document.getElementById('networkInfo');
            networkInfo.innerHTML = `
                <strong>معلومات الاتصال:</strong><br>
                ✓ المعرف: ${playerId ? playerId.substring(0, 15) + '...' : 'غير معروف'}<br>
                ✓ يمكن للأجهزة الأخرى الاتصال بنفس الخادم
            `;
        }
        
        // التهيئة
        updatePlayerInfo();
        updateWaitTime();
        showNetworkInfo();
        
        // البدء في التحقق فوراً
        checkForGame();
        updateStats();
        
        // تعيين الفواصل الزمنية
        checkInterval = setInterval(checkForGame, 2000);
        statsInterval = setInterval(updateStats, 3000);
        
        // تحديث وقت الانتظار كل ثانية
        setInterval(updateWaitTime, 1000);
        
        // إرسال نبضة حياة كل 30 ثانية
        setInterval(() => {
            if (playerId) {
                fetch('/heartbeat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ player_id: playerId })
                });
            }
        }, 30000);
        
        // تنظيف عند مغادرة الصفحة
        window.addEventListener('beforeunload', function() {
            if (playerId) {
                navigator.sendBeacon('/heartbeat', JSON.stringify({ player_id: playerId }));
            }
        });
    </script>
</body>
</html>
"""

html_game = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <title>لعبة XO - {{game_id}}</title>
    <meta charset="UTF-8">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .game-container {
            background: white;
            border-radius: 25px;
            padding: 30px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 900px;
        }
        
        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #f8f9fa;
        }
        
        .game-header h1 {
            color: #333;
            font-size: 32px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .game-id {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 16px;
        }
        
        .players-section {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin: 40px 0;
            gap: 30px;
        }
        
        .player {
            padding: 25px 40px;
            border-radius: 20px;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
            min-width: 250px;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .player-x {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .player-o {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .player.current-turn {
            transform: scale(1.08);
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        }
        
        .player.you::after {
            content: ' (أنت)';
            font-size: 16px;
            opacity: 0.9;
        }
        
        .vs {
            font-size: 28px;
            font-weight: bold;
            color: #6c757d;
            background: #f8f9fa;
            padding: 15px 30px;
            border-radius: 15px;
        }
        
        .game-status {
            text-align: center;
            margin: 30px 0;
            font-size: 28px;
            font-weight: bold;
            color: #333;
            min-height: 50px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        
        .game-board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 40px auto;
            width: 500px;
            height: 500px;
            background: #34495e;
            padding: 20px;
            border-radius: 25px;
        }
        
        .cell {
            background: white;
            border-radius: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 90px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            user-select: none;
        }
        
        .cell:hover {
            background: #f8f9fa;
            transform: translateY(-5px);
        }
        
        .cell.x {
            color: #667eea;
        }
        
        .cell.o {
            color: #f5576c;
        }
        
        .cell.win-cell {
            background: #ffeaa7;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .cell.disabled {
            cursor: not-allowed;
            opacity: 0.7;
            transform: none !important;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 25px;
            margin-top: 50px;
        }
        
        .control-btn {
            padding: 18px 45px;
            font-size: 20px;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .new-game {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .quit-game {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .control-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        
        .notification {
            position: fixed;
            top: 30px;
            right: 30px;
            padding: 20px 30px;
            border-radius: 15px;
            color: white;
            font-weight: bold;
            animation: slideIn 0.3s ease;
            z-index: 1000;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            max-width: 400px;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .success { background: linear-gradient(135deg, #2ecc71, #27ae60); }
        .error { background: linear-gradient(135deg, #e74c3c, #c0392b); }
        .info { background: linear-gradient(135deg, #3498db, #2980b9); }
        
        .rules {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin-top: 30px;
            font-size: 14px;
            color: #6c757d;
            line-height: 1.6;
        }
        
        @media (max-width: 768px) {
            .players-section {
                flex-direction: column;
            }
            
            .game-board {
                width: 90vw;
                height: 90vw;
                max-width: 400px;
                max-height: 400px;
            }
            
            .cell {
                font-size: 60px;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-header">
            <h1><span>🎮</span> لعبة XO الجماعية</h1>
            <div class="game-id">رقم: {{game_id}}</div>
        </div>
        
        <div class="players-section">
            <div id="playerX" class="player player-x">{{player1_name}} (X)</div>
            <div class="vs">VS</div>
            <div id="playerO" class="player player-o">{{player2_name}} (O)</div>
        </div>
        
        <div id="gameStatus" class="game-status">⏳ جاري تحميل اللعبة...</div>
        
        <div class="game-board" id="gameBoard">
            <!-- يتم تعبئته بالجافاسكريبت -->
        </div>
        
        <div class="controls">
            <button class="control-btn new-game" onclick="newGame()">
                <span>🔄</span> لعبة جديدة
            </button>
            <button class="control-btn quit-game" onclick="quitGame()">
                <span>🚪</span> خروج
            </button>
        </div>
        
        <div class="rules">
            <strong>📋 قواعد اللعبة:</strong><br>
            1. كل لاعب يلعب بدوره فقط (X يلعب دوره، O يلعب دوره)<br>
            2. لا يمكن لـ X أن يلعب مكان O أو العكس<br>
            3. الفوز يكون بملء صف، عمود، أو قطر بنفس الرمز<br>
            4. إذا امتلئت جميع الخلايا دون فائز، تكون النتيجة تعادل
        </div>
    </div>
    
    <script>
        const gameId = '{{game_id}}';
        const playerId = localStorage.getItem('xo_player_id');
        const playerName = localStorage.getItem('xo_player_name');
        
        let currentTurn = '';
        let mySymbol = '';
        let gameBoard = [];
        let gameActive = true;
        let refreshInterval;
        
        // عرض الإشعارات
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // تحديث لوحة اللعبة
        function updateBoard(board) {
            const boardElement = document.getElementById('gameBoard');
            boardElement.innerHTML = '';
            
            board.forEach((cell, index) => {
                const cellElement = document.createElement('div');
                cellElement.className = 'cell';
                
                if (cell) {
                    cellElement.textContent = cell;
                    cellElement.classList.add(cell.toLowerCase());
                    cellElement.classList.add('disabled');
                } else if (gameActive && currentTurn === mySymbol) {
                    cellElement.onclick = () => makeMove(index);
                } else {
                    cellElement.classList.add('disabled');
                }
                
                boardElement.appendChild(cellElement);
            });
        }
        
        // تحديث معلومات اللعبة
        function updateGameInfo(data) {
            if (!data || !data.success) {
                showNotification('❌ خطأ في تحميل بيانات اللعبة', 'error');
                return;
            }
            
            currentTurn = data.turn;
            gameBoard = data.board;
            
            // تحديث حالة اللاعبين
            document.getElementById('playerX').classList.toggle('current-turn', currentTurn === 'X');
            document.getElementById('playerO').classList.toggle('current-turn', currentTurn === 'O');
            
            // تحديد رمزي وإضافة علامة "أنت"
            if (!mySymbol && data.player_symbol) {
                mySymbol = data.player_symbol;
                const myPlayerElement = document.getElementById(`player${mySymbol}`);
                if (myPlayerElement) {
                    myPlayerElement.classList.add('you');
                }
            }
            
            // تحديث حالة اللعبة
            const statusElement = document.getElementById('gameStatus');
            if (data.winner) {
                statusElement.innerHTML = `🎉 الفائز: <span style="color: ${data.winner === 'X' ? '#667eea' : '#f5576c'}">${data.winner}</span>`;
                gameActive = false;
                showNotification(data.winner === mySymbol ? '🎊 مبروك! فزت باللعبة!' : '😢 خسرت! حاول مرة أخرى', 
                                data.winner === mySymbol ? 'success' : 'error');
            } else if (data.is_draw) {
                statusElement.innerHTML = '🤝 تعادل!';
                gameActive = false;
                showNotification('التعادل! حاول مرة أخرى', 'info');
            } else {
                if (currentTurn === mySymbol) {
                    statusElement.innerHTML = '✅ دورك الآن! ضع علامة ' + mySymbol;
                } else {
                    statusElement.innerHTML = '⏳ انتظر دور الخصم...';
                }
                gameActive = true;
            }
            
            updateBoard(gameBoard);
            
            // إضافة تأثير الفوز إذا كان هناك فائز
            if (data.win_line) {
                data.win_line.forEach(index => {
                    const cells = document.getElementsByClassName('cell');
                    if (cells[index]) {
                        cells[index].classList.add('win-cell');
                    }
                });
            }
        }
        
        // تحميل حالة اللعبة
        function loadGameState() {
            if (!playerId) {
                showNotification('❌ لم يتم العثور على بيانات اللاعب', 'error');
                setTimeout(() => window.location.href = '/', 2000);
                return;
            }
            
            fetch(`/game_state/${gameId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ player_id: playerId })
            })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        showNotification('❌ اللعبة غير موجودة', 'error');
                        setTimeout(() => window.location.href = '/', 2000);
                    }
                    throw new Error('Network error');
                }
                return response.json();
            })
            .then(data => {
                updateGameInfo(data);
            })
            .catch(error => {
                console.error('Error loading game:', error);
            });
        }
        
        // تنفيذ حركة
        function makeMove(index) {
            if (!gameActive || currentTurn !== mySymbol) {
                showNotification('❌ ليس دورك الآن!', 'error');
                return;
            }
            
            if (!playerId) {
                showNotification('❌ خطأ في هوية اللاعب', 'error');
                return;
            }
            
            fetch(`/move/${gameId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    player_id: playerId,
                    index: index
                })
            })
            .then(response => {
                if (response.status === 403) {
                    showNotification('❌ ليس دورك!', 'error');
                } else if (response.status === 400) {
                    showNotification('❌ حركة غير صالحة!', 'error');
                } else if (response.status === 404) {
                    showNotification('❌ اللاعب غير موجود في اللعبة', 'error');
                } else if (response.status === 200) {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.success) {
                    showNotification('✅ حركتك تم تسجيلها!', 'success');
                    setTimeout(loadGameState, 500);
                }
            })
            .catch(error => {
                showNotification('❌ خطأ في الاتصال بالخادم', 'error');
            });
        }
        
        // بدء لعبة جديدة
        function newGame() {
            if (confirm('هل تريد بدء لعبة جديدة؟')) {
                localStorage.removeItem('xo_player_id');
                localStorage.removeItem('xo_player_name');
                window.location.href = '/';
            }
        }
        
        // خروج من اللعبة
        function quitGame() {
            if (confirm('هل تريد الخروج من اللعبة؟')) {
                if (playerId) {
                    fetch(`/quit/${gameId}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ player_id: playerId })
                    });
                }
                localStorage.clear();
                window.location.href = '/';
            }
        }
        
        // إرسال نبضة حياة
        function sendHeartbeat() {
            if (playerId) {
                fetch('/heartbeat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ player_id: playerId })
                });
            }
        }
        
        // التهيئة
        loadGameState();
        refreshInterval = setInterval(loadGameState, 1500);
        
        // إرسال نبضات حياة كل 30 ثانية
        setInterval(sendHeartbeat, 30000);
        
        // إرسال نبضة حياة عند مغادرة الصفحة
        window.addEventListener('beforeunload', function() {
            if (playerId) {
                navigator.sendBeacon('/heartbeat', JSON.stringify({ player_id: playerId }));
            }
        });
        
        // فحص إذا كان اللاعب لا يزال في اللعبة
        setInterval(() => {
            if (playerId && gameActive) {
                fetch(`/check_player/${gameId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ player_id: playerId })
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.in_game) {
                        showNotification('❌ تم إزالتك من اللعبة', 'error');
                        setTimeout(() => window.location.href = '/', 3000);
                    }
                });
            }
        }, 5000);
    </script>
</body>
</html>
"""

# ============== Routes ==============

@app.route('/')
def index():
    return render_template_string(html_main)

@app.route('/register', methods=['POST'])
def register():
    """تسجيل لاعب جديد"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        player_name = data.get('player_name')
        
        if not player_id or not player_name:
            return jsonify({'success': False, 'error': 'بيانات غير مكتملة'})
        
        with lock:
            # التحقق من عدم وجود اللاعب مسبقاً
            for pid, info in players.items():
                if info['name'] == player_name and info.get('game_id'):
                    return jsonify({'success': False, 'error': 'الاسم مستخدم في لعبة حالية'})
            
            # تسجيل اللاعب الجديد
            players[player_id] = {
                'name': player_name,
                'last_seen': datetime.now().isoformat(),
                'game_id': None
            }
            
            # إضافة لقائمة الانتظار
            if player_id not in waiting_list:
                waiting_list.append(player_id)
        
        print(f"✅ لاعب جديد: {player_name} (ID: {player_id[:10]}...)")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ خطأ في التسجيل: {e}")
        return jsonify({'success': False, 'error': 'خطأ في الخادم'})

@app.route('/reconnect', methods=['POST'])
def reconnect():
    """إعادة اتصال لاعب"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'success': False})
        
        with lock:
            if player_id in players:
                player_info = players[player_id]
                player_info['last_seen'] = datetime.now().isoformat()
                
                if player_info.get('game_id'):
                    # اللاعب في لعبة حالية
                    return jsonify({
                        'success': True,
                        'game_id': player_info['game_id']
                    })
                elif player_id in waiting_list:
                    # اللاعب في قائمة الانتظار
                    return jsonify({
                        'success': True,
                        'in_waiting': True
                    })
        
        return jsonify({'success': False})
        
    except Exception as e:
        print(f"❌ خطأ في إعادة الاتصال: {e}")
        return jsonify({'success': False})

@app.route('/waiting')
def waiting_page():
    """صفحة الانتظار"""
    return render_template_string(html_waiting)

@app.route('/check_game', methods=['POST'])
def check_game():
    """التحقق من وجود لعبة للاعب"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'success': False, 'error': 'معرف اللاعب مطلوب'})
        
        with lock:
            if player_id not in players:
                return jsonify({'success': False, 'error': 'player_not_found'})
            
            player_info = players[player_id]
            player_info['last_seen'] = datetime.now().isoformat()
            
            if player_info.get('game_id'):
                return jsonify({
                    'success': True,
                    'game_id': player_info['game_id']
                })
        
        return jsonify({'success': True, 'waiting': True})
        
    except Exception as e:
        print(f"❌ خطأ في التحقق من اللعبة: {e}")
        return jsonify({'success': False, 'error': 'خطأ في الخادم'})

@app.route('/stats')
def get_stats():
    """إحصائيات الخادم"""
    with lock:
        waiting = len(waiting_list)
        active = len([g for g in games.values() if not g.get('winner') and not g.get('is_draw')])
    
    return jsonify({
        'waiting': waiting,
        'active_games': active
    })

@app.route('/cancel_wait', methods=['POST'])
def cancel_wait():
    """إلغاء الانتظار"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if player_id:
            with lock:
                if player_id in waiting_list:
                    waiting_list.remove(player_id)
                if player_id in players:
                    del players[player_id]
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ خطأ في إلغاء الانتظار: {e}")
        return jsonify({'success': False})

@app.route('/game/<game_id>')
def game_page(game_id):
    """صفحة اللعبة"""
    with lock:
        if game_id not in games:
            return "اللعبة غير موجودة", 404
        
        game = games[game_id]
        
        # الحصول على أسماء اللاعبين
        player1_name = players.get(game['player1_id'], {}).get('name', 'لاعب 1')
        player2_name = players.get(game['player2_id'], {}).get('name', 'لاعب 2')
        
        return render_template_string(
            html_game,
            game_id=game_id,
            player1_name=player1_name,
            player2_name=player2_name
        )

@app.route('/game_state/<game_id>', methods=['POST'])
def game_state(game_id):
    """الحصول على حالة اللعبة"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'success': False, 'error': 'معرف اللاعب مطلوب'}), 400
        
        with lock:
            if game_id not in games:
                return jsonify({'success': False, 'error': 'اللعبة غير موجودة'}), 404
            
            game = games[game_id]
            
            # التحقق من أن اللاعب في هذه اللعبة
            if player_id not in [game['player1_id'], game['player2_id']]:
                return jsonify({'success': False, 'error': 'لاعب غير مصرح'}), 403
            
            # تحديث وقت آخر رؤية للاعب
            if player_id in players:
                players[player_id]['last_seen'] = datetime.now().isoformat()
            
            # تحديد رمز اللاعب
            player_symbol = 'X' if player_id == game['player1_id'] else 'O'
            
            return jsonify({
                'success': True,
                'board': game['board'],
                'turn': game['turn'],
                'winner': game.get('winner'),
                'win_line': game.get('win_line'),
                'is_draw': game.get('is_draw', False),
                'player_symbol': player_symbol,
                'player1_id': game['player1_id'],
                'player2_id': game['player2_id']
            })
            
    except Exception as e:
        print(f"❌ خطأ في حالة اللعبة: {e}")
        return jsonify({'success': False, 'error': 'خطأ في الخادم'}), 500

@app.route('/move/<game_id>', methods=['POST'])
def make_move(game_id):
    """تنفيذ حركة في اللعبة"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        index = data.get('index')
        
        if not player_id or index is None:
            return jsonify({'success': False, 'error': 'بيانات غير مكتملة'}), 400
        
        if index < 0 or index > 8:
            return jsonify({'success': False, 'error': 'حركة غير صالحة'}), 400
        
        with lock:
            if game_id not in games:
                return jsonify({'success': False, 'error': 'اللعبة غير موجودة'}), 404
            
            game = games[game_id]
            
            # التحقق من أن اللاعب في هذه اللعبة
            if player_id not in [game['player1_id'], game['player2_id']]:
                return jsonify({'success': False, 'error': 'لاعب غير مصرح'}), 403
            
            # التحقق من أن اللعبة لم تنتهي
            if game.get('winner') or game.get('is_draw'):
                return jsonify({'success': False, 'error': 'اللعبة انتهت'}), 400
            
            # التحقق من أن الخلية فارغة
            if game['board'][index]:
                return jsonify({'success': False, 'error': 'الخلية مشغولة'}), 400
            
            # تحديد رمز اللاعب والتحقق من دوره
            player_symbol = 'X' if player_id == game['player1_id'] else 'O'
            if game['turn'] != player_symbol:
                return jsonify({'success': False, 'error': 'ليس دورك'}), 403
            
            # تنفيذ الحركة
            game['board'][index] = player_symbol
            
            # التحقق من الفوز
            win_line = check_winner(game['board'])
            if win_line:
                game['winner'] = player_symbol
                game['win_line'] = win_line
                
                # تحديث حالة اللاعبين
                players[game['player1_id']]['game_id'] = None
                players[game['player2_id']]['game_id'] = None
            
            # التحقق من التعادل
            elif "" not in game['board']:
                game['is_draw'] = True
                
                # تحديث حالة اللاعبين
                players[game['player1_id']]['game_id'] = None
                players[game['player2_id']]['game_id'] = None
            
            # تغيير الدور
            else:
                game['turn'] = 'O' if game['turn'] == 'X' else 'X'
            
            # تحديث وقت اللعبة
            game['last_update'] = datetime.now().isoformat()
            
            print(f"🎮 حركة في اللعبة {game_id}: {player_symbol} في المربع {index}")
            
            return jsonify({'success': True})
            
    except Exception as e:
        print(f"❌ خطأ في الحركة: {e}")
        return jsonify({'success': False, 'error': 'خطأ في الخادم'}), 500

@app.route('/quit/<game_id>', methods=['POST'])
def quit_game(game_id):
    """خروج لاعب من اللعبة"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'success': False, 'error': 'معرف اللاعب مطلوب'}), 400
        
        with lock:
            if game_id in games:
                game = games[game_id]
                
                # إذا كان اللاعب في هذه اللعبة
                if player_id in [game['player1_id'], game['player2_id']]:
                    # تعيين الفائز (اللاعب الآخر)
                    other_player_id = game['player2_id'] if player_id == game['player1_id'] else game['player1_id']
                    game['winner'] = 'O' if player_id == game['player1_id'] else 'X'
                    
                    # تحديث حالة اللاعبين
                    if player_id in players:
                        players[player_id]['game_id'] = None
                    if other_player_id in players:
                        players[other_player_id]['game_id'] = None
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ خطأ في الخروج: {e}")
        return jsonify({'success': False, 'error': 'خطأ في الخادم'}), 500

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """تحديث وقت آخر نشاط للاعب"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if player_id:
            with lock:
                if player_id in players:
                    players[player_id]['last_seen'] = datetime.now().isoformat()
        
        return jsonify({'success': True})
        
    except:
        return jsonify({'success': False})

@app.route('/check_player/<game_id>', methods=['POST'])
def check_player(game_id):
    """التحقق من وجود اللاعب في اللعبة"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'in_game': False}), 400
        
        with lock:
            if game_id not in games:
                return jsonify({'in_game': False}), 404
            
            game = games[game_id]
            in_game = player_id in [game['player1_id'], game['player2_id']]
            
            return jsonify({'in_game': in_game})
            
    except Exception as e:
        print(f"❌ خطأ في التحقق من اللاعب: {e}")
        return jsonify({'in_game': False}), 500

def check_winner(board):
    """التحقق من وجود فائز"""
    win_lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # صفوف
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # أعمدة
        [0, 4, 8], [2, 4, 6]              # أقطار
    ]
    
    for line in win_lines:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return line
    
    return None

def matchmaking_thread():
    """خيط للمطابقة التلقائية بين اللاعبين"""
    while True:
        try:
            with lock:
                # إذا كان هناك لاعبين منتظرين على الأقل
                if len(waiting_list) >= 2:
                    player1_id = waiting_list.pop(0)
                    player2_id = waiting_list.pop(0)
                    
                    # التحقق من أن اللاعبين ما زالوا نشطين
                    if player1_id not in players or player2_id not in players:
                        continue
                    
                    # إنشاء معرف للعبة
                    game_id = str(uuid.uuid4())[:6]
                    
                    # إنشاء اللعبة
                    games[game_id] = {
                        'player1_id': player1_id,
                        'player2_id': player2_id,
                        'board': [""] * 9,
                        'turn': 'X',
                        'winner': None,
                        'win_line': None,
                        'is_draw': False,
                        'created_at': datetime.now().isoformat(),
                        'last_update': datetime.now().isoformat()
                    }
                    
                    # تحديث حالة اللاعبين
                    players[player1_id]['game_id'] = game_id
                    players[player2_id]['game_id'] = game_id
                    
                    player1_name = players[player1_id]['name']
                    player2_name = players[player2_id]['name']
                    
                    print(f"🎮 لعبة جديدة: {player1_name} (X) vs {player2_name} (O) - ID: {game_id}")
                    
        except Exception as e:
            print(f"❌ خطأ في المطابقة: {e}")
        
        time.sleep(1)

def cleanup_thread():
    """خيط لتنظيف الموارد القديمة"""
    while True:
        try:
            current_time = datetime.now()
            
            with lock:
                # تنظيف اللاعبين غير النشطين
                inactive_players = []
                for player_id, info in list(players.items()):
                    try:
                        last_seen = datetime.fromisoformat(info['last_seen'])
                        if (current_time - last_seen).total_seconds() > 300:  # 5 دقائق
                            inactive_players.append(player_id)
                    except:
                        inactive_players.append(player_id)
                
                for player_id in inactive_players:
                    # إزالة من قائمة الانتظار
                    if player_id in waiting_list:
                        waiting_list.remove(player_id)
                    
                    # إذا كان في لعبة، إنهاء اللعبة
                    game_id = players[player_id].get('game_id')
                    if game_id and game_id in games:
                        game = games[game_id]
                        # تعيين الفائز (اللاعب الآخر)
                        other_player_id = game['player2_id'] if player_id == game['player1_id'] else game['player1_id']
                        game['winner'] = 'O' if player_id == game['player1_id'] else 'X'
                        
                        # تحديث حالة اللاعب الآخر
                        if other_player_id in players:
                            players[other_player_id]['game_id'] = None
                    
                    # حذف اللاعب
                    del players[player_id]
                
                # تنظيف الألعاب القديمة
                expired_games = []
                for game_id, game in list(games.items()):
                    try:
                        last_update = datetime.fromisoformat(game['last_update'])
                        if (current_time - last_update).total_seconds() > 3600:  # ساعة
                            expired_games.append(game_id)
                    except:
                        expired_games.append(game_id)
                
                for game_id in expired_games:
                    # تحديث حالة اللاعبين
                    game = games[game_id]
                    if game['player1_id'] in players:
                        players[game['player1_id']]['game_id'] = None
                    if game['player2_id'] in players:
                        players[game['player2_id']]['game_id'] = None
                    
                    # حذف اللعبة
                    del games[game_id]
            
            print(f"🧹 تم التنظيف: {len(players)} لاعب، {len(games)} لعبة")
            
        except Exception as e:
            print(f"❌ خطأ في التنظيف: {e}")
        
        time.sleep(60)  # كل دقيقة

@app.route('/server_status')
def server_status():
    """حالة الخادم"""
    with lock:
        total_players = len(players)
        waiting = len(waiting_list)
        active_games = len([g for g in games.values() if not g.get('winner') and not g.get('is_draw')])
    
    return jsonify({
        'status': 'online',
        'total_players': total_players,
        'waiting_players': waiting,
        'active_games': active_games,
        'server_time': datetime.now().isoformat()
    })

# بدء الخيوط
matchmaking_thread_instance = threading.Thread(target=matchmaking_thread, daemon=True)
cleanup_thread_instance = threading.Thread(target=cleanup_thread, daemon=True)

# بدء الخيوط فقط إذا لم تكن تعمل بالفعل
if not matchmaking_thread_instance.is_alive():
    matchmaking_thread_instance.start()

if not cleanup_thread_instance.is_alive():
    cleanup_thread_instance.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    print("=" * 60)
    print("\n✅ المميزات:")
    print("   ✓ يعمل على عدة أجهزة على نفس الشبكة")
    print("   ✓ لا مشاكل في الجلسات (Session)")
    print("   ✓ مطابقة تلقائية بين اللاعبين")
    print("   ✓ منع تداخل الأدوار (X لا يلعب دور O)")
    print("   ✓ واجهة مستخدم متطورة")
    print("\n🌐 معلومات الاتصال:")
    print(f"   📍 http://localhost:{port}")
    print("   📱 http://[عنوان IP جهازك]:" + str(port))
    print("\n🔗 للاتصال من أجهزة أخرى:")
    print("   1. تأكد أن جميع الأجهزة على نفس الشبكة")
    print("   2. افتح المتصفح في الجهاز الآخر")
    print("   3. اكتب: http://[IP-جهازك]:" + str(port))
    print("\n📊 للحصول على حالة الخادم:")
    print("   http://[IP-جهازك]:" + str(port) + "/server_status")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=port, debug=False)