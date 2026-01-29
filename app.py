import os
import json
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import eventlet
eventlet.monkey_patch()

# ============ التهيئة ============
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip', 'docx'}

socketio = SocketIO(app, cors_allowed_origins="*")

# ============ قاعدة البيانات في الذاكرة ============
users_files = {}  # {username: [file1, file2]}
files_db = []     # تخزين جميع الملفات
global_chat = []  # المحادثة العالمية

# الكلمات الممنوعة في الوصف
BANNED_WORDS = ['سيء', 'ممنوع', 'خطر', 'غير لائق']

# أيقونات الملفات
FILE_ICONS = {
    'pdf': '📄', 'txt': '📋', 'doc': '📄', 'docx': '📄',
    'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️', 'gif': '🖼️',
    'mp4': '🎬', 'avi': '🎬', 'mov': '🎬',
    'mp3': '🎵', 'wav': '🎵',
    'zip': '📦', 'rar': '📦'
}

# ============ دوال مساعدة ============
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_icon(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
    return FILE_ICONS.get(ext, '📄')

def check_banned_words(text):
    for word in BANNED_WORDS:
        if word in text.lower():
            return True, f"كلمة '{word}' غير مسموحة"
    return False, ""

def get_user_avatar(username):
    if username:
        return username[0].upper()
    return "?"

def get_user_color(username):
    colors = ['#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0']
    hash_val = sum(ord(char) for char in username) if username else 0
    return colors[hash_val % len(colors)]

# ============ Routes ============
@app.route('/')
def index():
    return render_template_string(TEMPLATE, files=files_db, chat_messages=global_chat[-10:])

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'لم يتم اختيار ملف'}), 400
        
        file = request.files['file']
        username = request.form.get('username', 'مجهول').strip()
        description = request.form.get('description', '').strip()
        
        if not username:
            return jsonify({'error': 'الرجاء إدخال الاسم'}), 400
        
        if not file or file.filename == '':
            return jsonify({'error': 'الرجاء اختيار ملف'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'نوع الملف غير مسموح'}), 400
        
        # التحقق من عدد ملفات المستخدم
        if username in users_files and len(users_files[username]) >= 5:
            return jsonify({'error': 'تجاوزت الحد المسموح (5 ملفات لكل مستخدم)'}), 400
        
        # التحقق من الكلمات الممنوعة
        has_banned, message = check_banned_words(description)
        if has_banned:
            return jsonify({'error': message}), 400
        
        # حفظ الملف
        filename = secure_filename(file.filename)
        file_id = secrets.token_hex(8)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(filepath)
        
        # حفظ بيانات الملف
        file_data = {
            'id': file_id,
            'filename': filename,
            'original_name': filename,
            'username': username,
            'description': description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': 'الآن',
            'size': os.path.getsize(filepath),
            'icon': get_file_icon(filename),
            'avatar': get_user_avatar(username),
            'color': get_user_color(username),
            'downloads': 0,
            'comments': []
        }
        
        # تحديث قواعد البيانات
        files_db.append(file_data)
        if username not in users_files:
            users_files[username] = []
        users_files[username].append(file_data)
        
        # إرسال تحديث للجميع
        socketio.emit('new_file', file_data, broadcast=True)
        
        return jsonify({'success': True, 'file': file_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    for file_data in files_db:
        if file_data['id'] == file_id:
            file_data['downloads'] += 1
            filename = file_data['filename']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            
            # تحديث للجميع
            socketio.emit('file_updated', file_data, broadcast=True)
            
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True, download_name=filename)
    
    abort(404)

@app.route('/api/files')
def get_files():
    return jsonify(files_db)

@app.route('/api/file/<file_id>')
def get_file(file_id):
    for file_data in files_db:
        if file_data['id'] == file_id:
            return jsonify(file_data)
    return jsonify({'error': 'الملف غير موجود'}), 404

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.json
        username = data.get('username', 'مجهول')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'الرسالة فارغة'}), 400
        
        chat_message = {
            'id': secrets.token_hex(4),
            'username': username,
            'avatar': get_user_avatar(username),
            'color': get_user_color(username),
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M')
        }
        
        global_chat.append(chat_message)
        
        # إرسال للجميع
        socketio.emit('new_message', chat_message, broadcast=True)
        
        return jsonify({'success': True})
    
    return jsonify(global_chat[-20:])

