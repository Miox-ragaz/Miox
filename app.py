from flask import Flask, render_template_string, request, jsonify
import datetime

app = Flask(__name__)

# بيانات الموقع
SITE_DATA = {
    "app_name": "Moix",
    "company": "Moix Technologies FZ-LLC",
    "tagline": "منصة اتصال ذكية للمستقبل الرقمي",
    "slogan": "التواصل الآمن السريع",
    "version": "2.1.0",
    "release_year": "2024",
    "download_link": "https://play.google.com/store/apps/details?id=com.moix.app",
    "support_email": "support@moix.tech",
    "website": "https://moix.tech"
}

# اللغات المتاحة
LANGUAGES = [
    {"code": "ar", "name": "العربية", "icon": "🇸🇦"},
    {"code": "en", "name": "English", "icon": "🇺🇸"},
    {"code": "fr", "name": "Français", "icon": "🇫🇷"},
    {"code": "ru", "name": "Русский", "icon": "🇷🇺"}
]

# الثيمات (المظاهر)
THEMES = [
    {"id": "light", "name": "فاتح", "icon": "fas fa-sun"},
    {"id": "dark", "name": "داكن", "icon": "fas fa-moon"},
    {"id": "blue", "name": "أزرق", "icon": "fas fa-palette"},
    {"id": "green", "name": "أخضر", "icon": "fas fa-leaf"}
]

# المميزات الرئيسية
FEATURES = [
    {
        "icon": "fas fa-bolt",
        "title": "سرعة فائقة",
        "desc": "محرك دردشة يعمل بسرعة الضوء مع زمن استجابة أقل من 0.1 ثانية"
    },
    {
        "icon": "fas fa-shield-alt",
        "title": "أمان متقدم",
        "desc": "تشفير من طرف إلى طرف (End-to-End) مع حماية متعددة الطبقات"
    },
    {
        "icon": "fas fa-users",
        "title": "مجموعات كبيرة",
        "desc": "دعم مجموعات تصل إلى 10,000 عضو مع إدارة متقدمة"
    },
    {
        "icon": "fas fa-cloud-upload-alt",
        "title": "تخزين سحابي",
        "desc": "مساحة تخزين غير محدودة للملفات والوسائط"
    },
    {
        "icon": "fas fa-robot",
        "title": "ذكاء اصطناعي",
        "desc": "مساعد ذكي للترجمة الفورية وتنظيم المحادثات"
    },
    {
        "icon": "fas fa-video",
        "title": "مكالمات عالية الجودة",
        "desc": "مكالمات فيديو بدقة 4K ومكالمات صوتية بنقاء استوديو"
    }
]

