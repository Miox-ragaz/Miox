from flask import Flask, render_template_string
import datetime

app = Flask(__name__)

# بيانات الموقع
SITE_DATA = {
    "app_name": "Moix",
    "tagline": "منصة دردشة آمنة ومتقدمة للمستقبل",
    "version": "1.0.0",
    "release_date": "ديسمبر 2024",
    "company": "Moix Technologies",
    "base_color": "#1a365d",  # أزرق داكن رسمي
    "accent_color": "#2d6a4f",  # أخضر احترافي
}

# أقسام الموقع
SECTIONS = [
    {
        "id": "hero",
        "title": "Moix - ثورة في عالم الاتصال",
        "content": "منصة دردشة مبتكرة تجمع بين السرعة التامة والأمان المتقدم، مصممة خصيصاً لتلبية احتياجات الاتصال في العصر الرقمي.",
        "icon": "fas fa-comments"
    },
    {
        "id": "features",
        "title": "مميزات التطبيق",
        "content": "يدعم Moix مجموعة واسعة من المميزات المتقدمة التي تضمن تجربة مستخدم استثنائية.",
        "icon": "fas fa-star"
    },
    {
        "id": "security",
        "title": "الأمان والخصوصية",
        "content": "نضع أمان بياناتك في مقدمة أولوياتنا بتقنيات تشفير متطورة.",
        "icon": "fas fa-shield-alt"
    },
    {
        "id": "about",
        "title": "عن Moix",
        "content": "منصة تطويرية تهدف إلى إعادة تعريف طرق التواصل الرقمي.",
        "icon": "fas fa-info-circle"
    }
]

# المميزات
FEATURES = [
    {"title": "دردشة فورية", "desc": "تواصل فوري بدون تأخير", "icon": "fas fa-bolt"},
    {"title": "تشكيل مجموعات", "desc": "إنشاء مجموعات بلا حدود", "icon": "fas fa-users"},
    {"title": "مشاركة الملفات", "desc": "مشاركة آمنة للصور والملفات", "icon": "fas fa-file-upload"},
    {"title": "مكالمات صوتية", "desc": "جودة صوت عالية الوضوح", "icon": "fas fa-phone-alt"},
    {"title": "تشفير End-to-End", "desc": "حماية كاملة للمحادثات", "icon": "fas fa-lock"},
    {"title": "واجهة متعددة اللغات", "desc": "دعم للغة العربية والإنجليزية", "icon": "fas fa-globe"},
]

