from flask import Flask, render_template_string

app = Flask(__name__)

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
        }
        
        body {
            font-family: system-ui, sans-serif;
            background: #0f172a;
            color: #f1f5f9;
            line-height: 1.6;
        }
        
        /* الهيدر مع الصورة */
        .header {
            height: 70vh;
            background: linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.9)),
                        url('https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1600&q=80');
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
        }
        
        .header-content {
            max-width: 800px;
            padding: 2rem;
        }
        
        .app-logo {
            font-size: 4rem;
            color: #60a5fa;
            margin-bottom: 1rem;
        }
        
        .app-title {
            font-size: 3rem;
            color: white;
            margin-bottom: 1rem;
        }
        
        .app-tagline {
            font-size: 1.2rem;
            color: #cbd5e1;
            max-width: 600px;
            margin: 0 auto;
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
        
        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
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
        }
        
        .section-title {
            font-size: 2rem;
            color: #60a5fa;
            margin-bottom: 2rem;
            text-align: center;
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
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: #60a5fa;
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
        }
        
        .faq-question {
            padding: 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1e293b;
        }
        
        .faq-answer {
            padding: 1.5rem;
            border-top: 1px solid #334155;
            display: none;
            background: #0f172a;
        }
        
        /* المطورون */
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
        
        /* زر التحميل */
        .download-section {
            text-align: center;
            padding: 3rem;
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            border-radius: 20px;
            margin: 3rem 0;
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
        }
        
        .download-btn:hover {
            background: #f8fafc;
        }
        
        /* التذييل */
        footer {
            text-align: center;
            padding: 3rem;
            color: #94a3b8;
            border-top: 1px solid #334155;
            margin-top: 4rem;
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
        }
    </style>