@app.route('/api/comment/<file_id>', methods=['POST'])
def add_comment(file_id):
    data = request.json
    username = data.get('username', 'مجهول')
    comment = data.get('comment', '').strip()
    
    if not comment:
        return jsonify({'error': 'التعليق فارغ'}), 400
    
    for file_data in files_db:
        if file_data['id'] == file_id:
            comment_data = {
                'id': secrets.token_hex(4),
                'username': username,
                'avatar': get_user_avatar(username),
                'color': get_user_color(username),
                'comment': comment,
                'timestamp': datetime.now().strftime('%H:%M')
            }
            
            file_data['comments'].append(comment_data)
            
            # تحديث للجميع
            socketio.emit('new_comment', {
                'file_id': file_id,
                'comment': comment_data
            }, broadcast=True)
            
            return jsonify({'success': True})
    
    return jsonify({'error': 'الملف غير موجود'}), 404

@app.route('/api/stats/<username>')
def get_stats(username):
    user_files = [f for f in files_db if f['username'] == username]
    total_size = sum(f['size'] for f in user_files)
    
    return jsonify({
        'file_count': len(user_files),
        'max_files': 5,
        'total_size': total_size,
        'max_size': 50 * 1024 * 1024,
        'comments_count': sum(len(f['comments']) for f in user_files)
    })