# الأسئلة الشائعة
FAQ = [
    {
        "q": "ما هو تطبيق Moix؟",
        "a": "Moix هو منصة دردشة متقدمة تجمع بين السرعة والأمان والحداثة في واجهة مستخدم بديهية."
    },
    {
        "q": "هل التطبيق مجاني؟",
        "a": "نعم، الإصدار الأساسي مجاني تماماً مع جميع المميزات الأساسية."
    },
    {
        "q": "كيف أحافظ على خصوصيتي؟",
        "a": "جميع محادثاتك مشفرة ولا يمكن لأحد قراءتها، حتى نحن لا نستطيع الوصول إليها."
    },
    {
        "q": "هل يدعم اللغة العربية؟",
        "a": "نعم، التطبيق يدعم اللغة العربية كاملة مع واجهة مخصصة للمستخدم العربي."
    },
    {
        "q": "كيف أبدأ باستخدام التطبيق؟",
        "a": "قم بتحميل التطبيق، أنشئ حسابك في 30 ثانية وابدأ التواصل فوراً."
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.app_name }} - {{ data.tagline }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
    <style>
        /* المتغيرات الأساسية */
        :root {
            /* الألوان الأساسية */
            --primary-color: #2563eb;
            --secondary-color: #10b981;
            --accent-color: #8b5cf6;
            
            /* الثيم الفاتح (الإفتراضي) */
            --bg-color: #ffffff;
            --card-bg: #f8fafc;
            --text-color: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            --hover-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
        }

        /* الثيم الداكن */
        .theme-dark {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #334155;
            --shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            --hover-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        /* الثيم الأزرق */
        .theme-blue {
            --primary-color: #3b82f6;
            --bg-color: #eff6ff;
            --card-bg: #dbeafe;
            --text-color: #1e40af;
            --border-color: #93c5fd;
        }

        /* الثيم الأخضر */
        .theme-green {
            --primary-color: #10b981;
            --bg-color: #f0fdf4;
            --card-bg: #dcfce7;
            --text-color: #065f46;
            --border-color: #86efac;
        }

        /* التصميم العام */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: background-color 0.3s, color 0.3s;
        }

        body {
            font-family: 'Tajawal', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.7;
            min-height: 100vh;
        }

        /* الشريط العلوي - ثابت */
        .top-bar {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            padding: 1rem 2rem;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 70px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo-icon {
            background: rgba(255, 255, 255, 0.2);
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
        }

        .logo-text h1 {
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
        }

        .logo-text p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.9rem;
            margin-top: 3px;
        }

        /* أزرار التحكم */
        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .btn {
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            cursor: pointer;
            font-family: 'Tajawal', sans-serif;
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
            white-space: nowrap;
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .btn-download {
            background: linear-gradient(135deg, #10b981, #059669);
            border: none;
            padding: 0.7rem 1.5rem;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* المحتوى الرئيسي */
        main {
            padding-top: 70px;
            max-width: 1400px;
            margin: 0 auto;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* القسم البطولي */
        .hero {
            text-align: center;
            padding: 4rem 1rem;
            margin-bottom: 3rem;
        }

        .hero h2 {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .hero p {
            font-size: 1.3rem;
            color: var(--text-secondary);
            max-width: 800px;
            margin: 0 auto 2rem;
        }

        /* إحصائيات */
        .stats {
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
            margin: 3rem 0;
        }

        .stat-box {
            text-align: center;
            padding: 1.5rem;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--primary-color);
            display: block;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        /* المميزات */
        .features {
            margin: 4rem 0;
        }

        .section-title {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: var(--text-color);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }

        .feature-card {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            transition: all 0.3s;
        }

        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: var(--hover-shadow);
        }

        .feature-icon {
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }

        /* قسم الشركة */
        .company-section {
            background: var(--card-bg);
            padding: 3rem;
            border-radius: 20px;
            margin: 4rem 0;
            border: 1px solid var(--border-color);
        }

        /* قسم التحميل */
        .download-section {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            border-radius: 30px;
            margin: 4rem 0;
            color: white;
        }

        .download-section h3 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        /* التذييل */
        footer {
            text-align: center;
            padding: 3rem 2rem;
            border-top: 1px solid var(--border-color);
            margin-top: 4rem;
            color: var(--text-secondary);
        }

        /* النوافذ المنبثقة */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 2000;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 20px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .close-modal {
            float: left;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
        }

        /* القائمة الرأسية للإعدادات */
        .settings-menu {
            list-style: none;
        }

        .settings-menu li {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background 0.3s;
        }

        .settings-menu li:hover {
            background: rgba(0, 0, 0, 0.05);
        }

        .theme-options {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 1rem;
        }

        .theme-option {
            padding: 1rem;
            border-radius: 10px;
            cursor: pointer;
            text-align: center;
            border: 2px solid var(--border-color);
            transition: all 0.3s;
        }

        .theme-option:hover {
            border-color: var(--primary-color);
        }

        .theme-option.active {
            border-color: var(--primary-color);
            background: rgba(37, 99, 235, 0.1);
        }

        /* الأسئلة الشائعة */
        .faq-item {
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
        }

        .faq-question {
            padding: 1rem;
            background: var(--card-bg);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .faq-answer {
            padding: 1rem;
            display: none;
            border-top: 1px solid var(--border-color);
        }

        /* التجاوبية */
        @media (max-width: 1024px) {
            .hero h2 {
                font-size: 2.8rem;
            }
            
            .features-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 768px) {
            .top-bar {
                padding: 1rem;
                height: auto;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .controls {
                order: 3;
                width: 100%;
                justify-content: center;
                margin-top: 10px;
            }
            
            .hero h2 {
                font-size: 2.2rem;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
            
            .stats {
                gap: 1.5rem;
            }
            
            .stat-number {
                font-size: 2rem;
            }
            
            main {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        @media (max-width: 480px) {
            .btn {
                padding: 0.5rem 1rem;
                font-size: 0.8rem;
            }
            
            .hero h2 {
                font-size: 1.8rem;
            }
            
            .hero p {
                font-size: 1.1rem;
            }
        }
    </style>
</head>
<body>
    <!-- الشريط العلوي -->
    <div class="top-bar">
        <div class="logo">
            <div class="logo-icon">
                <i class="fas fa-comment-dots"></i>
            </div>
            <div class="logo-text">
                <h1>{{ data.app_name }}</h1>
                <p>{{ data.slogan }}</p>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="openModal('settingsModal')">
                <i class="fas fa-cog"></i> الإعدادات
            </button>
            
            <button class="btn" onclick="openModal('faqModal')">
                <i class="fas fa-question-circle"></i> أسئلة شائعة
            </button>
            
            <button class="btn btn-download" onclick="downloadApp()">
                <i class="fas fa-download"></i> تحميل التطبيق
            </button>
        </div>
    </div>

    <!-- المحتوى الرئيسي -->
    <main>
        <!-- القسم البطولي -->
        <section class="hero">
            <h2>مرحباً في عالم {{ data.app_name }}</h2>
            <p>
                منصة اتصال رقمية متطورة، تجمع بين بساطة الاستخدام وقوة الأداء. 
                مصممة خصيصاً لتلبية احتياجات التواصل في العصر الحديث مع الحفاظ على أعلى معايير الأمان والخصوصية.
            </p>
            
            <!-- إحصائيات -->
            <div class="stats">
                <div class="stat-box">
                    <span class="stat-number">+500K</span>
                    <span class="stat-label">مستخدم نشط</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">99.9%</span>
                    <span class="stat-label">وقت تشغيل</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">+50</span>
                    <span class="stat-label">دولة</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">128-bit</span>
                    <span class="stat-label">تشفير</span>
                </div>
            </div>
        </section>

        <!-- المميزات -->
        <section class="features">
            <h2 class="section-title">مميزات فريدة</h2>
            <div class="features-grid">
                {% for feature in features %}
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="{{ feature.icon }}"></i>
                    </div>
                    <h3>{{ feature.title }}</h3>
                    <p>{{ feature.desc }}</p>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- قسم الشركة -->
        <section class="company-section">
            <h2 class="section-title">عن {{ data.company }}</h2>
            <div style="font-size: 1.1rem; line-height: 1.8;">
                <p>
                    {{ data.company }} هي شركة رائدة في مجال التقنية الرقمية، متخصصة في تطوير حلول اتصال آمنة ومبتكرة.
                    نؤمن بأن التواصل يجب أن يكون سلساً وآمناً للجميع، بغض النظر عن مكانهم أو لغتهم.
                </p>
                <p style="margin-top: 1rem;">
                    مهمتنا هي إعادة تعريف طرق التواصل الرقمي من خلال تقديم منصات ذكية تجمع بين السرعة والأمان وسهولة الاستخدام.
                    نحن نعمل باستمرار على تطوير وتحسين منتجاتنا لضمان تجربة مستخدم استثنائية.
                </p>
                <p style="margin-top: 1rem;">
                    <strong>رؤيتنا:</strong> أن نكون المنصة الرائدة عالمياً في مجال الاتصال الآمن.
                    <br>
                    <strong>قيمنا:</strong> الأمان، الخصوصية، الابتكار، الشفافية.
                </p>
            </div>
        </section>

        <!-- قسم التحميل -->
        <section class="download-section">
            <h3>جاهز للبدء؟</h3>
            <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">
                حمل تطبيق {{ data.app_name }} الآن وانضم إلى مجتمعنا المتنامي
            </p>
            <button class="btn" style="background: white; color: var(--primary-color); padding: 1rem 2rem; font-size: 1.1rem;" onclick="downloadApp()">
                <i class="fas fa-download"></i> تحميل الآن
            </button>
            <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
                متوفر على Google Play و App Store
            </p>
        </section>
    </main>

    <!-- التذييل -->
    <footer>
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">© {{ data.release_year }} {{ data.company }}. جميع الحقوق محفوظة.</p>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">
            الإصدار {{ data.version }} | 
            <a href="mailto:{{ data.support_email }}" style="color: var(--primary-color); text-decoration: none;">{{ data.support_email }}</a> | 
            <a href="{{ data.website }}" style="color: var(--primary-color); text-decoration: none;">{{ data.website }}</a>
        </p>
    </footer>

    <!-- نافذة الإعدادات -->
    <div id="settingsModal" class="modal">
        <div class="modal-content">
            <button class="close-modal" onclick="closeModal('settingsModal')">×</button>
            <h2 style="margin-bottom: 1.5rem;"><i class="fas fa-cog"></i> الإعدادات</h2>
            
            <ul class="settings-menu">
                <li onclick="showThemeOptions()">
                    <i class="fas fa-palette"></i>
                    <div>
                        <strong>تغيير المظهر</strong>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 3px;">اختر ثيم الموقع</p>
                    </div>
                </li>
                <li onclick="showLanguageOptions()">
                    <i class="fas fa-language"></i>
                    <div>
                        <strong>تغيير اللغة</strong>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 3px;">اختر لغة الواجهة</p>
                    </div>
                </li>
                <li onclick="downloadApp()">
                    <i class="fas fa-download"></i>
                    <div>
                        <strong>تحميل التطبيق</strong>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 3px;">نزل تطبيق Moix</p>
                    </div>
                </li>
            </ul>

            <!-- خيارات الثيمات -->
            <div id="themeOptions" style="display: none; margin-top: 2rem;">
                <h3 style="margin-bottom: 1rem;">اختر مظهر الموقع</h3>
                <div class="theme-options">
                    {% for theme in themes %}
                    <div class="theme-option {{ 'active' if theme.id == 'light' else '' }}" 
                         data-theme="{{ theme.id }}"
                         onclick="changeTheme('{{ theme.id }}')">
                        <i class="{{ theme.icon }}"></i><br>
                        {{ theme.name }}
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- خيارات اللغة -->
            <div id="languageOptions" style="display: none; margin-top: 2rem;">
                <h3 style="margin-bottom: 1rem;">اختر اللغة</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    {% for lang in languages %}
                    <div style="padding: 1rem; border: 1px solid var(--border-color); border-radius: 10px; cursor: pointer;" onclick="changeLanguage('{{ lang.code }}')">
                        <strong>{{ lang.icon }} {{ lang.name }}</strong>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- نافذة الأسئلة الشائعة -->
    <div id="faqModal" class="modal">
        <div class="modal-content">
            <button class="close-modal" onclick="closeModal('faqModal')">×</button>
            <h2 style="margin-bottom: 1.5rem;"><i class="fas fa-question-circle"></i> الأسئلة الشائعة</h2>
            
            {% for item in faq %}
            <div class="faq-item">
                <div class="faq-question" onclick="toggleFaq({{ loop.index }})">
                    <span>{{ item.q }}</span>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer" id="faqAnswer{{ loop.index }}">
                    {{ item.a }}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        // حالة التطبيق
        let currentTheme = 'light';
        let currentLanguage = 'ar';

        // فتح النوافذ المنبثقة
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'flex';
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }

        // إظهار خيارات الثيمات
        function showThemeOptions() {
            document.getElementById('themeOptions').style.display = 'block';
            document.getElementById('languageOptions').style.display = 'none';
        }

        // إظهار خيارات اللغة
        function showLanguageOptions() {
            document.getElementById('languageOptions').style.display = 'block';
            document.getElementById('themeOptions').style.display = 'none';
        }

        // تغيير الثيم (المظهر)
        function changeTheme(themeId) {
            // إزالة جميع الثيمات
            document.body.classList.remove('theme-dark', 'theme-blue', 'theme-green');
            
            // إضافة الثيم المختار
            if (themeId !== 'light') {
                document.body.classList.add('theme-' + themeId);
            }
            
            currentTheme = themeId;
            
            // تحديث الزر النشط
            document.querySelectorAll('.theme-option').forEach(option => {
                option.classList.remove('active');
                if (option.dataset.theme === themeId) {
                    option.classList.add('active');
                }
            });
            
            // حفظ في التخزين المحلي
            localStorage.setItem('moix_theme', themeId);
        }

        // تغيير اللغة
        function changeLanguage(langCode) {
            currentLanguage = langCode;
            alert('تم تغيير اللغة إلى ' + langCode + '\n\n(هذه ميزة تجريبية - في الإصدار الكامل ستتغير كل نصوص الموقع)');
            localStorage.setItem('moix_language', langCode);
        }

        // تحميل التطبيق
        function downloadApp() {
            window.open('{{ data.download_link }}', '_blank');
        }

        // تبديل الأسئلة الشائعة
        function toggleFaq(index) {
            const answer = document.getElementById('faqAnswer' + index);
            const icon = document.querySelector(`#faqAnswer${index}`).previousElementSibling.querySelector('i');
            
            if (answer.style.display === 'block') {
                answer.style.display = 'none';
                icon.className = 'fas fa-chevron-down';
            } else {
                answer.style.display = 'block';
                icon.className = 'fas fa-chevron-up';
            }
        }

        // عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            // تحميل الثيم المحفوظ
            const savedTheme = localStorage.getItem('moix_theme');
            if (savedTheme) {
                changeTheme(savedTheme);
            }

            // تحميل اللغة المحفوظة
            const savedLang = localStorage.getItem('moix_language');
            if (savedLang) {
                currentLanguage = savedLang;
            }

            // إغلاق النوافذ بالضغط خارجها
            window.onclick = function(event) {
                if (event.target.classList.contains('modal')) {
                    event.target.style.display = 'none';
                }
            };

            console.log('📍 موقع {{ data.app_name }} جاهز للعمل!');
            console.log('📱 متجاوب مع جميع الشاشات');
            console.log('🎨 ' + currentTheme + ' theme active');
            console.log('🌐 ' + currentLanguage + ' language selected');
        });

        // إخفاء النوافذ بالضغط على زر ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal').forEach(modal => {
                    modal.style.display = 'none';
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE,
        data=SITE_DATA,
        features=FEATURES,
        languages=LANGUAGES,
        themes=THEMES,
        faq=FAQ
    )

@app.route('/api/change-theme', methods=['POST'])
def change_theme():
    theme = request.json.get('theme', 'light')
    return jsonify({'status': 'success', 'theme': theme})

@app.route('/api/change-language', methods=['POST'])
def change_language():
    lang = request.json.get('lang', 'ar')
    return jsonify({'status': 'success', 'language': lang})

if __name__ == '__main__':
    print("🚀 تشغيل موقع Moix المتطور...")
    print("📧 الدعم: support@moix.tech")
    print("🌐 افتح: http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)