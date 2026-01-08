from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

# ===== HTML Templates =====
html_main = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>واجهة التطبيق</title>
    <style>
        body { font-family: Arial; background: #f4f4f4; text-align: center; padding: 50px; }
        .box { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
        button { padding: 12px 20px; margin: 10px; font-size: 16px; cursor: pointer; border: none; border-radius: 6px; background: #007bff; color: white; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="box">
        <h1>مرحبًا بك في تطبيق التجربة</h1>
        <p>هذه الصفحة تعرض بيانات مختصرة عن التطبيق.</p>
        <ul>
            <li>إصدار: 1.0</li>
            <li>المطور: فريق تجريبي</li>
            <li>حالة الخادم: يعمل</li>
        </ul>
        <button onclick="window.location.href='/developer'">واجهة المطورين</button>
    </div>
</body>
</html>
"""

html_developer = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>واجهة المطورين</title>
    <style>
        body { font-family: Arial; background: #e8f0fe; text-align: center; padding: 50px; }
        .box { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
        button { padding: 12px 20px; margin: 10px; font-size: 16px; cursor: pointer; border: none; border-radius: 6px; background: #28a745; color: white; }
        button:hover { background: #1e7e34; }
        pre { text-align: left; background: #f4f4f4; padding: 15px; border-radius: 6px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="box">
        <h1>واجهة المطورين</h1>
        <p>هنا يمكنك رؤية بيانات التطبيق كاملة لتجربة المطور.</p>
        <pre>
- إصدار التطبيق: 1.0
- المطور: فريق تجريبي
- وصف: نسخة اختبارية للتجربة فقط
- بيانات النظام: تعمل على Flask
        </pre>
        <button onclick="window.location.href='/'">العودة للواجهة الرئيسية</button>
    </div>
</body>
</html>
"""

# ===== Routes =====
@app.route('/')
def main_page():
    return render_template_string(html_main)

@app.route('/developer')
def developer_page():
    return render_template_string(html_developer)

# ===== Run server =====
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)