# المطورون (بيانات عامة)
DEVELOPERS = [
    {"name": "فريق التطوير", "role": "مطورون رئيسيون", "icon": "fas fa-code"},
    {"name": "فريق التصميم", "role": "مصممون واجهات", "icon": "fas fa-palette"},
    {"name": "فريق الجودة", "role": "اختبار وضمان جودة", "icon": "fas fa-check-circle"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.app_name }} - منصة الدردشة المتقدمة</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: {{ data.base_color }};
            --secondary-color: {{ data.accent_color }};
            --light-bg: #f8fafc;
            --dark-bg: #0f172a;
            --light-text: #1e293b;
            --dark-text: #f1f5f9;
            --card-bg-light: #ffffff;
            --card-bg-dark: #1e293b;
            --shadow-light: 0 4px 20px rgba(0, 0, 0, 0.08);
            --shadow-dark: 0 4px 20px rgba(0, 0, 0, 0.3);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Cairo', sans-serif;
            line-height: 1.6;
            transition: var(--transition);
        }

        body.light-mode {
            background-color: var(--light-bg);
            color: var(--light-text);
        }

        body.dark-mode {
            background-color: var(--dark-bg);
            color: var(--dark-text);
        }

        /* الشريط العلوي */
        .top-bar {
            background: linear-gradient(135deg, var(--primary-color), #2c5282);
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo {
            font-size: 2rem;
            background: rgba(255, 255, 255, 0.1);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }

        .logo-text h1 {
            font-size: 1.8rem;
            margin-bottom: 5px;
        }

        .logo-text p {
            opacity: 0.9;
            font-size: 0.9rem;
        }

        /* أزرار التحكم */
        .controls {
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .mode-toggle, .settings-btn, .publish-btn {
            background: rgba(255, 255, 255, 0.15);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Cairo', sans-serif;
            font-size: 0.9rem;
            transition: var(--transition);
        }

        .mode-toggle:hover, .settings-btn:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }

        .publish-btn {
            background: var(--secondary-color);
            font-weight: bold;
        }

        .publish-btn:hover {
            background: #1b4332;
            transform: translateY(-2px);
        }

        .publish-btn.published {
            background: #38a169;
        }

        /* المحتوى الرئيسي */
        .container {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }

        /* القسم البطولي */
        .hero-section {
            text-align: center;
            padding: 60px 20px;
            margin-bottom: 40px;
            border-radius: 20px;
            box-shadow: var(--shadow-light);
            transition: var(--transition);
        }

        .light-mode .hero-section {
            background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
        }

        .dark-mode .hero-section {
            background: linear-gradient(135deg, #1e3a8a, #3730a3);
        }

        .hero-title {
            font-size: 2.8rem;
            margin-bottom: 20px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .hero-description {
            font-size: 1.2rem;
            max-width: 800px;
            margin: 0 auto 30px;
            opacity: 0.9;
        }

        /* الكروت */
        .card {
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            transition: var(--transition);
            box-shadow: var(--shadow-light);
        }

        .light-mode .card {
            background: var(--card-bg-light);
        }

        .dark-mode .card {
            background: var(--card-bg-dark);
            box-shadow: var(--shadow-dark);
        }

        .card-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--secondary-color);
        }

        /* المميزات */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }

        .feature-card {
            padding: 25px;
            border-radius: 12px;
            transition: var(--transition);
            border: 1px solid transparent;
        }

        .light-mode .feature-card {
            background: white;
            border-color: #e2e8f0;
        }

        .dark-mode .feature-card {
            background: rgba(255, 255, 255, 0.05);
            border-color: #334155;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 15px;
            color: var(--secondary-color);
        }

        /* المطورون */
        .developers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }

        .developer-card {
            text-align: center;
            padding: 25px;
            border-radius: 12px;
            transition: var(--transition);
        }

        .light-mode .developer-card {
            background: #f1f5f9;
        }

        .dark-mode .developer-card {
            background: rgba(255, 255, 255, 0.05);
        }

        .dev-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            color: var(--secondary-color);
        }

        /* منطقة الصورة */
        .image-section {
            text-align: center;
            margin: 40px 0;
            padding: 30px;
            border-radius: 15px;
        }

        .light-mode .image-section {
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
        }

        .dark-mode .image-section {
            background: rgba(255, 255, 255, 0.05);
            border: 2px dashed #475569;
        }

        .app-image {
            max-width: 400px;
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 10px;
            margin: 20px auto;
            border: 3px solid var(--secondary-color);
            display: none; /* مخفي حتى تضيف الصورة */
        }

        .image-placeholder {
            width: 400px;
            height: 250px;
            margin: 20px auto;
            background: linear-gradient(45deg, #e2e8f0, #cbd5e1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #64748b;
            border: 2px dashed #94a3b8;
        }

        .dark-mode .image-placeholder {
            background: linear-gradient(45deg, #334155, #475569);
            color: #cbd5e1;
            border-color: #64748b;
        }

        /* التذييل */
        footer {
            text-align: center;
            padding: 30px;
            margin-top: 50px;
            border-top: 1px solid;
            transition: var(--transition);
        }

        .light-mode footer {
            border-color: #e2e8f0;
            background: #f8fafc;
        }

        .dark-mode footer {
            border-color: #334155;
            background: rgba(0, 0, 0, 0.2);
        }

        .version-info {
            opacity: 0.8;
            font-size: 0.9rem;
            margin-top: 15px;
        }

        /* إشعار النشر */
        .notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 25px;
            background: var(--secondary-color);
            color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            display: none;
            align-items: center;
            gap: 10px;
            z-index: 1001;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        /* التجاوبية */
        @media (max-width: 768px) {
            .top-bar {
                flex-direction: column;
                gap: 15px;
                padding: 15px;
            }

            .controls {
                width: 100%;
                justify-content: center;
            }

            .hero-title {
                font-size: 2rem;
            }

            .features-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body class="light-mode">
    <!-- الشريط العلوي -->
    <div class="top-bar">
        <div class="logo-container">
            <div class="logo">
                <i class="fas fa-comment-dots"></i>
            </div>
            <div class="logo-text">
                <h1>{{ data.app_name }}</h1>
                <p>{{ data.tagline }}</p>
            </div>
        </div>
        
        <div class="controls">
            <button class="mode-toggle" onclick="toggleDarkMode()">
                <i class="fas fa-moon"></i> الوضع الداكن
            </button>
            
            <button class="settings-btn" onclick="openSettings()">
                <i class="fas fa-cog"></i> الإعدادات
            </button>
            
            <button class="publish-btn" onclick="publishApp()">
                <i class="fas fa-upload"></i> نشر التطبيق
            </button>
        </div>
    </div>

    <!-- المحتوى الرئيسي -->
    <div class="container">
        <!-- القسم البطولي -->
        <section class="hero-section">
            <h2 class="hero-title">مرحباً بك في {{ data.app_name }}</h2>
            <p class="hero-description">
                منصة دردشة احترافية تجمع بين بساطة الاستخدام وقوة الأداء. 
                مصممة لتلبية أعلى معايير الجودة والأمان في عالم الاتصال الرقمي.
            </p>
            <div class="image-section">
                <h3><i class="fas fa-image"></i> معاينة التطبيق</h3>
                <!-- هنا تضيف صورتك -->
                <div class="image-placeholder" id="imagePlaceholder">
                    <i class="fas fa-camera"></i> إضافة صورة واجهة التطبيق
                </div>
                <img src="" alt="واجهة تطبيق Moix" class="app-image" id="appImage">
                <p>واجهة مستخدم حديثة وسهلة الاستخدام</p>
            </div>
        </section>

        <!-- مميزات التطبيق -->
        <section class="card">
            <h3 class="card-title"><i class="fas fa-star"></i> مميزات {{ data.app_name }}</h3>
            <div class="features-grid">
                {% for feature in features %}
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="{{ feature.icon }}"></i>
                    </div>
                    <h4>{{ feature.title }}</h4>
                    <p>{{ feature.desc }}</p>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- الأمان -->
        <section class="card">
            <h3 class="card-title"><i class="fas fa-shield-alt"></i> نظام الأمان المتقدم</h3>
            <p>
                يتمتع {{ data.app_name }} بنظام أمان متعدد الطبقات يشمل تشفير end-to-end، 
                مصادقة متعددة العوامل، وتخزين آمن للبيانات. جميع المحادثات محمية بأحدث 
                تقنيات التشفير العالمية.
            </p>
        </section>

        <!-- المطورون -->
        <section class="card">
            <h3 class="card-title"><i class="fas fa-users-cog"></i> فريق التطوير</h3>
            <div class="developers-grid">
                {% for dev in developers %}
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="{{ dev.icon }}"></i>
                    </div>
                    <h4>{{ dev.name }}</h4>
                    <p>{{ dev.role }}</p>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- معلومات الإصدار -->
        <section class="card">
            <h3 class="card-title"><i class="fas fa-info-circle"></i> معلومات الإصدار</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div>
                    <h4><i class="fas fa-code-branch"></i> الإصدار</h4>
                    <p>{{ data.version }}</p>
                </div>
                <div>
                    <h4><i class="fas fa-calendar-alt"></i> تاريخ الإصدار</h4>
                    <p>{{ data.release_date }}</p>
                </div>
                <div>
                    <h4><i class="fas fa-building"></i> الشركة</h4>
                    <p>{{ data.company }}</p>
                </div>
            </div>
        </section>
    </div>

    <!-- التذييل -->
    <footer>
        <p>جميع الحقوق محفوظة © {{ data.company }} {{ now.year }}</p>
        <p class="version-info">الإصدار {{ data.version }} | آخر تحديث: {{ now.strftime('%Y-%m-%d') }}</p>
    </footer>

    <!-- إشعار النشر -->
    <div class="notification" id="publishNotification">
        <i class="fas fa-check-circle"></i>
        <span>تم نشر التطبيق بنجاح!</span>
    </div>

    <script>
        // تفعيل الوضع الداكن/الفاتح
        function toggleDarkMode() {
            const body = document.body;
            const modeBtn = document.querySelector('.mode-toggle i');
            
            if (body.classList.contains('dark-mode')) {
                body.classList.remove('dark-mode');
                body.classList.add('light-mode');
                modeBtn.className = 'fas fa-moon';
                document.querySelector('.mode-toggle span').textContent = 'الوضع الداكن';
            } else {
                body.classList.remove('light-mode');
                body.classList.add('dark-mode');
                modeBtn.className = 'fas fa-sun';
                document.querySelector('.mode-toggle span').textContent = 'الوضع الفاتح';
            }
        }

        // فتح الإعدادات
        function openSettings() {
            alert('🚀 صفحة الإعدادات قيد التطوير\n\nسيتم إضافة:\n- خيارات اللغة\n- إشعارات\n- خيارات الخصوصية\n- والمزيد...');
        }

        // نشر التطبيق
        let isPublished = false;
        function publishApp() {
            const publishBtn = document.querySelector('.publish-btn');
            const notification = document.getElementById('publishNotification');
            
            if (!isPublished) {
                publishBtn.innerHTML = '<i class="fas fa-check"></i> تم النشر';
                publishBtn.classList.add('published');
                isPublished = true;
                
                // عرض الإشعار
                notification.style.display = 'flex';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);
                
                alert('🎉 تم نشر تطبيق Moix بنجاح!\n\nيمكن الآن الوصول إليه من قبل المستخدمين.');
            } else {
                alert('✅ التطبيق منشور بالفعل!');
            }
        }

        // إضافة الصورة (يمكنك تعديل هذا الجزء)
        function addImage(imageUrl) {
            const placeholder = document.getElementById('imagePlaceholder');
            const image = document.getElementById('appImage');
            
            if (imageUrl) {
                placeholder.style.display = 'none';
                image.src = imageUrl;
                image.style.display = 'block';
            }
        }

        // عند التحميل
        document.addEventListener('DOMContentLoaded', function() {
            // يمكنك استدعاء addImage هنا عندما يكون لديك رابط الصورة
            // مثال: addImage('https://example.com/your-image.jpg');
            
            console.log('موقع Moix جاهز للتقديم!');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    now = datetime.datetime.now()
    return render_template_string(
        HTML_TEMPLATE, 
        data=SITE_DATA,
        sections=SECTIONS,
        features=FEATURES,
        developers=DEVELOPERS,
        now=now
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)