from flask import Flask, render_template_string

app = Flask(__name__)

# بيانات الصور مع وصف وتفاصيل إضافية
photos = [
    {
        "id": 1,
        "src": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
        "alt": "منظر طبيعي جبلي",
        "title": "جبال الشمال",
        "description": "منظر خلوي لقمم جبلية مغطاة بالثلوج في فصل الشتاء.",
        "location": "سويسرا",
        "date": "2024-01-15"
    },
    {
        "id": 2,
        "src": "https://images.unsplash.com/photo-1518837695005-2083093ee35b",
        "alt": "شاطئ استوائي",
        "title": "شاطئ الجنة",
        "description": "مياه فيروزية ورمال بيضاء تحت أشعة الشمس الاستوائية.",
        "location": "جزر المالديف",
        "date": "2024-02-20"
    },
    {
        "id": 3,
        "src": "https://images.unsplash.com/photo-1519681393784-d120267933ba",
        "alt": "مدينة حديثة ليلاً",
        "title": "أضواء المدينة",
        "description": "أفق المدينة يتلألأ بأنوار ناطحات السحاب في الليل.",
        "location": "دبي",
        "date": "2024-03-10"
    }
]

html_template = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>معرض الصور الاحترافي</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00c6ff, #0072ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 5px 15px rgba(0, 114, 255, 0.3);
        }
        
        .subtitle {
            color: #aaa;
            font-size: 1.2rem;
        }
        
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
        }
        
        .photo-card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s ease;
            position: relative;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .photo-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            border-color: rgba(0, 198, 255, 0.5);
        }
        
        /* الإطار حول الصورة */
        .image-frame {
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .image-frame img {
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 12px;
            display: block;
            border: 3px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s;
        }
        
        .photo-card:hover .image-frame img {
            border-color: #00c6ff;
            transform: scale(1.02);
        }
        
        /* زر المعلومات */
        .info-btn {
            position: absolute;
            top: 30px;
            left: 30px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            transition: all 0.3s;
            z-index: 10;
        }
        
        .info-btn:hover {
            background: #0072ff;
            transform: scale(1.1);
        }
        
        /* معلومات إضافية (تظهر عند الضغط على الزر) */
        .extra-info {
            display: none;
            padding: 15px;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            margin-top: 10px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .info-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            color: #ccc;
        }
        
        .info-item i {
            margin-left: 10px;
            color: #00c6ff;
            width: 20px;
        }
        
        /* تفاصيل الصورة */
        .details {
            padding: 20px;
        }
        
        .photo-title {
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: #fff;
            display: flex;
            align-items: center;
        }
        
        .photo-title i {
            margin-left: 10px;
            color: #00c6ff;
        }
        
        .description {
            color: #aaa;
            line-height: 1.6;
            margin-bottom: 15px;
            font-size: 1rem;
        }
        
        footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #777;
            font-size: 0.9rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        @media (max-width: 768px) {
            .gallery {
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            }
            
            h1 {
                font-size: 2.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-camera-retro"></i> معرض الصور الاحترافي</h1>
            <p class="subtitle">تصميم تفاعلي مع إطارات وزر معلومات | تجربة مستخدم محسّنة</p>
        </header>
        
        <div class="gallery">
            {% for photo in photos %}
            <div class="photo-card" id="card-{{ photo.id }}">
                <div class="image-frame">
                    <button class="info-btn" onclick="toggleInfo({{ photo.id }})" title="معلومات إضافية">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <img src="{{ photo.src }}" alt="{{ photo.alt }}" loading="lazy">
                </div>
                
                <div class="details">
                    <h3 class="photo-title">
                        <i class="fas fa-image"></i> {{ photo.title }}
                    </h3>
                    <p class="description">{{ photo.description }}</p>
                    
                    <!-- المعلومات الإضافية (مخفية بالافتراضي) -->
                    <div class="extra-info" id="info-{{ photo.id }}">
                        <div class="info-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>الموقع: {{ photo.location }}</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-calendar-alt"></i>
                            <span>التاريخ: {{ photo.date }}</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-id-card"></i>
                            <span>رقم الصورة: #{{ photo.id }}</span>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <footer>
            <p>تم التصميم باستخدام Flask & HTML/CSS | جميع الصور من Unsplash</p>
            <p>© 2024 معرض صور تجريبي | نسخة تطويرية</p>
        </footer>
    </div>
    
    <script>
        // دالة لإظهار/إخفاء المعلومات الإضافية
        function toggleInfo(photoId) {
            const infoDiv = document.getElementById('info-' + photoId);
            const card = document.getElementById('card-' + photoId);
            
            if (infoDiv.style.display === 'block') {
                infoDiv.style.display = 'none';
                card.style.transform = 'translateY(0)';
            } else {
                infoDiv.style.display = 'block';
                card.style.transform = 'translateY(-10px)';
            }
        }
        
        // إضافة تأثير عند التحميل
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.photo-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'opacity 0.5s, transform 0.5s';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 200);
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_template, photos=photos)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)