"""
🎯 تطبيق مشاركة الملفات المتوافق مع:
• Pydroid 3 على Android
• GitHub Codespaces  
• Replit.com
• VS Code على الحاسوب
"""

import os
import json
import secrets
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file, abort, Response
from werkzeug.utils import secure_filename
from functools import wraps

# ============ التهيئة ============
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['ALLOWED_EXTENSIONS'] = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
    'mp4', 'mp3', 'wav', 'zip', 'rar', 'docx', 
    'xlsx', 'pptx', 'md', 'py', 'html', 'css', 'js'
}

# ============ قاعدة البيانات في الذاكرة ============
class FileSharingDB:
    def __init__(self):
        self.files = []
        self.users = {}
        self.global_chat = []
        self.notifications = []
        self.likes = {}
        self.file_id_counter = 1
        self.notification_id_counter = 1
        
    def add_file(self, file_data):
        file_data['id'] = f"file_{self.file_id_counter}"
        file_data['created_at'] = datetime.now().isoformat()
        file_data['downloads'] = 0
        file_data['likes'] = 0
        file_data['liked_by'] = []
        file_data['comments'] = []
        self.file_id_counter += 1
        self.files.insert(0, file_data)  # إضافة في البداية
        
        # إشعار للجميع
        self.add_notification(
            f"📁 {file_data['username']} رفع ملف جديد: {file_data['filename']}",
            "file_upload"
        )
        return file_data
    
    def add_notification(self, message, notif_type="info"):
        notif = {
            'id': f"notif_{self.notification_id_counter}",
            'message': message,
            'type': notif_type,
            'time': datetime.now().isoformat(),
            'read': False
        }
        self.notification_id_counter += 1
        self.notifications.insert(0, notif)
        
        # حفظ آخر 50 إشعار فقط
        if len(self.notifications) > 50:
            self.notifications = self.notifications[:50]
        return notif
    
    def like_file(self, file_id, username):
        for file in self.files:
            if file['id'] == file_id:
                if username not in file['liked_by']:
                    file['liked_by'].append(username)
                    file['likes'] += 1
                    
                    # إشعار للمالك
                    if username != file['username']:
                        self.add_notification(
                            f"❤️ {username} أعجب بملفك: {file['filename']}",
                            "like"
                        )
                    return True
        return False
    
    def get_user_files(self, username):
        return [f for f in self.files if f['username'] == username]
    
    def get_file(self, file_id):
        for file in self.files:
            if file['id'] == file_id:
                return file
        return None

db = FileSharingDB()

# ============ دوال مساعدة ============
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_icon(filename):
    icons = {
        'pdf': '📄', 'txt': '📝', 'doc': '📄', 'docx': '📄',
        'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️', 'gif': '🖼️',
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'mkv': '🎬',
        'mp3': '🎵', 'wav': '🎵', 'ogg': '🎵',
        'zip': '📦', 'rar': '📦', '7z': '📦',
        'py': '🐍', 'html': '🌐', 'css': '🎨', 'js': '⚡',
        'xlsx': '📊', 'pptx': '📊'
    }
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
    return icons.get(ext, '📁')

def get_user_avatar(username):
    if not username:
        return "?"
    return username[0].upper()

def get_user_color(username):
    colors = ['#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0', 
              '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51']
    if not username:
        return colors[0]
    hash_val = sum(ord(char) for char in username)
    return colors[hash_val % len(colors)]

def check_banned_words(text):
    banned = ['سيء', 'ممنوع', 'خطر', 'غير لائق', 'سيئ', 'قبيح']
    for word in banned:
        if word in text.lower():
            return True, f"كلمة '{word}' غير مسموحة"
    return False, ""

def format_time_ago(dt_str):
    dt = datetime.fromisoformat(dt_str)
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "الآن"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"قبل {minutes} دقيقة"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"قبل {hours} ساعة"
    else:
        days = diff.days
        return f"قبل {days} يوم"

# ============ SSE للإشعارات الحية ============
class ServerSentEvents:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()
    
    def add_client(self):
        queue = []
        with self.lock:
            self.clients.append(queue)
        return queue
    
    def remove_client(self, queue):
        with self.lock:
            if queue in self.clients:
                self.clients.remove(queue)
    
    def broadcast(self, data):
        with self.lock:
            for client in self.clients:
                client.append(data)

sse = ServerSentEvents()

def sse_stream():
    queue = sse.add_client()
    try:
        while True:
            if queue:
                data = queue.pop(0)
                yield f"data: {json.dumps(data)}\n\n"
            else:
                time.sleep(0.5)  # تقليل استهلاك CPU
    finally:
        sse.remove_client(queue)

# ============ Routes ============
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template_string(HTML_TEMPLATE, files=db.files[:50], notifications=db.notifications[:10])