# ============ SocketIO Events ============
@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected successfully'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# ============ HTML Template ============
TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مشاركة الملفات</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            padding-bottom: 100px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        /* كروت الملفات */
        .files-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 100px;
        }
        
        .file-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }
        
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }
        
        .user-name {
            font-weight: bold;
            color: #333;
        }
        
        .time-ago {
            color: #888;
            font-size: 0.9rem;
        }
        
        .file-name {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #333;
        }
        
        .file-icon {
            font-size: 1.5rem;
        }
        
        .file-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.3s;
            font-size: 0.9rem;
        }
        
        .btn-download {
            background: #4361ee;
            color: white;
        }
        
        .btn-download:hover {
            background: #3a0ca3;
        }
        
        .btn-comments {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-comments:hover {
            background: #ddd;
        }
        
        .btn-description {
            background: #4cc9f0;
            color: white;
        }
        
        .btn-description:hover {
            background: #3a86ff;
        }
        
        .description-box {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-right: 4px solid #4cc9f0;
            display: none;
        }
        
        /* نافذة الرفع */
        .upload-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .upload-modal {
            background: white;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            padding: 30px;
            animation: modalSlide 0.3s ease-out;
        }
        
        @keyframes modalSlide {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .modal-header {
            text-align: center;
            margin-bottom: 25px;
        }
        
        .modal-header h2 {
            color: #4361ee;
            margin-bottom: 10px;
        }
        
        .steps {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .step {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            background: #ddd;
        }
        
        .step.active {
            background: #4361ee;
        }
        
        .step.completed {
            background: #2a9d8f;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #4361ee;
        }
        
        .file-input-wrapper {
            position: relative;
            overflow: hidden;
            display: inline-block;
            width: 100%;
        }
        
        .file-input-wrapper input[type=file] {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        
        .file-input-label {
            display: block;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            border: 2px dashed #ccc;
            transition: all 0.3s;
        }
        
        .file-input-label:hover {
            background: #e0e0e0;
            border-color: #4361ee;
        }
        
        .error-message {
            color: #e63946;
            background: #ffeaea;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }
        
        .success-message {
            color: #2a9d8f;
            background: #e8f4f3;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }
        
        .modal-buttons {
            display: flex;
            gap: 10px;
            margin-top: 25px;
        }
        
        .modal-buttons .btn {
            flex: 1;
        }
        
        .btn-primary {
            background: #4361ee;
            color: white;
        }
        
        .btn-primary:hover {
            background: #3a0ca3;
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #ddd;
        }
        
        /* البار السفلي */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            display: flex;
            justify-content: space-around;
            padding: 15px 0;
            box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.1);
            z-index: 100;
        }
        
        .nav-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            background: none;
            border: none;
            color: #888;
            font-size: 0.9rem;
            cursor: pointer;
            transition: color 0.3s;
            padding: 10px 20px;
            border-radius: 50px;
        }
        
        .nav-btn:hover {
            color: #4361ee;
            background: #f0f0f0;
        }
        
        .nav-btn.active {
            color: #4361ee;
            font-weight: bold;
        }
        
        .nav-btn i {
            font-size: 1.5rem;
        }
        
        /* نافذة المحادثة */
        .chat-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .chat-modal {
            background: white;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            height: 80vh;
            display: flex;
            flex-direction: column;
        }
        
        .chat-header {
            padding: 20px;
            border-bottom: 2px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            padding: 12px 15px;
            border-radius: 15px;
            max-width: 80%;
            position: relative;
        }
        
        .message.sent {
            background: #4361ee;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }
        
        .message.received {
            background: #f0f0f0;
            color: #333;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }
        
        .message-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
            font-size: 0.9rem;
        }
        
        .chat-input-area {
            padding: 15px;
            border-top: 2px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 1rem;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: #4361ee;
        }
        
        .btn-send {
            background: #4361ee;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn-send:hover {
            background: #3a0ca3;
        }
        
        /* التحميل */
        .loading {
            text-align: center;
            padding: 30px;
            color: #666;
        }
        
        /* رسائل النظام */
        .system-message {
            text-align: center;
            padding: 10px;
            background: #e8f4f3;
            color: #2a9d8f;
            border-radius: 10px;
            margin: 10px 0;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-share-alt"></i> مشاركة الملفات</h1>
            <p>شارك ملفاتك مع الآخرين بسهولة وأمان</p>
        </div>
        
        <div class="files-list" id="filesList">
            {% for file in files %}
            <div class="file-card" id="file-{{ file.id }}">
                <div class="file-header">
                    <div class="user-info">
                        <div class="user-avatar" style="background-color: {{ file.color }};">
                            {{ file.avatar }}
                        </div>
                        <div>
                            <div class="user-name">{{ file.username }}</div>
                            <div class="time-ago">{{ file.time_ago }}</div>
                        </div>
                    </div>
                    <div class="file-size">{{ (file.size / 1024 / 1024)|round(2) }} MB</div>
                </div>
                
                <div class="file-name">
                    <span class="file-icon">{{ file.icon }}</span>
                    <span>{{ file.filename }}</span>
                </div>
                
                <div class="file-actions">
                    <button class="btn btn-download" onclick="downloadFile('{{ file.id }}', '{{ file.filename }}')">
                        <i class="fas fa-download"></i> تنزيل ({{ file.downloads }})
                    </button>
                    <button class="btn btn-comments" onclick="showComments('{{ file.id }}')">
                        <i class="fas fa-comment"></i> تعليقات ({{ file.comments|length }})
                    </button>
                    <button class="btn btn-description" onclick="toggleDescription('{{ file.id }}')">
                        <i class="fas fa-info-circle"></i> وصف
                    </button>
                </div>
                
                <div class="description-box" id="desc-{{ file.id }}">
                    <p>{{ file.description }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="loading" id="loading" style="display: none;">
            <i class="fas fa-spinner fa-spin"></i> جاري التحميل...
        </div>
    </div>
    
    <!-- نافذة رفع الملف -->
    <div class="upload-overlay" id="uploadOverlay">
        <div class="upload-modal">
            <div class="modal-header">
                <h2><i class="fas fa-cloud-upload-alt"></i> رفع ملف جديد</h2>
                <p>شارك ملفك مع الآخرين</p>
            </div>
            
            <div class="steps">
                <div class="step active" id="step1">1</div>
                <div class="step" id="step2">2</div>
            </div>
            
            <div id="step1Content">
                <div class="form-group">
                    <label for="username"><i class="fas fa-user"></i> اسمك</label>
                    <input type="text" id="username" class="form-control" placeholder="أدخل اسمك" value="مستخدم">
                </div>
                
                <div class="form-group">
                    <label for="file"><i class="fas fa-file"></i> اختر الملف</label>
                    <div class="file-input-wrapper">
                        <input type="file" id="file" class="form-control" onchange="updateFileName()">
                        <div class="file-input-label" id="fileLabel">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <span>انقر لاختيار الملف</span>
                            <div style="font-size: 0.9rem; margin-top: 5px; color: #666;">
                                الحد الأقصى: 50MB | 5 ملفات لكل مستخدم
                            </div>
                        </div>
                    </div>
                    <div id="fileName" style="margin-top: 10px; color: #666;"></div>
                </div>
                
                <div class="error-message" id="step1Error"></div>
                
                <div class="modal-buttons">
                    <button class="btn btn-secondary" onclick="closeUploadModal()">إلغاء</button>
                    <button class="btn btn-primary" onclick="nextStep()">التالي <i class="fas fa-arrow-left"></i></button>
                </div>
            </div>
            
            <div id="step2Content" style="display: none;">
                <div class="form-group">
                    <label for="description"><i class="fas fa-edit"></i> وصف الملف</label>
                    <textarea id="description" class="form-control" rows="4" placeholder="اكتب وصفًا للملف..."></textarea>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">
                        تجنب الكلمات المخالفة للسياسة
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="file-info" style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                        <strong>ملخص الملف:</strong>
                        <div id="fileSummary"></div>
                    </div>
                </div>
                
                <div class="error-message" id="step2Error"></div>
                <div class="success-message" id="successMessage"></div>
                
                <div class="modal-buttons">
                    <button class="btn btn-secondary" onclick="prevStep()">رجوع <i class="fas fa-arrow-right"></i></button>
                    <button class="btn btn-primary" onclick="uploadFile()" id="uploadBtn">
                        <i class="fas fa-upload"></i> رفع الملف
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- نافذة المحادثة -->
    <div class="chat-overlay" id="chatOverlay">
        <div class="chat-modal">
            <div class="chat-header">
                <h2><i class="fas fa-comments"></i> المحادثة العالمية</h2>
                <button onclick="closeChatModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">✕</button>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                {% for msg in chat_messages %}
                <div class="message {% if msg.username == 'مستخدم' %}sent{% else %}received{% endif %}">
                    <div class="message-header">
                        <div class="user-avatar" style="width: 25px; height: 25px; font-size: 12px; background-color: {{ msg.color }};">
                            {{ msg.avatar }}
                        </div>
                        <strong>{{ msg.username }}</strong>
                        <span style="font-size: 0.8rem; opacity: 0.7;">{{ msg.timestamp }}</span>
                    </div>
                    <div>{{ msg.message }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="اكتب رسالة..." onkeypress="if(event.key == 'Enter') sendMessage()">
                <button class="btn-send" onclick="sendMessage()">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
    
    <!-- البار السفلي -->
    <div class="bottom-nav">
        <button class="nav-btn active" onclick="showHome()">
            <i class="fas fa-home"></i>
            <span>الرئيسية</span>
        </button>
        <button class="nav-btn" onclick="showChatModal()">
            <i class="fas fa-comments"></i>
            <span>المحادثة</span>
        </button>
        <button class="nav-btn" onclick="showUploadModal()" style="background: #4361ee; color: white; border-radius: 50%; width: 60px; height: 60px; margin-top: -20px; box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);">
            <i class="fas fa-plus" style="font-size: 1.8rem;"></i>
        </button>
        <button class="nav-btn" onclick="showStats()">
            <i class="fas fa-user"></i>
            <span>حسابي</span>
        </button>
    </div>
    
    <script>
        // SocketIO Connection
        const socket = io();
        
        // تحديثات الوقت
        function updateTimeAgo() {
            document.querySelectorAll('.time-ago').forEach(el => {
                // يمكن إضافة منطق حساب الوقت هنا
            });
        }
        
        // Socket Events
        socket.on('new_file', function(file) {
            addFileToUI(file);
        });
        
        socket.on('file_updated', function(file) {
            updateFileUI(file);
        });
        
        socket.on('new_message', function(message) {
            addMessageToUI(message);
        });
        
        socket.on('new_comment', function(data) {
            // يمكن إضافة تحديث التعليقات هنا
            console.log('تعليق جديد:', data);
        });
        
        socket.on('connected', function(data) {
            console.log('Connected to server');
        });
        
        // إضافة ملف جديد للواجهة
        function addFileToUI(file) {
            const filesList = document.getElementById('filesList');
            const loading = document.getElementById('loading');
            
            if (loading.style.display !== 'none') {
                loading.style.display = 'none';
            }
            
            const fileCard = document.createElement('div');
            fileCard.className = 'file-card';
            fileCard.id = 'file-' + file.id;
            fileCard.innerHTML = `
                <div class="file-header">
                    <div class="user-info">
                        <div class="user-avatar" style="background-color: ${file.color};">
                            ${file.avatar}
                        </div>
                        <div>
                            <div class="user-name">${file.username}</div>
                            <div class="time-ago">${file.time_ago}</div>
                        </div>
                    </div>
                    <div class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                </div>
                
                <div class="file-name">
                    <span class="file-icon">${file.icon}</span>
                    <span>${file.filename}</span>
                </div>
                
                <div class="file-actions">
                    <button class="btn btn-download" onclick="downloadFile('${file.id}', '${file.filename}')">
                        <i class="fas fa-download"></i> تنزيل (0)
                    </button>
                    <button class="btn btn-comments" onclick="showComments('${file.id}')">
                        <i class="fas fa-comment"></i> تعليقات (0)
                    </button>
                    <button class="btn btn-description" onclick="toggleDescription('${file.id}')">
                        <i class="fas fa-info-circle"></i> وصف
                    </button>
                </div>
                
                <div class="description-box" id="desc-${file.id}" style="display: none;">
                    <p>${file.description}</p>
                </div>
            `;
            
            filesList.insertBefore(fileCard, filesList.firstChild);
            
            // رسالة نظام
            showSystemMessage(`تم رفع ملف جديد: ${file.filename}`);
        }
        
        // تحديث ملف في الواجهة
        function updateFileUI(file) {
            const fileCard = document.getElementById('file-' + file.id);
            if (fileCard) {
                const downloadBtn = fileCard.querySelector('.btn-download');
                if (downloadBtn) {
                    downloadBtn.innerHTML = `<i class="fas fa-download"></i> تنزيل (${file.downloads})`;
                }
                
                const commentsBtn = fileCard.querySelector('.btn-comments');
                if (commentsBtn) {
                    commentsBtn.innerHTML = `<i class="fas fa-comment"></i> تعليقات (${file.comments.length})`;
                }
            }
        }
        
        // إضافة رسالة للواجهة
        function addMessageToUI(message) {
            const chatMessages = document.getElementById('chatMessages');
            const isCurrentUser = message.username === document.getElementById('username').value;
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isCurrentUser ? 'sent' : 'received'}`;
            messageDiv.innerHTML = `
                <div class="message-header">
                    <div class="user-avatar" style="width: 25px; height: 25px; font-size: 12px; background-color: ${message.color};">
                        ${message.avatar}
                    </div>
                    <strong>${message.username}</strong>
                    <span style="font-size: 0.8rem; opacity: 0.7;">${message.timestamp}</span>
                </div>
                <div>${message.message}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // نافذة الرفع
        let currentStep = 1;
        let selectedFile = null;
        
        function showUploadModal() {
            document.getElementById('uploadOverlay').style.display = 'flex';
            resetUploadForm();
        }
        
        function closeUploadModal() {
            document.getElementById('uploadOverlay').style.display = 'none';
            resetUploadForm();
        }
        
        function resetUploadForm() {
            currentStep = 1;
            selectedFile = null;
            document.getElementById('step1').className = 'step active';
            document.getElementById('step2').className = 'step';
            document.getElementById('step1Content').style.display = 'block';
            document.getElementById('step2Content').style.display = 'none';
            document.getElementById('step1Error').style.display = 'none';
            document.getElementById('step2Error').style.display = 'none';
            document.getElementById('successMessage').style.display = 'none';
            document.getElementById('fileName').innerHTML = '';
            document.getElementById('file').value = '';
            document.getElementById('description').value = '';
        }
        
        function updateFileName() {
            const fileInput = document.getElementById('file');
            const fileNameDiv = document.getElementById('fileName');
            
            if (fileInput.files.length > 0) {
                selectedFile = fileInput.files[0];
                fileNameDiv.innerHTML = `<i class="fas fa-check-circle" style="color: #2a9d8f;"></i> ${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(2)} MB)`;
            }
        }
        
        function nextStep() {
            const username = document.getElementById('username').value.trim();
            const fileInput = document.getElementById('file');
            const errorDiv = document.getElementById('step1Error');
            
            if (!username) {
                errorDiv.textContent = 'الرجاء إدخال اسمك';
                errorDiv.style.display = 'block';
                return;
            }
            
            if (!fileInput.files.length) {
                errorDiv.textContent = 'الرجاء اختيار ملف';
                errorDiv.style.display = 'block';
                return;
            }
            
            selectedFile = fileInput.files[0];
            
            // التحقق من الحجم
            if (selectedFile.size > 50 * 1024 * 1024) {
                errorDiv.textContent = 'حجم الملف يتجاوز 50MB';
                errorDiv.style.display = 'block';
                return;
            }
            
            errorDiv.style.display = 'none';
            
            // الانتقال للخطوة 2
            currentStep = 2;
            document.getElementById('step1').className = 'step completed';
            document.getElementById('step2').className = 'step active';
            document.getElementById('step1Content').style.display = 'none';
            document.getElementById('step2Content').style.display = 'block';
            
            // عرض ملخص الملف
            document.getElementById('fileSummary').innerHTML = `
                <div>الاسم: ${selectedFile.name}</div>
                <div>الحجم: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB</div>
                <div>المستخدم: ${username}</div>
            `;
        }
        
        function prevStep() {
            currentStep = 1;
            document.getElementById('step1').className = 'step active';
            document.getElementById('step2').className = 'step';
            document.getElementById('step1Content').style.display = 'block';
            document.getElementById('step2Content').style.display = 'none';
            document.getElementById('step2Error').style.display = 'none';
        }
        
        function uploadFile() {
            const username = document.getElementById('username').value.trim();
            const description = document.getElementById('description').value.trim();
            const errorDiv = document.getElementById('step2Error');
            const successDiv = document.getElementById('successMessage');
            const uploadBtn = document.getElementById('uploadBtn');
            
            // التحقق من الوصف
            if (!description) {
                errorDiv.textContent = 'الرجاء إدخال وصف للملف';
                errorDiv.style.display = 'block';
                return;
            }
            
            // إرسال الملف
            const formData = new FormData();
            formData.append('username', username);
            formData.append('description', description);
            formData.append('file', selectedFile);
            
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الرفع...';
            uploadBtn.disabled = true;
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    errorDiv.textContent = data.error;
                    errorDiv.style.display = 'block';
                    successDiv.style.display = 'none';
                } else {
                    errorDiv.style.display = 'none';
                    successDiv.textContent = '✓ تم رفع الملف بنجاح!';
                    successDiv.style.display = 'block';
                    
                    setTimeout(() => {
                        closeUploadModal();
                        successDiv.style.display = 'none';
                    }, 2000);
                }
                uploadBtn.innerHTML = '<i class="fas fa-upload"></i> رفع الملف';
                uploadBtn.disabled = false;
            })
            .catch(error => {
                errorDiv.textContent = 'حدث خطأ أثناء الرفع';
                errorDiv.style.display = 'block';
                uploadBtn.innerHTML = '<i class="fas fa-upload"></i> رفع الملف';
                uploadBtn.disabled = false;
            });
        }
        
        // نافذة المحادثة
        function showChatModal() {
            document.getElementById('chatOverlay').style.display = 'flex';
            document.getElementById('chatInput').focus();
        }
        
        function closeChatModal() {
            document.getElementById('chatOverlay').style.display = 'none';
        }
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const username = document.getElementById('username').value.trim() || 'مستخدم';
            const message = input.value.trim();
            
            if (!message) return;
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    message: message
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    input.value = '';
                }
            });
        }
        
        // التنزيل والتعليقات
        function downloadFile(fileId, filename) {
            fetch(`/download/${fileId}`)
                .then(response => {
                    if (response.ok) {
                        return response.blob();
                    }
                    throw new Error('فشل التنزيل');
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    showSystemMessage(`تم تنزيل الملف: ${filename}`);
                })
                .catch(error => {
                    alert('حدث خطأ أثناء التنزيل: ' + error.message);
                });
        }
        
        function toggleDescription(fileId) {
            const desc = document.getElementById('desc-' + fileId);
            if (desc.style.display === 'none' || desc.style.display === '') {
                desc.style.display = 'block';
            } else {
                desc.style.display = 'none';
            }
        }
        
        function showComments(fileId) {
            alert('ميزة التعليقات قيد التطوير. سيتم إضافتها قريبًا!');
        }
        
        function showHome() {
            // تحديث القائمة
            window.location.reload();
        }
        
        function showStats() {
            const username = document.getElementById('username').value.trim() || 'مستخدم';
            fetch(`/api/stats/${username}`)
                .then(response => response.json())
                .then(data => {
                    alert(`إحصائيات ${username}:
                    
• الملفات المرفوعة: ${data.file_count}/${data.max_files}
• المساحة المستخدمة: ${(data.total_size / 1024 / 1024).toFixed(2)}MB/${data.max_size / 1024 / 1024}MB
• التعليقات المكتوبة: ${data.comments_count}
                    
يمكنك رفع ${data.max_files - data.file_count} ملفات أخرى.`);
                });
        }
        
        function showSystemMessage(message) {
            const filesList = document.getElementById('filesList');
            const systemMsg = document.createElement('div');
            systemMsg.className = 'system-message';
            systemMsg.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
            filesList.insertBefore(systemMsg, filesList.firstChild);
            
            setTimeout(() => {
                systemMsg.remove();
            }, 5000);
        }
        
        // تحميل الملفات عند بدء التشغيل
        window.onload = function() {
            fetch('/api/files')
                .then(response => response.json())
                .then(files => {
                    const loading = document.getElementById('loading');
                    if (loading) loading.style.display = 'none';
                });
        };
    </script>
</body>
</html>
'''

# ============ تشغيل التطبيق ============
if __name__ == '__main__':
    # إنشاء مجلد التحميل إذا لم يكن موجودًا
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"تم إنشاء مجلد '{app.config['UPLOAD_FOLDER']}'")
    
    print("\n" + "="*50)
    print("🚀 تطبيق مشاركة الملفات يعمل!")
    print("="*50)
    print(f"🌐 افتح المتصفح واذهب إلى: http://localhost:5000")
    print(f"📁 مجلد التحميل: {app.config['UPLOAD_FOLDER']}")
    print(f"⚡ SocketIO يعمل على نفس المنفذ")
    print("="*50 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)