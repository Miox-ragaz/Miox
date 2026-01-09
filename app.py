from flask import Flask, render_template_string

app = Flask(__name__)
@app.route('/google620d181fa7a7ee21.html')
def google_verification():
    return "google-site-verification: google620d181fa7a7ee21.html"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mocat - تطبيق الدردشة الآمن</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* الأساسيات */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }
        
        body {
            font-family: system-ui, sans-serif;
            background: #0f172a;
            color: #f1f5f9;
            line-height: 1.6;
        }
        
        body.theme-white {
            background: #ffffff;
            color: #1f2937;
        }
        
        /* الهيدر مع الصورة - أكثر شفافية */
        .header {
            height: 70vh;
            background: linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.7)),
                        url('https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1600&q=80&fit=crop&crop=faces');
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            animation: fadeIn 1s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        body.theme-white .header {
            background: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.8)),
                        url('https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1600&q=80&fit=crop&crop=faces');
        }
        
        .header-content {
            max-width: 800px;
            padding: 2rem;
            animation: slideUp 1s ease-out 0.3s both;
        }
        
        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .app-logo {
            font-size: 4rem;
            color: #60a5fa;
            margin-bottom: 1rem;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .app-title {
            font-size: 3rem;
            color: white;
            margin-bottom: 1rem;
            animation: fadeIn 1.5s ease-out 0.5s both;
        }
        
        body.theme-white .app-title {
            color: #1f2937;
        }
        
        .app-tagline {
            font-size: 1.2rem;
            color: #cbd5e1;
            max-width: 600px;
            margin: 0 auto;
            animation: fadeIn 1.5s ease-out 0.7s both;
        }
        
        body.theme-white .app-tagline {
            color: #4b5563;
        }
        
        /* التنقل */
        .nav {
            background: rgba(30, 41, 59, 0.95);
            padding: 1rem 2rem;
            display: flex;
            justify-content: center;
            gap: 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
            animation: slideDown 0.5s ease-out;
        }
        
        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }
        
        body.theme-white .nav {
            background: rgba(255, 255, 255, 0.95);
        }
        
        .nav-btn {
            background: none;
            border: none;
            color: #cbd5e1;
            font-size: 1rem;
            cursor: pointer;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        body.theme-white .nav-btn {
            color: #6b7280;
        }
        
        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            transform: translateY(-2px);
        }
        
        body.theme-white .nav-btn:hover {
            background: rgba(0, 0, 0, 0.05);
            color: #1f2937;
        }
        
        /* المحتوى */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .section {
            padding: 4rem 0;
            border-bottom: 1px solid #334155;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.8s ease-out forwards;
        }
        
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .section:nth-child(1) { animation-delay: 0.2s; }
        .section:nth-child(2) { animation-delay: 0.4s; }
        .section:nth-child(3) { animation-delay: 0.6s; }
        .section:nth-child(4) { animation-delay: 0.8s; }
        
        body.theme-white .section {
            border-bottom: 1px solid #e5e7eb;
        }
        
        .section-title {
            font-size: 2rem;
            color: #60a5fa;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        body.theme-white .section-title {
            color: #1d4ed8;
        }
        
        /* المميزات */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .feature-card {
            background: #1e293b;
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #334155;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .feature-card:nth-child(1) { animation-delay: 0.3s; }
        .feature-card:nth-child(2) { animation-delay: 0.4s; }
        .feature-card:nth-child(3) { animation-delay: 0.5s; }
        .feature-card:nth-child(4) { animation-delay: 0.6s; }
        .feature-card:nth-child(5) { animation-delay: 0.7s; }
        .feature-card:nth-child(6) { animation-delay: 0.8s; }
        
        body.theme-white .feature-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }
        
        .feature-card:hover {
            transform: translateY(-5px) scale(1.02);
            border-color: #60a5fa;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .feature-icon {
            font-size: 2rem;
            color: #60a5fa;
            margin-bottom: 1rem;
        }
        
        /* الأسئلة الشائعة */
        .faq-grid {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .faq-item {
            background: #1e293b;
            border-radius: 10px;
            margin-bottom: 1rem;
            overflow: hidden;
            border: 1px solid #334155;
            animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .faq-item:nth-child(1) { animation-delay: 0.3s; }
        .faq-item:nth-child(2) { animation-delay: 0.4s; }
        .faq-item:nth-child(3) { animation-delay: 0.5s; }
        .faq-item:nth-child(4) { animation-delay: 0.6s; }
        
        body.theme-white .faq-item {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }
        
        .faq-question {
            padding: 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1e293b;
            transition: all 0.3s ease;
        }
        
        body.theme-white .faq-question {
            background: #f9fafb;
        }
        
        .faq-question:hover {
            background: #334155;
        }
        
        body.theme-white .faq-question:hover {
            background: #e5e7eb;
        }
        
        .faq-answer {
            padding: 1.5rem;
            border-top: 1px solid #334155;
            display: none;
            background: #0f172a;
            animation: slideDownAnswer 0.3s ease-out;
        }
        
        @keyframes slideDownAnswer {
            from { 
                opacity: 0;
                transform: translateY(-10px);
            }
            to { 
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        body.theme-white .faq-answer {
            border-top: 1px solid #e5e7eb;
            background: #ffffff;
        }
        
        /* المطورون - صورة جديدة لأشخاص مبسوطين */
        .developers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        
        .developer-card {
            text-align: center;
            padding: 2rem;
            background: #1e293b;
            border-radius: 12px;
            border: 1px solid #334155;
            animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .developer-card:nth-child(1) { animation-delay: 0.3s; }
        .developer-card:nth-child(2) { animation-delay: 0.4s; }
        .developer-card:nth-child(3) { animation-delay: 0.5s; }
        
        body.theme-white .developer-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }
        
        .dev-icon {
            font-size: 3rem;
            color: #60a5fa;
            margin-bottom: 1rem;
        }
        
        /* الإعدادات */
        .settings-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        }
        
        .settings-content {
            background: #1e293b;
            padding: 2rem;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #334155;
            animation: slideUp 0.3s ease;
        }
        
        body.theme-white .settings-content {
            background: #ffffff;
            border: 1px solid #e5e7eb;
        }
        
        .settings-section {
            margin-bottom: 2rem;
        }
        
        .setting-item {
            padding: 1rem;
            background: #0f172a;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #334155;
        }
        
        body.theme-white .setting-item {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }
        
        /* أزرار التحديد - زرين فقط */
        .theme-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
        }
        
        .theme-btn {
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            border: 2px solid transparent;
            background: #1e293b;
            color: white;
            flex: 1;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .theme-btn.active {
            border-color: #60a5fa;
            background: rgba(96, 165, 250, 0.2);
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
        }
        
        body.theme-white .theme-btn {
            background: #f3f4f6;
            color: #1f2937;
        }
        
        body.theme-white .theme-btn.active {
            border-color: #1d4ed8;
            background: rgba(29, 78, 216, 0.1);
            box-shadow: 0 4px 12px rgba(29, 78, 216, 0.2);
        }
        
        .lang-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
        }
        
        .lang-btn {
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            border: 2px solid transparent;
            background: #1e293b;
            color: white;
            flex: 1;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .lang-btn.active {
            border-color: #60a5fa;
            background: rgba(96, 165, 250, 0.2);
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
        }
        
        body.theme-white .lang-btn {
            background: #f3f4f6;
            color: #1f2937;
        }
        
        body.theme-white .lang-btn.active {
            border-color: #1d4ed8;
            background: rgba(29, 78, 216, 0.1);
            box-shadow: 0 4px 12px rgba(29, 78, 216, 0.2);
        }
        
        /* زر التحميل */
        .download-section {
            text-align: center;
            padding: 3rem;
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            border-radius: 20px;
            margin: 3rem 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .download-btn {
            background: white;
            color: #1e40af;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            border-radius: 10px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
            margin-top: 1rem;
            transition: all 0.3s ease;
        }
        
        .download-btn:hover {
            background: #f8fafc;
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }
        
        /* التذييل */
        footer {
            text-align: center;
            padding: 3rem;
            color: #94a3b8;
            border-top: 1px solid #334155;
            margin-top: 4rem;
            animation: fadeIn 1s ease-out 1s both;
        }
        
        body.theme-white footer {
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }
        
        /* التجاوبية */
        @media (max-width: 768px) {
            .header {
                height: 60vh;
            }
            
            .app-title {
                font-size: 2rem;
            }
            
            .nav {
                padding: 1rem;
                gap: 1rem;
            }
            
            .nav-btn span {
                display: none;
            }
            
            .container {
                padding: 0 1rem;
            }
            
            .section {
                padding: 3rem 0;
            }
            
            .theme-buttons, .lang-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <!-- الهيدر مع الصورة الجديدة -->
    <header class="header">
        <div class="header-content">
            <div class="app-logo">
                <i class="fas fa-comment-dots"></i>
            </div>
            <h1 class="app-title" id="appTitle">Mocat</h1>
            <p class="app-tagline" id="appTagline">
                تطبيق دردشة آمن وسريع. تواصل مع أصدقائك بخصوصية تامة وحماية متقدمة.
            </p>
        </div>
    </header>

    <!-- التنقل -->
    <nav class="nav">
        <button class="nav-btn" onclick="scrollToSection('features')">
            <i class="fas fa-star"></i>
            <span id="navFeatures">المميزات</span>
        </button>
        <button class="nav-btn" onclick="scrollToSection('developers')">
            <i class="fas fa-users"></i>
            <span id="navDevelopers">المطورون</span>
        </button>
        <button class="nav-btn" onclick="scrollToSection('security')">
            <i class="fas fa-shield-alt"></i>
            <span id="navSecurity">الأمان</span>
        </button>
        <button class="nav-btn" onclick="openSettings()">
            <i class="fas fa-cog"></i>
            <span id="navSettings">الإعدادات</span>
        </button>
        <button class="nav-btn" onclick="openFAQ()">
            <i class="fas fa-question-circle"></i>
            <span id="navFAQ">أسئلة شائعة</span>
        </button>
    </nav>

    <!-- المحتوى الرئيسي -->
    <div class="container">
        <!-- مميزات -->
        <section id="features" class="section">
            <h2 class="section-title" id="featuresTitle">مميزات التطبيق</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                    <h3 id="feature1Title">تشفير كامل</h3>
                    <p id="feature1Desc">جميع المحادثات مشفرة من البداية إلى النهاية. لا يمكن لأي شخص قراءة رسائلك، حتى نحن.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <h3 id="feature2Title">سرعة عالية</h3>
                    <p id="feature2Desc">إرسال واستقبال الرسائل فورياً بدون تأخير. واجهة سريعة تستجيب فوراً لأي أمر.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-user-group"></i>
                    </div>
                    <h3 id="feature3Title">مجموعات ذكية</h3>
                    <p id="feature3Desc">أنشئ مجموعات دردشة مع أصدقائك. أدوات إدارة متقدمة وسهلة الاستخدام.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-image"></i>
                    </div>
                    <h3 id="feature4Title">مشاركة الوسائط</h3>
                    <p id="feature4Desc">شارك الصور والفيديوهات والملفات بسهولة. دعم لكافة الصيغ الشائعة.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-moon"></i>
                    </div>
                    <h3 id="feature5Title">وضع ليلي</h3>
                    <p id="feature5Desc">وضع مظلم مريح للعين أثناء الليل. يتكامل مع نظام الجهاز تلقائياً.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-language"></i>
                    </div>
                    <h3 id="feature6Title">دعم عربي كامل</h3>
                    <p id="feature6Desc">واجهة باللغة العربية مع دعم كامل للحروف والاتجاه. مناسب للمستخدم العربي.</p>
                </div>
            </div>
        </section>

        <!-- الأمان -->
        <section id="security" class="section">
            <h2 class="section-title" id="securityTitle">نظام الأمان المتقدم</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <h3 id="security1Title">حماية البيانات</h3>
                    <p id="security1Desc">بياناتك تبقى على جهازك ولا نرسلها إلى سيرفرات خارجية. هذا يعني خصوصية كاملة.</p>
                </div>
                
                <div class="feature-card">
                    <h3 id="security2Title">هل سمعت من قبل عن اختراق؟</h3>
                    <p id="security2Desc">لا داعي للقلق. نظامنا مبني على أساس عدم تخزين بيانات حساسة. لا توجد قاعدة بيانات مركزية يمكن اختراقها.</p>
                </div>
                
                <div class="feature-card">
                    <h3 id="security3Title">التحكم في الصلاحيات</h3>
                    <p id="security3Desc">أنت تتحكم كاملاً في الصلاحيات. التطبيق لا يطلب صلاحيات غير ضرورية.</p>
                </div>
            </div>
        </section>

        <!-- المطورون -->
        <section id="developers" class="section">
            <h2 class="section-title" id="developersTitle">فريق التطوير</h2>
            <div class="developers-grid">
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="fas fa-code"></i>
                    </div>
                    <h3 id="dev1Title">مطورون متمرسون</h3>
                    <p id="dev1Desc">فريق من المطورين المتخصصين في برمجة تطبيقات التواصل والأمان.</p>
                </div>
                
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="fas fa-palette"></i>
                    </div>
                    <h3 id="dev2Title">مصممو واجهات</h3>
                    <p id="dev2Desc">مصممون محترفون يهتمون بتجربة المستخدم وسهولة الاستخدام.</p>
                </div>
                
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3 id="dev3Title">خبراء أمان</h3>
                    <p id="dev3Desc">متخصصون في أمن المعلومات وحماية البيانات الرقمية.</p>
                </div>
            </div>
        </section>

        <!-- الأسئلة الشائعة -->
        <section id="faq" class="section">
            <h2 class="section-title" id="faqTitle">أسئلة شائعة</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(1)">
                        <span id="faq1Question">كيف يعمل تطبيق Mocat؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq1Answer">
                        <p id="faq1AnswerText">التطبيق يسمح لك بإنشاء حساب، إضافة أصدقاء، وإنشاء محادثات فردية أو جماعية. جميع الرسائل ترسل مشفرة وتظهر فوراً للمستقبل.</p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(2)">
                        <span id="faq2Question">هل المحادثات آمنة حقاً؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq2Answer">
                        <p id="faq2AnswerText">نعم، نستخدم تشفير من طرف إلى طرف. هذا يعني أن الرسائل تتشفر على جهازك وتتشفر على جهاز المستقبل. لا يمكن قراءتها أثناء النقل.</p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(3)">
                        <span id="faq3Question">ما هي مميزات التطبيق؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq3Answer">
                        <p id="faq3AnswerText">تطبيق Mocat يوفر تشفير كامل، سرعة عالية، مجموعات ذكية، مشاركة وسائط، وضع ليلي، ودعم عربي كامل لتجربة دردشة آمنة وسلسة.</p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(4)">
                        <span id="faq4Question">هل يمكن اختراق التطبيق؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq4Answer">
                        <p id="faq4AnswerText">النظام مبني على مبدأ الأمان أولاً. لا نخزن بيانات حساسة على سيرفرات مركزية. حتى لو تم اختراق السيرفر، لن تصل للمحادثات لأنها مشفرة.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- التحميل -->
        <section class="download-section">
            <h2 style="font-size: 2rem; margin-bottom: 1rem;" id="downloadTitle">جاهز للبدء؟</h2>
            <p style="font-size: 1.1rem; margin-bottom: 1rem;" id="downloadDesc">حمل Mocat الآن وابدأ الدردشة الآمنة</p>
            <button class="download-btn" onclick="downloadApp()">
                <i class="fas fa-download"></i> <span id="downloadBtn">تحميل التطبيق</span>
            </button>
        </section>
    </div>

    <!-- التذييل -->
    <footer>
        <p id="footerText">Mocat &copy; 2024 - تطبيق دردشة آمن</p>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: #64748b;" id="footerSubtext">
            مصمم بحب لتوفير تواصل آمن للجميع
        </p>
    </footer>

    <!-- نافذة الإعدادات -->
    <div id="settingsModal" class="settings-modal">
        <div class="settings-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2 style="color: #60a5fa;">
                    <i class="fas fa-cog"></i> <span id="settingsTitle">إعدادات التطبيق</span>
                </h2>
                <button onclick="closeSettings()" style="background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer;">
                    ×
                </button>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-info-circle"></i> <span id="infoTitle">معلومات التطبيق</span>
                </h3>
                <div class="setting-item">
                    <strong id="appNameLabel">اسم التطبيق:</strong> Mocat<br>
                    <strong id="versionLabel">الإصدار:</strong> 1.0.0<br>
                    <strong id="typeLabel">النوع:</strong> <span id="appType">تطبيق دردشة</span><br>
                    <strong id="statusLabel">الحالة:</strong> <span id="appStatus">تحت التطوير</span>
                </div>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-palette"></i> <span id="themeTitle">المظهر</span>
                </h3>
                <div class="setting-item">
                    <div class="theme-buttons">
                        <button id="themeDark" class="theme-btn active" onclick="changeTheme('dark')">
                            داكن
                        </button>
                        <button id="themeWhite" class="theme-btn" onclick="changeTheme('white')">
                            فاتح
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-language"></i> <span id="languageTitle">اللغة</span>
                </h3>
                <div class="setting-item">
                    <div class="lang-buttons">
                        <button id="langAr" class="lang-btn active" onclick="changeLanguage('ar')">
                            العربية
                        </button>
                        <button id="langEn" class="lang-btn" onclick="changeLanguage('en')">
                            English
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-book"></i> <span id="aboutTitle">حول التطبيق</span>
                </h3>
                <div class="setting-item">
                    <p style="color: #94a3b8;" id="aboutText">
                        Mocat هو تطبيق دردشة يركز على الأمان والخصوصية. تم تطويره باستخدام تقنيات حديثة تضمن حماية بيانات المستخدمين مع توفير تجربة استخدام سلسة.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // حالة التطبيق
        let currentLanguage = 'ar';
        let currentTheme = 'dark';
        
        // نصوص عربية
        const arabicTexts = {
            appTitle: "Mocat",
            appTagline: "تطبيق دردشة آمن وسريع. تواصل مع أصدقائك بخصوصية تامة وحماية متقدمة.",
            navFeatures: "المميزات",
            navDevelopers: "المطورون",
            navSecurity: "الأمان",
            navSettings: "الإعدادات",
            navFAQ: "أسئلة شائعة",
            featuresTitle: "مميزات التطبيق",
            feature1Title: "تشفير كامل",
            feature1Desc: "جميع المحادثات مشفرة من البداية إلى النهاية. لا يمكن لأي شخص قراءة رسائلك، حتى نحن.",
            feature2Title: "سرعة عالية",
            feature2Desc: "إرسال واستقبال الرسائل فورياً بدون تأخير. واجهة سريعة تستجيب فوراً لأي أمر.",
            feature3Title: "مجموعات ذكية",
            feature3Desc: "أنشئ مجموعات دردشة مع أصدقائك. أدوات إدارة متقدمة وسهلة الاستخدام.",
            feature4Title: "مشاركة الوسائط",
            feature4Desc: "شارك الصور والفيديوهات والملفات بسهولة. دعم لكافة الصيغ الشائعة.",
            feature5Title: "وضع ليلي",
            feature5Desc: "وضع مظلم مريح للعين أثناء الليل. يتكامل مع نظام الجهاز تلقائياً.",
            feature6Title: "دعم عربي كامل",
            feature6Desc: "واجهة باللغة العربية مع دعم كامل للحروف والاتجاه. مناسب للمستخدم العربي.",
            securityTitle: "نظام الأمان المتقدم",
            security1Title: "حماية البيانات",
            security1Desc: "بياناتك تبقى على جهازك ولا نرسلها إلى سيرفرات خارجية. هذا يعني خصوصية كاملة.",
            security2Title: "هل سمعت من قبل عن اختراق؟",
            security2Desc: "لا داعي للقلق. نظامنا مبني على أساس عدم تخزين بيانات حساسة. لا توجد قاعدة بيانات مركزية يمكن اختراقها.",
            security3Title: "التحكم في الصلاحيات",
            security3Desc: "أنت تتحكم كاملاً في الصلاحيات. التطبيق لا يطلب صلاحيات غير ضرورية.",
            developersTitle: "فريق التطوير",
            dev1Title: "مطورون متمرسون",
            dev1Desc: "فريق من المطورين المتخصصين في برمجة تطبيقات التواصل والأمان.",
            dev2Title: "مصممو واجهات",
            dev2Desc: "مصممون محترفون يهتمون بتجربة المستخدم وسهولة الاستخدام.",
            dev3Title: "خبراء أمان",
            dev3Desc: "متخصصون في أمن المعلومات وحماية البيانات الرقمية.",
            faqTitle: "أسئلة شائعة",
            faq1Question: "كيف يعمل تطبيق Mocat؟",
            faq1AnswerText: "التطبيق يسمح لك بإنشاء حساب، إضافة أصدقاء، وإنشاء محادثات فردية أو جماعية. جميع الرسائل ترسل مشفرة وتظهر فوراً للمستقبل.",
            faq2Question: "هل المحادثات آمنة حقاً؟",
            faq2AnswerText: "نعم، نستخدم تشفير من طرف إلى طرف. هذا يعني أن الرسائل تتشفر على جهازك وتتشفر على جهاز المستقبل. لا يمكن قراءتها أثناء النقل.",
            faq3Question: "ما هي مميزات التطبيق؟",
            faq3AnswerText: "تطبيق Mocat يوفر تشفير كامل، سرعة عالية، مجموعات ذكية، مشاركة وسائط، وضع ليلي، ودعم عربي كامل لتجربة دردشة آمنة وسلسة.",
            faq4Question: "هل يمكن اختراق التطبيق؟",
            faq4AnswerText: "النظام مبني على مبدأ الأمان أولاً. لا نخزن بيانات حساسة على سيرفرات مركزية. حتى لو تم اختراق السيرفر، لن تصل للمحادثات لأنها مشفرة.",
            downloadTitle: "جاهز للبدء؟",
            downloadDesc: "حمل Mocat الآن وابدأ الدردشة الآمنة",
            downloadBtn: "تحميل التطبيق",
            footerText: "Mocat &copy; 2024 - تطبيق دردشة آمن",
            footerSubtext: "مصمم بحب لتوفير تواصل آمن للجميع",
            settingsTitle: "إعدادات التطبيق",
            infoTitle: "معلومات التطبيق",
            appNameLabel: "اسم التطبيق:",
            versionLabel: "الإصدار:",
            typeLabel: "النوع:",
            appType: "تطبيق دردشة",
            statusLabel: "الحالة:",
            appStatus: "تحت التطوير",
            themeTitle: "المظهر",
            languageTitle: "اللغة",
            aboutTitle: "حول التطبيق",
            aboutText: "Mocat هو تطبيق دردشة يركز على الأمان والخصوصية. تم تطويره باستخدام تقنيات حديثة تضمن حماية بيانات المستخدمين مع توفير تجربة استخدام سلسة."
        };
        
        // نصوص إنجليزية
        const englishTexts = {
            appTitle: "Mocat",
            appTagline: "Secure and fast chat app. Connect with your friends with complete privacy and advanced protection.",
            navFeatures: "Features",
            navDevelopers: "Developers",
            navSecurity: "Security",
            navSettings: "Settings",
            navFAQ: "FAQ",
            featuresTitle: "App Features",
            feature1Title: "Full Encryption",
            feature1Desc: "All conversations are encrypted end-to-end. No one can read your messages, not even us.",
            feature2Title: "High Speed",
            feature2Desc: "Send and receive messages instantly without delay. Fast interface that responds immediately to any command.",
            feature3Title: "Smart Groups",
            feature3Desc: "Create chat groups with your friends. Advanced and easy-to-use management tools.",
            feature4Title: "Media Sharing",
            feature4Desc: "Share photos, videos, and files easily. Support for all common formats.",
            feature5Title: "Night Mode",
            feature5Desc: "Dark mode comfortable for eyes at night. Integrates automatically with the device system.",
            feature6Title: "Full Arabic Support",
            feature6Desc: "Arabic interface with full support for Arabic letters and direction. Suitable for Arab users.",
            securityTitle: "Advanced Security System",
            security1Title: "Data Protection",
            security1Desc: "Your data stays on your device and we don't send it to external servers. This means complete privacy.",
            security2Title: "Ever heard of hacking?",
            security2Desc: "No need to worry. Our system is built on the principle of not storing sensitive data. There is no central database that can be hacked.",
            security3Title: "Permission Control",
            security3Desc: "You have full control over permissions. The app doesn't request unnecessary permissions.",
            developersTitle: "Development Team",
            dev1Title: "Experienced Developers",
            dev1Desc: "A team of developers specialized in programming communication and security applications.",
            dev2Title: "UI Designers",
            dev2Desc: "Professional designers who care about user experience and ease of use.",
            dev3Title: "Security Experts",
            dev3Desc: "Specialists in information security and digital data protection.",
            faqTitle: "Frequently Asked Questions",
            faq1Question: "How does Mocat app work?",
            faq1AnswerText: "The app allows you to create an account, add friends, and create individual or group conversations. All messages are sent encrypted and appear immediately to the recipient.",
            faq2Question: "Are conversations really secure?",
            faq2AnswerText: "Yes, we use end-to-end encryption. This means messages are encrypted on your device and decrypted on the recipient's device. They cannot be read during transmission.",
            faq3Question: "What are the app features?",
            faq3AnswerText: "Mocat app provides full encryption, high speed, smart groups, media sharing, night mode, and full Arabic support for a secure and smooth chatting experience.",
            faq4Question: "Can the app be hacked?",
            faq4AnswerText: "The system is built on the principle of security first. We don't store sensitive data on central servers. Even if the server is hacked, conversations won't be accessed because they are encrypted.",
            downloadTitle: "Ready to start?",
            downloadDesc: "Download Mocat now and start secure chatting",
            downloadBtn: "Download App",
            footerText: "Mocat &copy; 2024 - Secure Chat App",
            footerSubtext: "Designed with love to provide secure communication for everyone",
            settingsTitle: "App Settings",
            infoTitle: "App Information",
            appNameLabel: "App Name:",
            versionLabel: "Version:",
            typeLabel: "Type:",
            appType: "Chat Application",
            statusLabel: "Status:",
            appStatus: "Under Development",
            themeTitle: "Appearance",
            languageTitle: "Language",
            aboutTitle: "About",
            aboutText: "Mocat is a chat application that focuses on security and privacy. It was developed using modern technologies that ensure user data protection while providing a smooth user experience."
        };
        
        // التمرير للأقسام
        function scrollToSection(sectionId) {
            const section = document.getElementById(sectionId);
            if (section) {
                section.scrollIntoView({ behavior: 'smooth' });
            }
        }
        
        // فتح الإعدادات
        function openSettings() {
            document.getElementById('settingsModal').style.display = 'flex';
        }
        
        function closeSettings() {
            document.getElementById('settingsModal').style.display = 'none';
        }
        
        // فتح الأسئلة الشائعة
        function openFAQ() {
            scrollToSection('faq');
        }
        
        // تبديل الأسئلة
        function toggleFAQ(num) {
            const answer = document.getElementById('faq' + num + 'Answer');
            const icon = event.currentTarget.querySelector('i');
            
            if (answer.style.display === 'block') {
                answer.style.display = 'none';
                icon.className = 'fas fa-chevron-down';
                answer.style.animation = 'slideUpAnswer 0.3s ease-out';
            } else {
                answer.style.display = 'block';
                icon.className = 'fas fa-chevron-up';
                answer.style.animation = 'slideDownAnswer 0.3s ease-out';
            }
        }
        
        // تغيير المظهر
        function changeTheme(theme) {
            // إزالة كل الثيمات
            document.body.classList.remove('theme-white');
            
            // إزالة الكلاس النشط من جميع أزرار الثيمات
            document.querySelectorAll('.theme-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // تطبيق الثيم الجديد وإضافة الكلاس النشط
            if (theme === 'white') {
                document.body.classList.add('theme-white');
                document.getElementById('themeWhite').classList.add('active');
            } else {
                document.getElementById('themeDark').classList.add('active');
            }
            
            currentTheme = theme;
            
            // حفظ في التخزين المحلي
            localStorage.setItem('mocat-theme', theme);
        }
        
        // تغيير اللغة
        function changeLanguage(lang) {
            currentLanguage = lang;
            
            // تغيير اتجاه الصفحة
            if (lang === 'en') {
                document.documentElement.dir = 'ltr';
                document.documentElement.lang = 'en';
                document.body.style.textAlign = 'left';
            } else {
                document.documentElement.dir = 'rtl';
                document.documentElement.lang = 'ar';
                document.body.style.textAlign = 'right';
            }
            
            // تحديث حالة الأزرار النشطة
            document.querySelectorAll('.lang-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById('lang' + (lang === 'en' ? 'En' : 'Ar')).classList.add('active');
            
            // تحديث النصوص
            updateTexts(lang);
            
            // حفظ في التخزين المحلي
            localStorage.setItem('mocat-language', lang);
        }
        
        // تحديث النصوص
        function updateTexts(lang) {
            const texts = lang === 'en' ? englishTexts : arabicTexts;
            
            // تحديث كل النصوص
            for (const [key, value] of Object.entries(texts)) {
                const element = document.getElementById(key);
                if (element) {
                    element.textContent = value;
                }
            }
        }
        
        // تحميل التطبيق
        function downloadApp() {
            window.open('https://example.com/download/mocat', '_blank');
        }
        
        // عند التحميل
        document.addEventListener('DOMContentLoaded', function() {
            // تحميل التفضيلات المحفوظة
            const savedTheme = localStorage.getItem('mocat-theme');
            const savedLanguage = localStorage.getItem('mocat-language');
            
            // تطبيق المظهر
            if (savedTheme) {
                changeTheme(savedTheme);
            } else {
                // الافتراضي: داكن
                changeTheme('dark');
            }
            
            // تطبيق اللغة
            if (savedLanguage) {
                changeLanguage(savedLanguage);
            } else {
                // الافتراضي: عربي
                changeLanguage('ar');
            }
            
            // إغلاق الإعدادات بالضغط خارجها
            window.addEventListener('click', function(event) {
                const modal = document.getElementById('settingsModal');
                if (event.target === modal) {
                    closeSettings();
                }
            });
            
            // إغلاق بالزر ESC
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape') {
                    closeSettings();
                }
            });
            
            // تفعيل الانيميشن عند التمرير
            const sections = document.querySelectorAll('.section');
            const featureCards = document.querySelectorAll('.feature-card');
            const developerCards = document.querySelectorAll('.developer-card');
            const faqItems = document.querySelectorAll('.faq-item');
            
            function checkScroll() {
                sections.forEach(section => {
                    const sectionTop = section.getBoundingClientRect().top;
                    if (sectionTop < window.innerHeight - 100) {
                        section.style.animationPlayState = 'running';
                    }
                });
                
                featureCards.forEach(card => {
                    const cardTop = card.getBoundingClientRect().top;
                    if (cardTop < window.innerHeight - 100) {
                        card.style.animationPlayState = 'running';
                    }
                });
                
                developerCards.forEach(card => {
                    const cardTop = card.getBoundingClientRect().top;
                    if (cardTop < window.innerHeight - 100) {
                        card.style.animationPlayState = 'running';
                    }
                });
                
                faqItems.forEach(item => {
                    const itemTop = item.getBoundingClientRect().top;
                    if (itemTop < window.innerHeight - 100) {
                        item.style.animationPlayState = 'running';
                    }
                });
            }
            
            window.addEventListener('scroll', checkScroll);
            checkScroll(); // تشغيل فور التحميل
            
            console.log('موقع Mocat يعمل بنجاح');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("🚀 تشغيل موقع Mocat...")
    print("📍 افتح: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)