@app.route('/api/events')
def events():
    """SSE stream للإشعارات الحية"""
    response = Response(sse_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

@app.route('/api/notifications')
def get_notifications():
    """الحصول على الإشعارات"""
    return jsonify({
        'notifications': db.notifications[:20],
        'unread': len([n for n in db.notifications if not n['read']])
    })

@app.route('/api/notifications/read', methods=['POST'])
def mark_notifications_read():
    """تحديد الإشعارات كمقروءة"""
    data = request.json
    notification_ids = data.get('ids', [])
    
    for notif in db.notifications:
        if notif['id'] in notification_ids:
            notif['read'] = True
    
    return jsonify({'success': True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """رفع ملف جديد"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'لم يتم اختيار ملف'}), 400
        
        file = request.files['file']
        username = request.form.get('username', '').strip() or 'مستخدم'
        description = request.form.get('description', '').strip()
        
        if not file or file.filename == '':
            return jsonify({'error': 'الرجاء اختيار ملف'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'نوع الملف غير مسموح'}), 400
        
        # التحقق من عدد ملفات المستخدم
        user_files = db.get_user_files(username)
        if len(user_files) >= 10:  # 10 ملفات كحد أقصى
            return jsonify({'error': 'تجاوزت الحد المسموح (10 ملفات لكل مستخدم)'}), 400
        
        # التحقق من حجم الملف
        if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'حجم الملف يتجاوز 50MB'}), 400
        
        # التحقق من الكلمات الممنوعة
        has_banned, message = check_banned_words(description)
        if has_banned:
            return jsonify({'error': message}), 400
        
        # حفظ الملف
        filename = secure_filename(file.filename)
        file_id = secrets.token_hex(8)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(filepath)
        
        # إضافة للمنصة
        file_data = {
            'id': file_id,
            'filename': filename,
            'original_name': filename,
            'username': username,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'size': os.path.getsize(filepath),
            'icon': get_file_icon(filename),
            'avatar': get_user_avatar(username),
            'color': get_user_color(username),
            'downloads': 0,
            'likes': 0,
            'liked_by': [],
            'comments': []
        }
        
        file_obj = db.add_file(file_data)
        
        # إرسال تحديث SSE
        sse.broadcast({
            'type': 'new_file',
            'file': file_obj,
            'time': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True, 
            'file': file_obj,
            'message': 'تم رفع الملف بنجاح!'
        })
    
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@app.route('/api/files')
def get_files():
    """الحصول على جميع الملفات"""
    return jsonify({
        'files': db.files[:100],
        'total': len(db.files)
    })

@app.route('/api/files/<file_id>')
def get_file(file_id):
    """الحصول على ملف معين"""
    file = db.get_file(file_id)
    if file:
        return jsonify(file)
    return jsonify({'error': 'الملف غير موجود'}), 404

@app.route('/api/download/<file_id>')
def download_file(file_id):
    """تنزيل ملف"""
    file = db.get_file(file_id)
    if not file:
        abort(404)
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{file['filename']}")
    
    if not os.path.exists(filepath):
        abort(404)
    
    # تحديث عدد التنزيلات
    file['downloads'] += 1
    
    # إشعار للمالك
    if file['downloads'] == 1:  # أول تنزيل فقط
        db.add_notification(
            f"⬇️ {file['filename']} تم تنزيله لأول مرة!",
            "download"
        )
    
    return send_file(filepath, as_attachment=True, download_name=file['original_name'])

@app.route('/api/like/<file_id>', methods=['POST'])
def like_file(file_id):
    """الإعجاب بملف"""
    data = request.json
    username = data.get('username', '').strip() or 'مستخدم'
    
    if db.like_file(file_id, username):
        file = db.get_file(file_id)
        
        # إرسال تحديث SSE
        sse.broadcast({
            'type': 'file_liked',
            'file_id': file_id,
            'username': username,
            'likes': file['likes'],
            'time': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'likes': file['likes'],
            'message': 'تم تسجيل إعجابك!'
        })
    
    return jsonify({'error': 'الملف غير موجود'}), 404

@app.route('/api/comment/<file_id>', methods=['POST'])
def add_comment(file_id):
    """إضافة تعليق على ملف"""
    data = request.json
    username = data.get('username', '').strip() or 'مستخدم'
    comment = data.get('comment', '').strip()
    
    if not comment:
        return jsonify({'error': 'التعليق فارغ'}), 400
    
    file = db.get_file(file_id)
    if not file:
        return jsonify({'error': 'الملف غير موجود'}), 404
    
    comment_data = {
        'id': secrets.token_hex(4),
        'username': username,
        'avatar': get_user_avatar(username),
        'color': get_user_color(username),
        'comment': comment,
        'timestamp': datetime.now().isoformat()
    }
    
    file['comments'].insert(0, comment_data)
    
    # إشعار للمالك
    if username != file['username']:
        db.add_notification(
            f"💬 {username} علق على ملفك: {file['filename'][:20]}...",
            "comment"
        )
    
    # إرسال تحديث SSE
    sse.broadcast({
        'type': 'new_comment',
        'file_id': file_id,
        'comment': comment_data,
        'time': datetime.now().isoformat()
    })
    
    return jsonify({'success': True, 'comment': comment_data})

@app.route('/api/stats/<username>')
def get_stats(username):
    """إحصائيات المستخدم"""
    user_files = db.get_user_files(username)
    total_size = sum(f['size'] for f in user_files)
    total_likes = sum(f['likes'] for f in user_files)
    total_comments = sum(len(f['comments']) for f in user_files)
    
    return jsonify({
        'username': username,
        'file_count': len(user_files),
        'max_files': 10,
        'total_size': total_size,
        'max_size': 50 * 1024 * 1024,
        'total_downloads': sum(f['downloads'] for f in user_files),
        'total_likes': total_likes,
        'total_comments': total_comments,
        'avatar': get_user_avatar(username),
        'color': get_user_color(username)
    })

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    """المحادثة العالمية"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip() or 'مستخدم'
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'الرسالة فارغة'}), 400
        
        chat_message = {
            'id': secrets.token_hex(4),
            'username': username,
            'avatar': get_user_avatar(username),
            'color': get_user_color(username),
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        db.global_chat.append(chat_message)
        
        # حفظ آخر 200 رسالة فقط
        if len(db.global_chat) > 200:
            db.global_chat = db.global_chat[-200:]
        
        # إرسال تحديث SSE
        sse.broadcast({
            'type': 'new_chat_message',
            'message': chat_message,
            'time': datetime.now().isoformat()
        })
        
        return jsonify({'success': True, 'message': chat_message})
    
    # GET: إرجاع آخر الرسائل
    return jsonify({
        'messages': db.global_chat[-50:],
        'total': len(db.global_chat)
    })

# ============ HTML Template ============
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📁 مشاركة الملفات - متوافق مع كل المنصات</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --accent: #f72585;
            --success: #2a9d8f;
            --warning: #e9c46a;
            --danger: #e63946;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --shadow: 0 4px 20px rgba(0,0,0,0.1);
            --radius: 12px;
            --transition: all 0.3s ease;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Cairo', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            padding-bottom: 100px;
            color: var(--dark);
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* الهيدر */
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: var(--shadow);
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: var(--primary);
            margin-bottom: 10px;
            font-size: 2.2rem;
        }
        
        .header p {
            color: var(--gray);
            font-size: 1rem;
        }
        
        /* شريط الإشعارات */
        .notifications-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: var(--warning);
            color: var(--dark);
            padding: 10px;
            text-align: center;
            z-index: 1000;
            display: none;
            animation: slideDown 0.3s ease-out;
        }
        
        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }
        
        /* إشعارات */
        .notifications-panel {
            position: fixed;
            top: 60px;
            left: 20px;
            right: 20px;
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 15px;
            z-index: 999;
            display: none;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .notification-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .notification-item.unread {
            background: #f0f8ff;
            border-right: 4px solid var(--primary);
        }
        
        .notification-icon {
            font-size: 1.2rem;
        }
        
        /* قائمة الملفات */
        .files-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .file-card {
            background: white;
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: var(--shadow);
            transition: var(--transition);
            animation: fadeInUp 0.6s ease-out;
            border: 1px solid #eee;
        }
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .user-avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 20px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }
        
        .user-details {
            flex: 1;
        }
        
        .user-name {
            font-weight: 700;
            color: var(--dark);
            font-size: 1.1rem;
        }
        
        .file-time {
            color: var(--gray);
            font-size: 0.85rem;
            margin-top: 3px;
        }
        
        .file-size {
            background: var(--light);
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            color: var(--gray);
        }
        
        .file-content {
            margin: 15px 0;
        }
        
        .file-name {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 10px;
        }
        
        .file-icon {
            font-size: 2rem;
        }
        
        .file-description {
            color: var(--gray);
            line-height: 1.6;
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            border-right: 3px solid var(--primary);
        }
        
        .file-stats {
            display: flex;
            gap: 15px;
            margin: 15px 0;
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .file-actions {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        
        .action-btn {
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: var(--transition);
            font-size: 0.9rem;
        }
        
        .action-btn i {
            font-size: 1.1rem;
        }
        
        .btn-download {
            background: var(--primary);
            color: white;
        }
        
        .btn-download:hover {
            background: var(--secondary);
        }
        
        .btn-like {
            background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
            color: white;
        }
        
        .btn-like:hover {
            background: linear-gradient(45deg, #ff5252, #ff7b7b);
        }
        
        .btn-like.liked {
            background: linear-gradient(45deg, #ff4757, #ff6b81);
        }
        
        .btn-comment {
            background: var(--success);
            color: white;
        }
        
        .btn-comment:hover {
            background: #23857a;
        }
        
        .btn-share {
            background: var(--accent);
            color: white;
        }
        
        .btn-share:hover {
            background: #e1156d;
        }
        
        /* زر الإضافة */
        .add-btn {
            position: fixed;
            bottom: 80px;
            right: 50%;
            transform: translateX(50%);
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 0 6px 25px rgba(67, 97, 238, 0.5);
            transition: var(--transition);
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .add-btn:hover {
            transform: translateX(50%) scale(1.1);
            box-shadow: 0 8px 30px rgba(67, 97, 238, 0.6);
        }
        
        /* البار السفلي */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-around;
            padding: 15px 10px;
            box-shadow: 0 -5px 25px rgba(0,0,0,0.1);
            z-index: 100;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .nav-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            background: none;
            border: none;
            color: var(--gray);
            font-size: 0.8rem;
            cursor: pointer;
            transition: var(--transition);
            padding: 10px 15px;
            border-radius: 15px;
            flex: 1;
            max-width: 100px;
        }
        
        .nav-btn:hover, .nav-btn.active {
            color: var(--primary);
            background: rgba(67, 97, 238, 0.1);
        }
        
        .nav-btn i {
            font-size: 1.4rem;
        }
        
        .notification-badge {
            position: absolute;
            top: 0;
            right: 20px;
            background: var(--danger);
            color: white;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            font-size: 0.7rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* المودال */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 20px;
        }
        
        .modal {
            background: white;
            border-radius: var(--radius);
            width: 100%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
            animation: modalSlide 0.3s ease-out;
        }
        
        @keyframes modalSlide {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .modal-header {
            padding: 20px;
            border-bottom: 2px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-body {
            padding: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--dark);
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: var(--transition);
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        
        .file-input-wrapper {
            position: relative;
            overflow: hidden;
            border-radius: 10px;
            border: 2px dashed #ccc;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: var(--transition);
        }
        
        .file-input-wrapper:hover {
            border-color: var(--primary);
            background: #f8f9ff;
        }
        
        .file-input-wrapper input {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        
        .modal-footer {
            padding: 20px;
            border-top: 2px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        
        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--secondary);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: var(--dark);
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        /* التعليقات */
        .comments-section {
            margin-top: 20px;
            border-top: 2px solid #f0f0f0;
            padding-top: 15px;
        }
        
        .comment {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .comment-avatar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .comment-content {
            flex: 1;
        }
        
        /* تحميل */
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--gray);
        }
        
        .loading i {
            font-size: 2rem;
            margin-bottom: 15px;
            color: var(--primary);
        }
        
        /* رسائل */
        .alert {
            padding: 12px 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: none;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .file-actions {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .file-header {
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }
            
            .file-size {
                align-self: flex-start;
            }
            
            .modal {
                width: 95%;
            }
            
            .add-btn {
                bottom: 70px;
                right: 20px;
                transform: none;
            }
        }
        
        /* Animation for new items */
        @keyframes highlight {
            0% { background-color: #e3f2fd; }
            100% { background-color: white; }
        }
        
        .highlight {
            animation: highlight 3s ease;
        }
    </style>
</head>
<body>
    <!-- شريط الإشعارات المباشرة -->
    <div class="notifications-bar" id="liveNotificationBar">
        <span id="liveNotificationText"></span>
        <button onclick="hideLiveNotification()" style="margin-right: 15px; background: none; border: none; color: inherit;">✕</button>
    </div>
    
    <!-- لوحة الإشعارات -->
    <div class="notifications-panel" id="notificationsPanel">
        <h3 style="margin-bottom: 15px; color: var(--primary);">
            <i class="fas fa-bell"></i> الإشعارات
        </h3>
        <div id="notificationsList">
            <!-- الإشعارات تظهر هنا -->
        </div>
    </div>
    
    <div class="container">
        <!-- الهيدر -->
        <div class="header">
            <h1><i class="fas fa-share-alt"></i> مشاركة الملفات</h1>
            <p>شارك ملفاتك مع الآخرين وتابع من يعجب بها!</p>
            <div style="margin-top: 10px;">
                <button onclick="toggleNotifications()" class="btn" style="background: var(--warning); color: var(--dark);">
                    <i class="fas fa-bell"></i>
                    <span id="notificationCount">0</span>
                </button>
            </div>
        </div>
        
        <!-- الملفات -->
        <div class="files-container" id="filesContainer">
            <!-- الملفات تظهر هنا -->
        </div>
        
        <!-- التحميل -->
        <div class="loading" id="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>جاري تحميل الملفات...</p>
        </div>
    </div>
    
    <!-- زر الإضافة -->
    <button class="add-btn" onclick="showUploadModal()" id="addButton">
        <i class="fas fa-plus"></i>
    </button>
    
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
        <button class="nav-btn" onclick="showUploadModal()">
            <i class="fas fa-upload"></i>
            <span>رفع</span>
        </button>
        <button class="nav-btn" onclick="showStatsModal()">
            <i class="fas fa-user"></i>
            <span>حسابي</span>
        </button>
        <button class="nav-btn" onclick="toggleNotifications()">
            <i class="fas fa-bell"></i>
            <span>إشعارات</span>
            <span class="notification-badge" id="navNotificationBadge" style="display: none;">0</span>
        </button>
    </div>
    
    <!-- مودال رفع الملف -->
    <div class="modal-overlay" id="uploadModal">
        <div class="modal">
            <div class="modal-header">
                <h2><i class="fas fa-cloud-upload-alt"></i> رفع ملف جديد</h2>
                <button onclick="hideUploadModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
            </div>
            <div class="modal-body">
                <form id="uploadForm">
                    <div class="form-group">
                        <label class="form-label">اسمك</label>
                        <input type="text" id="username" class="form-control" placeholder="أدخل اسمك" value="مستخدم" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">اختر الملف</label>
                        <div class="file-input-wrapper">
                            <input type="file" id="fileInput" class="form-control" required>
                            <div>
                                <i class="fas fa-cloud-upload-alt" style="font-size: 3rem; color: var(--primary); margin-bottom: 10px;"></i>
                                <p style="font-weight: bold;">انقر لاختيار ملف</p>
                                <p style="font-size: 0.9rem; color: var(--gray); margin-top: 5px;">
                                    الحد الأقصى: 50MB | 10 ملفات لكل مستخدم
                                </p>
                            </div>
                        </div>
                        <div id="fileName" style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 8px; display: none;"></div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">وصف الملف (اختياري)</label>
                        <textarea id="description" class="form-control" rows="3" placeholder="اكتب وصفًا للملف..."></textarea>
                    </div>
                    
                    <div class="alert alert-error" id="uploadError"></div>
                    <div class="alert alert-success" id="uploadSuccess"></div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="hideUploadModal()">إلغاء</button>
                <button type="button" class="btn btn-primary" onclick="uploadFile()" id="uploadBtn">
                    <i class="fas fa-upload"></i> رفع الملف
                </button>
            </div>
        </div>
    </div>
    
    <!-- مودال الإحصائيات -->
    <div class="modal-overlay" id="statsModal">
        <div class="modal">
            <div class="modal-header">
                <h2><i class="fas fa-chart-line"></i> إحصائياتي</h2>
                <button onclick="hideStatsModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
            </div>
            <div class="modal-body">
                <div id="statsContent">
                    <!-- الإحصائيات تظهر هنا -->
                </div>
            </div>
        </div>
    </div>
    
    <!-- مودال المحادثة -->
    <div class="modal-overlay" id="chatModal">
        <div class="modal">
            <div class="modal-header">
                <h2><i class="fas fa-comments"></i> المحادثة العالمية</h2>
                <button onclick="hideChatModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
            </div>
            <div class="modal-body" style="height: 400px; display: flex; flex-direction: column;">
                <div id="chatMessages" style="flex: 1; overflow-y: auto; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                    <!-- الرسائل تظهر هنا -->
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <input type="text" id="chatInput" class="form-control" placeholder="اكتب رسالة..." style="flex: 1;">
                    <button class="btn btn-primary" onclick="sendChatMessage()">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // الحالة العامة
        let currentUsername = 'مستخدم';
        let likedFiles = new Set();
        let eventSource = null;
        
        // تهيئة الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            // تحديث الاسم من localStorage
            const savedUsername = localStorage.getItem('fileShare_username');
            if (savedUsername) {
                currentUsername = savedUsername;
                document.getElementById('username').value = savedUsername;
            }
            
            // تحميل الملفات
            loadFiles();
            
            // بدء الاتصال بالإشعارات الحية
            connectToNotifications();
            
            // تحديث عدد الإشعارات
            updateNotificationCount();
            
            // تحديث الاسم عند التغيير
            document.getElementById('username').addEventListener('change', function() {
                currentUsername = this.value || 'مستخدم';
                localStorage.setItem('fileShare_username', currentUsername);
            });
            
            // إخفاء التحميل بعد 3 ثواني
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
            }, 3000);
        });
        
        // الاتصال بالإشعارات الحية (SSE)
        function connectToNotifications() {
            if (eventSource) eventSource.close();
            
            eventSource = new EventSource('/api/events');
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleLiveNotification(data);
            };
            
            eventSource.onerror = function() {
                console.log('SSE connection error, reconnecting...');
                setTimeout(connectToNotifications, 3000);
            };
        }
        
        // معالجة الإشعارات الحية
        function handleLiveNotification(data) {
            console.log('إشعار مباشر:', data);
            
            switch(data.type) {
                case 'new_file':
                    showLiveNotification(`📁 ${data.file.username} رفع ملف جديد: ${data.file.filename}`);
                    addFileToUI(data.file);
                    break;
                    
                case 'file_liked':
                    if (data.username !== currentUsername) {
                        showLiveNotification(`❤️ ${data.username} أعجب بملفك!`);
                    }
                    updateFileLikes(data.file_id, data.likes);
                    break;
                    
                case 'new_comment':
                    showLiveNotification(`💬 ${data.comment.username} علق على ملفك`);
                    break;
                    
                case 'new_chat_message':
                    // تحديث المحادثة إذا كانت مفتوحة
                    if (document.getElementById('chatModal').style.display === 'flex') {
                        addChatMessage(data.message);
                    }
                    break;
            }
            
            // تحديث عدد الإشعارات
            updateNotificationCount();
        }
        
        // عرض إشعار مباشر
        function showLiveNotification(message) {
            const bar = document.getElementById('liveNotificationBar');
            const text = document.getElementById('liveNotificationText');
            
            text.textContent = message;
            bar.style.display = 'block';
            
            // إخفاء تلقائي بعد 5 ثواني
            setTimeout(() => {
                bar.style.display = 'none';
            }, 5000);
        }
        
        function hideLiveNotification() {
            document.getElementById('liveNotificationBar').style.display = 'none';
        }
        
        // تحميل الملفات
        async function loadFiles() {
            try {
                const response = await fetch('/api/files');
                const data = await response.json();
                
                const container = document.getElementById('filesContainer');
                container.innerHTML = '';
                
                if (data.files.length === 0) {
                    container.innerHTML = `
                        <div class="file-card" style="text-align: center;">
                            <i class="fas fa-folder-open" style="font-size: 3rem; color: var(--gray); margin-bottom: 15px;"></i>
                            <h3 style="color: var(--gray);">لا توجد ملفات بعد</h3>
                            <p style="color: var(--gray);">كن أول من يرفع ملف!</p>
                            <button onclick="showUploadModal()" class="btn btn-primary" style="margin-top: 15px;">
                                <i class="fas fa-plus"></i> رفع ملف جديد
                            </button>
                        </div>
                    `;
                    return;
                }
                
                data.files.forEach(file => {
                    addFileToUI(file);
                });
                
                document.getElementById('loading').style.display = 'none';
                
            } catch (error) {
                console.error('خطأ في تحميل الملفات:', error);
                document.getElementById('loading').innerHTML = `
                    <i class="fas fa-exclamation-triangle" style="color: var(--danger);"></i>
                    <p>حدث خطأ في تحميل الملفات</p>
                    <button onclick="loadFiles()" class="btn btn-primary">إعادة المحاولة</button>
                `;
            }
        }
        
        // إضافة ملف للواجهة
        function addFileToUI(file) {
            const container = document.getElementById('filesContainer');
            const loading = document.getElementById('loading');
            
            if (loading.style.display !== 'none') {
                loading.style.display = 'none';
            }
            
            const timeAgo = formatTimeAgo(file.timestamp || file.created_at);
            const isLiked = likedFiles.has(file.id) || (file.liked_by && file.liked_by.includes(currentUsername));
            
            const fileCard = document.createElement('div');
            fileCard.className = 'file-card highlight';
            fileCard.id = `file-${file.id}`;
            fileCard.innerHTML = `
                <div class="file-header">
                    <div class="user-info">
                        <div class="user-avatar" style="background-color: ${file.color};">
                            ${file.avatar}
                        </div>
                        <div class="user-details">
                            <div class="user-name">${file.username}</div>
                            <div class="file-time">${timeAgo}</div>
                        </div>
                    </div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
                
                <div class="file-content">
                    <div class="file-name">
                        <span class="file-icon">${file.icon}</span>
                        <span>${file.filename}</span>
                    </div>
                    
                    ${file.description ? `
                    <div class="file-description">
                        ${file.description}
                    </div>
                    ` : ''}
                    
                    <div class="file-stats">
                        <div class="stat-item">
                            <i class="fas fa-download"></i>
                            <span>${file.downloads || 0}</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-heart"></i>
                            <span>${file.likes || 0}</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-comment"></i>
                            <span>${(file.comments || []).length}</span>
                        </div>
                    </div>
                </div>
                
                <div class="file-actions">
                    <button class="action-btn btn-download" onclick="downloadFile('${file.id}')">
                        <i class="fas fa-download"></i> تنزيل
                    </button>
                    <button class="action-btn btn-like ${isLiked ? 'liked' : ''}" onclick="likeFile('${file.id}')" id="like-btn-${file.id}">
                        <i class="fas fa-heart"></i> أعجبني
                    </button>
                    <button class="action-btn btn-comment" onclick="showComments('${file.id}')">
                        <i class="fas fa-comment"></i> تعليق
                    </button>
                    <button class="action-btn btn-share" onclick="shareFile('${file.id}')">
                        <i class="fas fa-share-alt"></i> مشاركة
                    </button>
                </div>
                
                ${(file.comments || []).length > 0 ? `
                <div class="comments-section" id="comments-${file.id}" style="display: none;">
                    <h4 style="margin-bottom: 10px;">التعليقات</h4>
                    ${(file.comments || []).slice(0, 3).map(comment => `
                        <div class="comment">
                            <div class="comment-avatar" style="background-color: ${comment.color};">
                                ${comment.avatar}
                            </div>
                            <div class="comment-content">
                                <strong>${comment.username}</strong>
                                <p>${comment.comment}</p>
                                <small>${formatTimeAgo(comment.timestamp)}</small>
                            </div>
                        </div>
                    `).join('')}
                    ${(file.comments || []).length > 3 ? `
                        <p style="text-align: center; color: var(--gray);">
                            + ${(file.comments || []).length - 3} تعليقات أخرى
                        </p>
                    ` : ''}
                    <div style="display: flex; gap: 10px; margin-top: 10px;">
                        <input type="text" id="comment-input-${file.id}" class="form-control" placeholder="اكتب تعليق...">
                        <button class="btn btn-primary" onclick="addComment('${file.id}')">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
                ` : ''}
            `;
            
            // إضافة في البداية
            container.insertBefore(fileCard, container.firstChild);
            
            // إزالة التأثير بعد 3 ثواني
            setTimeout(() => {
                fileCard.classList.remove('highlight');
            }, 3000);
        }
        
        // تحديث عدد الإعجابات
        function updateFileLikes(fileId, likes) {
            const likeBtn = document.getElementById(`like-btn-${fileId}`);
            if (likeBtn) {
                const heartIcon = likeBtn.querySelector('i');
                const countSpan = likeBtn.querySelector('span');
                
                if (countSpan) {
                    countSpan.textContent = likes;
                }
                
                // إذا كان المستخدم قد أعجب بهذا الملف
                if (likedFiles.has(fileId)) {
                    likeBtn.classList.add('liked');
                    heartIcon.className = 'fas fa-heart';
                }
            }
        }
        
        // رفع ملف
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const username = document.getElementById('username').value.trim() || 'مستخدم';
            const description = document.getElementById('description').value.trim();
            const uploadBtn = document.getElementById('uploadBtn');
            const errorDiv = document.getElementById('uploadError');
            const successDiv = document.getElementById('uploadSuccess');
            
            if (!fileInput.files.length) {
                showError('الرجاء اختيار ملف');
                return;
            }
            
            const file = fileInput.files[0];
            
            // التحقق من الحجم
            if (file.size > 50 * 1024 * 1024) {
                showError('حجم الملف يتجاوز 50MB');
                return;
            }
            
            // إعداد البيانات
            const formData = new FormData();
            formData.append('username', username);
            formData.append('description', description);
            formData.append('file', file);
            
            // عرض التحميل
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الرفع...';
            uploadBtn.disabled = true;
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                } else {
                    showSuccess(data.message || 'تم رفع الملف بنجاح!');
                    
                    // إعادة تعيين النموذج
                    fileInput.value = '';
                    document.getElementById('fileName').style.display = 'none';
                    document.getElementById('description').value = '';
                    
                    // إغلاق المودال بعد 2 ثانية
                    setTimeout(() => {
                        hideUploadModal();
                        successDiv.style.display = 'none';
                    }, 2000);
                }
                
            } catch (error) {
                showError('حدث خطأ أثناء الرفع');
            } finally {
                uploadBtn.innerHTML = '<i class="fas fa-upload"></i> رفع الملف';
                uploadBtn.disabled = false;
            }
            
            function showError(message) {
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
                successDiv.style.display = 'none';
            }
            
            function showSuccess(message) {
                successDiv.textContent = message;
                successDiv.style.display = 'block';
                errorDiv.style.display = 'none';
            }
        }
        
        // تنزيل ملف
        async function downloadFile(fileId) {
            try {
                const response = await fetch(`/api/download/${fileId}`);
                
                if (!response.ok) {
                    throw new Error('فشل التنزيل');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // الحصول على اسم الملف من الرأس
                const contentDisposition = response.headers.get('content-disposition');
                let filename = 'file';
                
                if (contentDisposition) {
                    const match = contentDisposition.match(/filename="?([^"]+)"?/);
                    if (match) filename = match[1];
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showLiveNotification('تم تنزيل الملف بنجاح!');
                
            } catch (error) {
                alert('حدث خطأ أثناء التنزيل: ' + error.message);
            }
        }
        
        // الإعجاب بملف
        async function likeFile(fileId) {
            const likeBtn = document.getElementById(`like-btn-${fileId}`);
            
            // منع النقر المزدوج
            if (likeBtn.disabled) return;
            
            likeBtn.disabled = true;
            
            try {
                const response = await fetch(`/api/like/${fileId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: currentUsername
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // تحديث الزر
                    likeBtn.classList.add('liked');
                    const heartIcon = likeBtn.querySelector('i');
                    heartIcon.className = 'fas fa-heart';
                    
                    // تحديث العدد
                    const countSpan = likeBtn.querySelector('span');
                    if (countSpan) {
                        countSpan.textContent = data.likes;
                    }
                    
                    // حفظ في الذاكرة
                    likedFiles.add(fileId);
                    
                    // إشعار محلي
                    if (data.message) {
                        showLiveNotification(data.message);
                    }
                }
                
            } catch (error) {
                console.error('خطأ في الإعجاب:', error);
            } finally {
                likeBtn.disabled = false;
            }
        }
        
        // إضافة تعليق
        async function addComment(fileId) {
            const input = document.getElementById(`comment-input-${fileId}`);
            const comment = input.value.trim();
            
            if (!comment) {
                alert('الرجاء كتابة تعليق');
                return;
            }
            
            try {
                const response = await fetch(`/api/comment/${fileId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: currentUsername,
                        comment: comment
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    input.value = '';
                    showLiveNotification('تم إضافة تعليقك!');
                    
                    // إظهار قسم التعليقات إذا كان مخفيًا
                    const commentsSection = document.getElementById(`comments-${fileId}`);
                    if (commentsSection) {
                        commentsSection.style.display = 'block';
                    }
                }
                
            } catch (error) {
                console.error('خطأ في إضافة التعليق:', error);
            }
        }
        
        // عرض التعليقات
        function showComments(fileId) {
            const commentsSection = document.getElementById(`comments-${fileId}`);
            if (commentsSection) {
                commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
            } else {
                alert('لا توجد تعليقات بعد. كن أول من يعلق!');
            }
        }
        
        // مشاركة ملف
        function shareFile(fileId) {
            const fileCard = document.getElementById(`file-${fileId}`);
            if (fileCard) {
                const fileTitle = fileCard.querySelector('.user-name').textContent + ' - ' + 
                                fileCard.querySelector('.file-name span:nth-child(2)').textContent;
                
                if (navigator.share) {
                    navigator.share({
                        title: fileTitle,
                        text: 'شاهد هذا الملف على تطبيق مشاركة الملفات',
                        url: window.location.href + '#file-' + fileId
                    });
                } else {
                    // نسخ الرابط
                    const link = window.location.href.split('#')[0] + '#file-' + fileId;
                    navigator.clipboard.writeText(link);
                    showLiveNotification('تم نسخ رابط الملف!');
                }
            }
        }
        
        // تحديث عدد الإشعارات
        async function updateNotificationCount() {
            try {
                const response = await fetch('/api/notifications');
                const data = await response.json();
                
                const count = data.unread || 0;
                document.getElementById('notificationCount').textContent = count;
                
                const badge = document.getElementById('navNotificationBadge');
                if (count > 0) {
                    badge.textContent = count > 9 ? '9+' : count;
                    badge.style.display = 'flex';
                } else {
                    badge.style.display = 'none';
                }
                
                // تحديث قائمة الإشعارات
                updateNotificationsList(data.notifications);
                
            } catch (error) {
                console.error('خطأ في تحميل الإشعارات:', error);
            }
        }
        
        // تحديث قائمة الإشعارات
        function updateNotificationsList(notifications) {
            const list = document.getElementById('notificationsList');
            
            if (!notifications || notifications.length === 0) {
                list.innerHTML = '<p style="text-align: center; color: var(--gray);">لا توجد إشعارات</p>';
                return;
            }
            
            list.innerHTML = notifications.map(notif => `
                <div class="notification-item ${notif.read ? '' : 'unread'}" data-id="${notif.id}">
                    <div class="notification-icon">
                        ${getNotificationIcon(notif.type)}
                    </div>
                    <div style="flex: 1;">
                        <div>${notif.message}</div>
                        <small style="color: var(--gray);">${formatTimeAgo(notif.time)}</small>
                    </div>
                </div>
            `).join('');
        }
        
        function getNotificationIcon(type) {
            const icons = {
                'file_upload': '📁',
                'like': '❤️',
                'comment': '💬',
                'download': '⬇️',
                'info': 'ℹ️'
            };
            return icons[type] || '🔔';
        }
        
        // تبديل عرض الإشعارات
        function toggleNotifications() {
            const panel = document.getElementById('notificationsPanel');
            panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
            
            // تحديث عند الفتح
            if (panel.style.display === 'block') {
                updateNotificationCount();
                markNotificationsAsRead();
            }
        }
        
        // تحديد الإشعارات كمقروءة
        async function markNotificationsAsRead() {
            try {
                // الحصول على الإشعارات غير المقروءة
                const response = await fetch('/api/notifications');
                const data = await response.json();
                
                const unreadIds = data.notifications
                    .filter(n => !n.read)
                    .map(n => n.id);
                
                if (unreadIds.length > 0) {
                    await fetch('/api/notifications/read', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            ids: unreadIds
                        })
                    });
                    
                    // تحديث العدد
                    updateNotificationCount();
                }
                
            } catch (error) {
                console.error('خطأ في تحديد الإشعارات كمقروءة:', error);
            }
        }
        
        // دوال المودال
        function showUploadModal() {
            document.getElementById('uploadModal').style.display = 'flex';
        }
        
        function hideUploadModal() {
            document.getElementById('uploadModal').style.display = 'none';
            document.getElementById('uploadError').style.display = 'none';
            document.getElementById('uploadSuccess').style.display = 'none';
        }
        
        function showStatsModal() {
            const modal = document.getElementById('statsModal');
            const content = document.getElementById('statsContent');
            
            // تحميل الإحصائيات
            fetch(`/api/stats/${currentUsername}`)
                .then(response => response.json())
                .then(data => {
                    content.innerHTML = `
                        <div style="text-align: center; margin-bottom: 20px;">
                            <div class="user-avatar" style="width: 80px; height: 80px; margin: 0 auto 15px; background-color: ${data.color}; font-size: 2rem;">
                                ${data.avatar}
                            </div>
                            <h3>${data.username}</h3>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 25px;">
                            <div style="background: #f8f9fa; padding: 15px; border-radius: var(--radius); text-align: center;">
                                <div style="font-size: 2rem; color: var(--primary); font-weight: bold;">${data.file_count}</div>
                                <div style="color: var(--gray);">ملف</div>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: var(--radius); text-align: center;">
                                <div style="font-size: 2rem; color: var(--success); font-weight: bold;">${data.total_downloads}</div>
                                <div style="color: var(--gray);">تنزيل</div>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: var(--radius); text-align: center;">
                                <div style="font-size: 2rem; color: var(--accent); font-weight: bold;">${data.total_likes}</div>
                                <div style="color: var(--gray);">إعجاب</div>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: var(--radius); text-align: center;">
                                <div style="font-size: 2rem; color: var(--warning); font-weight: bold;">${data.total_comments}</div>
                                <div style="color: var(--gray);">تعليق</div>
                            </div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; padding: 15px; border-radius: var(--radius); text-align: center;">
                            <div style="font-size: 1.2rem; margin-bottom: 5px;">المساحة المستخدمة</div>
                            <div style="font-size: 1.5rem; font-weight: bold;">
                                ${formatFileSize(data.total_size)} / 50MB
                            </div>
                            <div style="height: 10px; background: rgba(255,255,255,0.2); border-radius: 5px; margin-top: 10px; overflow: hidden;">
                                <div style="height: 100%; background: white; width: ${Math.min(100, (data.total_size / (50 * 1024 * 1024)) * 100)}%;"></div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; color: var(--gray); text-align: center;">
                            يمكنك رفع ${10 - data.file_count} ملفات أخرى
                        </div>
                    `;
                    
                    modal.style.display = 'flex';
                })
                .catch(error => {
                    content.innerHTML = `<p style="color: var(--danger); text-align: center;">حدث خطأ في تحميل الإحصائيات</p>`;
                    modal.style.display = 'flex';
                });
        }
        
        function hideStatsModal() {
            document.getElementById('statsModal').style.display = 'none';
        }
        
        function showChatModal() {
            const modal = document.getElementById('chatModal');
            modal.style.display = 'flex';
            
            // تحميل الرسائل
            loadChatMessages();
        }
        
        function hideChatModal() {
            document.getElementById('chatModal').style.display = 'none';
        }
        
        async function loadChatMessages() {
            try {
                const response = await fetch('/api/chat');
                const data = await response.json();
                
                const container = document.getElementById('chatMessages');
                container.innerHTML = '';
                
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        addChatMessage(msg);
                    });
                    
                    // التمرير للأسفل
                    container.scrollTop = container.scrollHeight;
                } else {
                    container.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 20px;">لا توجد رسائل بعد. كن أول من يرسل!</p>';
                }
                
            } catch (error) {
                console.error('خطأ في تحميل الرسائل:', error);
            }
        }
        
        function addChatMessage(msg) {
            const container = document.getElementById('chatMessages');
            const isCurrentUser = msg.username === currentUsername;
            
            const messageDiv = document.createElement('div');
            messageDiv.style.marginBottom = '10px';
            messageDiv.style.display = 'flex';
            messageDiv.style.flexDirection = isCurrentUser ? 'row-reverse' : 'row';
            messageDiv.style.alignItems = 'flex-start';
            messageDiv.style.gap = '10px';
            
            messageDiv.innerHTML = `
                <div class="user-avatar" style="width: 35px; height: 35px; flex-shrink: 0; background-color: ${msg.color};">
                    ${msg.avatar}
                </div>
                <div style="max-width: 70%;">
                    <div style="font-size: 0.8rem; color: var(--gray); margin-bottom: 3px; text-align: ${isCurrentUser ? 'right' : 'left'}">
                        ${msg.username} • ${formatTimeAgo(msg.timestamp)}
                    </div>
                    <div style="background: ${isCurrentUser ? 'var(--primary)' : '#e9ecef'}; 
                                color: ${isCurrentUser ? 'white' : 'var(--dark)'}; 
                                padding: 10px 15px; 
                                border-radius: 15px;
                                border-bottom-${isCurrentUser ? 'left' : 'right'}-radius: 5px;
                                word-break: break-word;
                                text-align: ${isCurrentUser ? 'right' : 'left'}">
                        ${msg.message}
                    </div>
                </div>
            `;
            
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: currentUsername,
                        message: message
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    input.value = '';
                    addChatMessage(data.message);
                }
                
            } catch (error) {
                console.error('خطأ في إرسال الرسالة:', error);
            }
        }
        
        // دوال المساعدة
        function formatTimeAgo(timestamp) {
            if (!timestamp) return 'قبل وقت';
            
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            
            const minute = 60 * 1000;
            const hour = 60 * minute;
            const day = 24 * hour;
            
            if (diff < minute) {
                return 'الآن';
            } else if (diff < hour) {
                const minutes = Math.floor(diff / minute);
                return `قبل ${minutes} دقيقة`;
            } else if (diff < day) {
                const hours = Math.floor(diff / hour);
                return `قبل ${hours} ساعة`;
            } else {
                const days = Math.floor(diff / day);
                return `قبل ${days} يوم`;
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes < 1024) return bytes + ' بايت';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' ك.ب';
            return (bytes / (1024 * 1024)).toFixed(1) + ' م.ب';
        }
        
        // عند اختيار ملف
        document.getElementById('fileInput').addEventListener('change', function() {
            const fileNameDiv = document.getElementById('fileName');
            
            if (this.files.length > 0) {
                const file = this.files[0];
                fileNameDiv.innerHTML = `
                    <strong><i class="fas fa-file"></i> ${file.name}</strong>
                    <div style="color: var(--gray); font-size: 0.9rem;">
                        ${formatFileSize(file.size)} • ${file.type || 'نوع غير معروف'}
                    </div>
                `;
                fileNameDiv.style.display = 'block';
            } else {
                fileNameDiv.style.display = 'none';
            }
        });
        
        // إغلاق النوافذ عند النقر خارجها
        window.addEventListener('click', function(event) {
            // إغلاق لوحة الإشعارات
            const panel = document.getElementById('notificationsPanel');
            if (panel.style.display === 'block' && !event.target.closest('.notifications-panel') && 
                !event.target.closest('.nav-btn') && !event.target.closest('#notificationCount')) {
                panel.style.display = 'none';
            }
            
            // إغلاق المودالات
            const modals = ['uploadModal', 'statsModal', 'chatModal'];
            modals.forEach(modalId => {
                const modal = document.getElementById(modalId);
                if (modal.style.display === 'flex' && event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
        
        // دعم الإدخال بالزر Enter في المحادثة
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    </script>
</body>
</html>
'''

# ============ تشغيل التطبيق ============
if __name__ == '__main__':
    # إنشاء مجلد التحميل
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"📁 تم إنشاء مجلد '{app.config['UPLOAD_FOLDER']}'")
    
    print("\n" + "="*60)
    print("🚀 تطبيق مشاركة الملفات يعمل على كل المنصات!")
    print("="*60)
    print("✅ متوافق مع: Pydroid 3 | GitHub | Replit | VS Code")
    print("✅ الإشعارات الحية: نعم (بدون SocketIO)")
    print("✅ الإعجابات: نعم")
    print("✅ المحادثة العالمية: نعم")
    print("✅ نظام الإشعارات: نعم")
    print("🌐 افتح المتصفح واذهب إلى: http://127.0.0.1:5000")
    print("="*60)
    
    # التشغيل
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)