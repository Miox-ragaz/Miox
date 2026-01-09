from flask import Flask, render_template_string

app = Flask(__name__)

# بيانات الموقع
SITE_DATA = {
    "company_name": "Moix",
    "app_name": "Mocat",
    "slogan": "تطبيق دردشة عملي",
    "year": "2024"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moix - تطبيق Mocat</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* إعادة الضبط */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            background: #f5f5f5;
            color: #333;
        }
        
        /* الشريط العلوي */
        .header {
            background: #1a73e8;
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo i {
            font-size: 1.5rem;
        }
        
        .logo h1 {
            font-size: 1.3rem;
        }
        
        .nav-buttons {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* المحتوى الرئيسي */
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        /* قسم الشركة */
        .company-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-title {
            color: #1a73e8;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* قسم التطبيق */
        .app-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .app-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 1.5rem;
        }
        
        .app-icon {
            background: #1a73e8;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
        }
        
        /* المميزات */
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .feature {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #1a73e8;
        }
        
        .feature i {
            color: #1a73e8;
            margin-bottom: 0.5rem;
        }
        
        /* زر التحميل */
        .download-section {
            text-align: center;
            padding: 2rem;
            background: #1a73e8;
            color: white;
            border-radius: 10px;
            margin: 2rem 0;
        }
        
        .download-btn {
            background: white;
            color: #1a73e8;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-top: 1rem;
            font-weight: bold;
        }
        
        .download-btn:hover {
            background: #f8f9fa;
        }
        
        /* الإعدادات */
        .settings-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .theme-options {
            display: flex;
            gap: 10px;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .theme-btn {
            padding: 8px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .theme-btn:hover {
            background: #f5f5f5;
        }
        
        .theme-btn.active {
            background: #1a73e8;
            color: white;
            border-color: #1a73e8;
        }
        
        /* التذييل */
        footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 3rem;
        }
        
        /* التجاوبية */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 10px;
            }
            
            .nav-buttons {
                width: 100%;
                justify-content: center;
            }
            
            .container {
                padding: 1rem;
            }
            
            .company-section,
            .app-section,
            .settings-section {
                padding: 1rem;
            }
            
            .features {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 480px) {
            .btn {
                padding: 6px 10px;
                font-size: 0.8rem;
            }
            
            .download-btn {
                padding: 10px 20px;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <!-- الشريط العلوي -->
    <header class="header">
        <div class="logo">
            <i class="fas fa-building"></i>
            <h1>{{ data.company_name }}</h1>
        </div>
        
        <div class="nav-buttons">
            <button class="btn" onclick="openSettings()">
                <i class="fas fa-cog"></i> إعدادات
            </button>
            <button class="btn" onclick="openAppInfo()">
                <i class="fas fa-info-circle"></i> عن التطبيق
            </button>
        </div>
    </header>

    <!-- المحتوى الرئيسي -->
    <div class="container">
        <!-- قسم الشركة -->
        <section class="company-section">
            <h2 class="section-title">
                <i class="fas fa-building"></i> عن شركة {{ data.company_name }}
            </h2>
            <p>
                نحن شركة صغيرة نطور تطبيقات مفيدة. نسعى لإنشاء أدوات تساعد الناس في التواصل.
            </p>
            <p style="margin-top: 1rem;">
                نعمل على تطوير {{ data.app_name }} كتطبيق دردشة بسيط وعملي.
            </p>
        </section>

        <!-- قسم التطبيق -->
        <section class="app-section">
            <div class="app-header">
                <div class="app-icon">
                    <i class="fas fa-comment"></i>
                </div>
                <div>
                    <h2 style="color: #1a73e8; font-size: 1.8rem;">{{ data.app_name }}</h2>
                    <p>{{ data.slogan }}</p>
                </div>
            </div>
            
            <h3 class="section-title">
                <i class="fas fa-star"></i> مميزات التطبيق
            </h3>
            
            <div class="features">
                <div class="feature">
                    <i class="fas fa-message"></i>
                    <h4>دردشة نصية</h4>
                    <p>إرسال واستقبال الرسائل النصية</p>
                </div>
                
                <div class="feature">
                    <i class="fas fa-user-group"></i>
                    <h4>مجموعات صغيرة</h4>
                    <p>إنشاء مجموعات دردشة للأصدقاء</p>
                </div>
                
                <div class="feature">
                    <i class="fas fa-image"></i>
                    <h4>مشاركة الصور</h4>
                    <p>إرسال الصور في المحادثات</p>
                </div>
                
                <div class="feature">
                    <i class="fas fa-lock"></i>
                    <h4>خصوصية أساسية</h4>
                    <p>حماية بسيطة للمحادثات</p>
                </div>
            </div>
            
            <div style="margin-top: 2rem;">
                <h3 class="section-title">
                    <i class="fas fa-book"></i> شرح التطبيق
                </h3>
                <p>
                    {{ data.app_name }} هو تطبيق دردشة يمكنك من:
                </p>
                <ul style="margin-top: 0.5rem; padding-right: 1.5rem;">
                    <li>التواصل مع أصدقائك عبر الرسائل</li>
                    <li>إنشاء مجموعات صغيرة للدردشة</li>
                    <li>مشاركة الصور والوسائط</li>
                    <li>تخزين سجل المحادثات</li>
                </ul>
            </div>
        </section>

        <!-- قسم التحميل -->
        <section class="download-section">
            <h3 style="margin-bottom: 1rem;">حمل التطبيق الآن</h3>
            <p>متوفر للتحميل المباشر</p>
            <button class="download-btn" onclick="downloadApp()">
                <i class="fas fa-download"></i> تحميل {{ data.app_name }}
            </button>
            <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
                الإصدار {{ data.version }}
            </p>
        </section>

        <!-- قسم الإعدادات -->
        <section class="settings-section" id="settingsSection" style="display: none;">
            <h2 class="section-title">
                <i class="fas fa-cog"></i> الإعدادات
            </h2>
            
            <div style="margin-bottom: 1.5rem;">
                <h4>تغيير الألوان</h4>
                <p style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">اختر لون الموقع:</p>
                <div class="theme-options">
                    <button class="theme-btn active" onclick="changeColor('#1a73e8')">
                        <i class="fas fa-circle" style="color: #1a73e8;"></i> أزرق
                    </button>
                    <button class="theme-btn" onclick="changeColor('#2ecc71')">
                        <i class="fas fa-circle" style="color: #2ecc71;"></i> أخضر
                    </button>
                    <button class="theme-btn" onclick="changeColor('#9b59b6')">
                        <i class="fas fa-circle" style="color: #9b59b6;"></i> بنفسجي
                    </button>
                    <button class="theme-btn" onclick="changeColor('#e74c3c')">
                        <i class="fas fa-circle" style="color: #e74c3c;"></i> أحمر
                    </button>
                </div>
            </div>
            
            <div>
                <h4>خيارات أخرى</h4>
                <div style="margin-top: 0.5rem;">
                    <button class="btn" style="background: #f5f5f5; color: #333; margin: 5px;" onclick="resetSettings()">
                        إعادة التعيين
                    </button>
                </div>
            </div>
        </section>
    </div>

    <!-- التذييل -->
    <footer>
        <p>&copy; {{ data.year }} {{ data.company_name }}</p>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">
            تطبيق {{ data.app_name }} - إصدار تجريبي
        </p>
    </footer>

    <script>
        // تغيير لون الموقع
        function changeColor(color) {
            // تحديث جميع العناصر ذات اللون الأزرق
            document.querySelectorAll('.header, .download-section').forEach(el => {
                el.style.backgroundColor = color;
            });
            
            document.querySelectorAll('.section-title, .app-icon, .feature i').forEach(el => {
                el.style.color = color;
            });
            
            document.querySelectorAll('.feature').forEach(el => {
                el.style.borderLeftColor = color;
            });
            
            // تحديث الأزرار النشطة
            document.querySelectorAll('.theme-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // حفظ في التخزين المحلي
            localStorage.setItem('site_color', color);
        }
        
        // فتح الإعدادات
        function openSettings() {
            const section = document.getElementById('settingsSection');
            if (section.style.display === 'none') {
                section.style.display = 'block';
                section.scrollIntoView({ behavior: 'smooth' });
            } else {
                section.style.display = 'none';
            }
        }
        
        // فتح معلومات التطبيق
        function openAppInfo() {
            alert('{{ data.app_name }}\n\nتطبيق دردشة مبسط\nالإصدار: {{ data.version }}\n\nميزات:\n- دردشة نصية\n- مجموعات صغيرة\n- مشاركة الصور\n- واجهة بسيطة');
        }
        
        // تحميل التطبيق (يفتح رابط)
        function downloadApp() {
            window.open('https://example.com/download/moix', '_blank');
        }
        
        // إعادة تعيين الإعدادات
        function resetSettings() {
            localStorage.removeItem('site_color');
            changeColor('#1a73e8');
            alert('تمت إعادة التعيين');
        }
        
        // عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            // تحميل اللون المحفوظ
            const savedColor = localStorage.getItem('site_color');
            if (savedColor) {
                changeColor(savedColor);
            }
            
            // إخفاء قسم الإعدادات
            document.getElementById('settingsSection').style.display = 'none';
            
            console.log('موقع {{ data.company_name }} - {{ data.app_name }} يعمل');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE,
        data=SITE_DATA
    )

if __name__ == '__main__':
    print("🌐 تشغيل موقع Moix لتطبيق Mocat...")
    print("📱 افتح: http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=3000)