</head>
<body>
    <!-- الهيدر مع الصورة -->
    <header class="header">
        <div class="header-content">
            <div class="app-logo">
                <i class="fas fa-comment-dots"></i>
            </div>
            <h1 class="app-title">Mocat</h1>
            <p class="app-tagline">
                تطبيق دردشة آمن وسريع. تواصل مع أصدقائك بخصوصية تامة وحماية متقدمة.
            </p>
        </div>
    </header>

    <!-- التنقل -->
    <nav class="nav">
        <button class="nav-btn" onclick="scrollToSection('features')">
            <i class="fas fa-star"></i>
            <span>المميزات</span>
        </button>
        <button class="nav-btn" onclick="scrollToSection('developers')">
            <i class="fas fa-users"></i>
            <span>المطورون</span>
        </button>
        <button class="nav-btn" onclick="scrollToSection('security')">
            <i class="fas fa-shield-alt"></i>
            <span>الأمان</span>
        </button>
        <button class="nav-btn" onclick="openSettings()">
            <i class="fas fa-cog"></i>
            <span>الإعدادات</span>
        </button>
        <button class="nav-btn" onclick="openFAQ()">
            <i class="fas fa-question-circle"></i>
            <span>أسئلة شائعة</span>
        </button>
    </nav>

    <!-- المحتوى الرئيسي -->
    <div class="container">
        <!-- مميزات -->
        <section id="features" class="section">
            <h2 class="section-title">مميزات التطبيق</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                    <h3>تشفير كامل</h3>
                    <p>جميع المحادثات مشفرة من البداية إلى النهاية. لا يمكن لأي شخص قراءة رسائلك، حتى نحن.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <h3>سرعة عالية</h3>
                    <p>إرسال واستقبال الرسائل فورياً بدون تأخير. واجهة سريعة تستجيب فوراً لأي أمر.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-user-group"></i>
                    </div>
                    <h3>مجموعات ذكية</h3>
                    <p>أنشئ مجموعات دردشة مع أصدقائك. أدوات إدارة متقدمة وسهلة الاستخدام.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-image"></i>
                    </div>
                    <h3>مشاركة الوسائط</h3>
                    <p>شارك الصور والفيديوهات والملفات بسهولة. دعم لكافة الصيغ الشائعة.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-moon"></i>
                    </div>
                    <h3>وضع ليلي</h3>
                    <p>وضع مظلم مريح للعين أثناء الليل. يتكامل مع نظام الجهاز تلقائياً.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-language"></i>
                    </div>
                    <h3>دعم عربي كامل</h3>
                    <p>واجهة باللغة العربية مع دعم كامل للحروف والاتجاه. مناسب للمستخدم العربي.</p>
                </div>
            </div>
        </section>

        <!-- الأمان -->
        <section id="security" class="section">
            <h2 class="section-title">نظام الأمان المتقدم</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <h3>حماية البيانات</h3>
                    <p>بياناتك تبقى على جهازك ولا نرسلها إلى سيرفرات خارجية. هذا يعني خصوصية كاملة.</p>
                </div>
                
                <div class="feature-card">
                    <h3>هل سمعت من قبل عن اختراق؟</h3>
                    <p>لا داعي للقلق. نظامنا مبني على أساس عدم تخزين بيانات حساسة. لا توجد قاعدة بيانات مركزية يمكن اختراقها.</p>
                </div>
                
                <div class="feature-card">
                    <h3>التحكم في الصلاحيات</h3>
                    <p>أنت تتحكم كاملاً في الصلاحيات. التطبيق لا يطلب صلاحيات غير ضرورية.</p>
                </div>
            </div>
        </section>

        <!-- المطورون -->
        <section id="developers" class="section">
            <h2 class="section-title">فريق التطوير</h2>
            <div class="developers-grid">
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="fas fa-code"></i>
                    </div>
                    <h3>مطورون متمرسون</h3>
                    <p>فريق من المطورين المتخصصين في برمجة تطبيقات التواصل والأمان.</p>
                </div>
                
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="fas fa-palette"></i>
                    </div>
                    <h3>مصممو واجهات</h3>
                    <p>مصممون محترفون يهتمون بتجربة المستخدم وسهولة الاستخدام.</p>
                </div>
                
                <div class="developer-card">
                    <div class="dev-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>خبراء أمان</h3>
                    <p>متخصصون في أمن المعلومات وحماية البيانات الرقمية.</p>
                </div>
            </div>
        </section>

        <!-- الأسئلة الشائعة -->
        <section id="faq" class="section">
            <h2 class="section-title">أسئلة شائعة</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(1)">
                        <span>كيف يعمل تطبيق Mocat؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq1">
                        التطبيق يسمح لك بإنشاء حساب، إضافة أصدقاء، وإنشاء محادثات فردية أو جماعية. جميع الرسائل ترسل مشفرة وتظهر فوراً للمستقبل.
                    </div>
                </div>
                
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(2)">
                        <span>هل المحادثات آمنة حقاً؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq2">
                        نعم، نستخدم تشفير من طرف إلى طرف. هذا يعني أن الرسائل تتشفر على جهازك وتتشفر على جهاز المستقبل. لا يمكن قراءتها أثناء النقل.
                    </div>
                </div>
                
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(3)">
                        <span>ما هي مسزات التطبيق؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq3">
                        المسزات (الامتيازات) التي يطلبها التطبيق هي فقط ما يحتاجه للعمل: الوصول للشبكة لإرسال الرسائل، التخزين لحفظ المحادثات، والميكروفون للمكالمات الصوتية.
                    </div>
                </div>
                
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFAQ(4)">
                        <span>هل يمكن اختراق التطبيق؟</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer" id="faq4">
                        النظام مبني على مبدأ الأمان أولاً. لا نخزن بيانات حساسة على سيرفرات مركزية. حتى لو تم اختراق السيرفر، لن تصل للمحادثات لأنها مشفرة.
                    </div>
                </div>
            </div>
        </section>

        <!-- التحميل -->
        <section class="download-section">
            <h2 style="font-size: 2rem; margin-bottom: 1rem;">جاهز للبدء؟</h2>
            <p style="font-size: 1.1rem; margin-bottom: 1rem;">حمل Mocat الآن وابدأ الدردشة الآمنة</p>
            <button class="download-btn" onclick="downloadApp()">
                <i class="fas fa-download"></i> تحميل التطبيق
            </button>
        </section>
    </div>

    <!-- التذييل -->
    <footer>
        <p>Mocat &copy; 2024 - تطبيق دردشة آمن</p>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: #64748b;">
            مصمم بحب لتوفير تواصل آمن للجميع
        </p>
    </footer>

    <!-- نافذة الإعدادات -->
    <div id="settingsModal" class="settings-modal">
        <div class="settings-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2 style="color: #60a5fa;">
                    <i class="fas fa-cog"></i> إعدادات التطبيق
                </h2>
                <button onclick="closeSettings()" style="background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer;">
                    ×
                </button>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-info-circle"></i> معلومات التطبيق
                </h3>
                <div class="setting-item">
                    <strong>اسم التطبيق:</strong> Mocat<br>
                    <strong>الإصدار:</strong> 1.0.0<br>
                    <strong>النوع:</strong> تطبيق دردشة<br>
                    <strong>الحجم:</strong> 15 ميجابايت
                </div>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-palette"></i> المظهر
                </h3>
                <div class="setting-item">
                    <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                        <button onclick="changeTheme('dark')" style="padding: 0.5rem 1rem; background: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px; cursor: pointer;">
                            داكن
                        </button>
                        <button onclick="changeTheme('blue')" style="padding: 0.5rem 1rem; background: #1e40af; color: white; border: none; border-radius: 6px; cursor: pointer;">
                            أزرق
                        </button>
                        <button onclick="changeTheme('gray')" style="padding: 0.5rem 1rem; background: #475569; color: white; border: none; border-radius: 6px; cursor: pointer;">
                            رمادي
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-shield-alt"></i> الخصوصية
                </h3>
                <div class="setting-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>حفظ سجل المحادثات</span>
                        <input type="checkbox" checked style="width: 20px; height: 20px;">
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <span>إشعارات الرسائل</span>
                        <input type="checkbox" checked style="width: 20px; height: 20px;">
                    </div>
                </div>
            </div>
            
            <div class="settings-section">
                <h3 style="margin-bottom: 1rem; color: #cbd5e1;">
                    <i class="fas fa-book"></i> شرح التطبيق
                </h3>
                <div class="setting-item">
                    <p style="color: #94a3b8;">
                        Mocat هو تطبيق دردشة يركز على الأمان والخصوصية. تم تطويره باستخدام تقنيات حديثة تضمن حماية بيانات المستخدمين مع توفير تجربة استخدام سلسة.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
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
            const answer = document.getElementById('faq' + num);
            const icon = event.currentTarget.querySelector('i');
            
            if (answer.style.display === 'block') {
                answer.style.display = 'none';
                icon.className = 'fas fa-chevron-down';
            } else {
                answer.style.display = 'block';
                icon.className = 'fas fa-chevron-up';
            }
        }
        
        // تغيير الثيم
        function changeTheme(theme) {
            if (theme === 'blue') {
                document.body.style.backgroundColor = '#0c4a6e';
                document.body.style.color = '#e0f2fe';
            } else if (theme === 'gray') {
                document.body.style.backgroundColor = '#1f2937';
                document.body.style.color = '#f9fafb';
            } else {
                document.body.style.backgroundColor = '#0f172a';
                document.body.style.color = '#f1f5f9';
            }
        }
        
        // تحميل التطبيق
        function downloadApp() {
            window.open('https://example.com/download/mocat', '_blank');
        }
        
        // عند التحميل
        document.addEventListener('DOMContentLoaded', function() {
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