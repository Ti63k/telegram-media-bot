# دليل استخدام بوت تيليجرام متعدد الوظائف لتحميل الوسائط

## مقدمة

هذا الدليل يشرح كيفية استخدام وإعداد ونشر بوت تيليجرام متعدد الوظائف لتحميل الوسائط من مختلف المنصات. البوت يدعم تحميل الوسائط من:

- Instagram (منشورات، ريلز، ستوريات، IGTV)
- TikTok (فيديوهات بدقة عالية بدون علامة مائية)
- YouTube (فيديوهات، Shorts، تحميل الصوت فقط)
- Facebook (فيديوهات عامة)
- Twitter/X (صور، فيديوهات، وسائط متعددة)
- Telegram (روابط لملفات أو منشورات عامة)
- SoundCloud (صوتيات)
- Spotify (صوتيات)

## استخدام البوت

### الأوامر الأساسية

- `/start` - بدء استخدام البوت والحصول على رسالة ترحيبية
- `/help` - عرض قائمة الأوامر المتاحة ومعلومات المساعدة
- `/about` - عرض معلومات حول البوت والمطور

### تحميل الوسائط

لتحميل الوسائط، ما عليك سوى إرسال رابط من إحدى المنصات المدعومة إلى البوت. يمكنك إرسال عدة روابط في رسالة واحدة وسيقوم البوت بمعالجتها واحدًا تلو الآخر.

### أوامر المشرفين

إذا كنت مشرفًا للبوت، يمكنك استخدام الأوامر التالية:

- `/adduser [user_id]` - إضافة مستخدم إلى قائمة المستخدمين المسموح لهم
- `/removeuser [user_id]` - إزالة مستخدم من قائمة المستخدمين المسموح لهم
- `/listusers` - عرض قائمة المستخدمين المسموح لهم

## إعداد البوت محليًا

### المتطلبات الأساسية

- Python 3.8 أو أحدث
- pip (مدير حزم Python)
- ffmpeg (للتعامل مع ملفات الوسائط)

### خطوات الإعداد

1. قم بتنزيل أو استنساخ المشروع:
   ```bash
   git clone https://github.com/Ti63k/telegram-media-bot.git
   cd telegram-media-bot
   ```

2. قم بإنشاء بيئة افتراضية (اختياري ولكن موصى به):
   ```bash
   python -m venv venv
   source venv/bin/activate  # على Linux/macOS
   venv\Scripts\activate  # على Windows
   ```

3. قم بتثبيت المتطلبات:
   ```bash
   pip install -r requirements.txt
   ```

4. قم بتعديل ملف `config.py` لإضافة توكن البوت الخاص بك ومعرف المشرف:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ADMIN_USER_ID = YOUR_TELEGRAM_ID_HERE
   ```

5. قم بإنشاء مجلد للتنزيلات المؤقتة (إذا لم يكن موجودًا):
   ```bash
   mkdir temp_downloads
   ```

6. قم بتشغيل البوت:
   ```bash
   python main.py
   ```

## نشر البوت على منصات الاستضافة

### نشر البوت على GitHub

تم بالفعل نشر البوت على GitHub في المستودع التالي:
https://github.com/Ti63k/telegram-media-bot

### نشر البوت على Replit

1. قم بإنشاء حساب على [Replit](https://replit.com/) إذا لم يكن لديك حساب بالفعل.
2. انقر على "Create Repl" وحدد "Import from GitHub".
3. أدخل عنوان المستودع: `https://github.com/Ti63k/telegram-media-bot`
4. انقر على "Import from GitHub".
5. بعد استيراد المشروع، قم بإنشاء ملف `.replit` بالمحتوى التالي:
   ```
   language = "python3"
   run = "python main.py"
   ```
6. قم بإنشاء ملف `pyproject.toml` بالمحتوى التالي:
   ```toml
   [tool.poetry]
   name = "telegram-media-bot"
   version = "1.0.0"
   description = "بوت تيليجرام متعدد الوظائف لتحميل الوسائط"
   authors = ["Your Name <your.email@example.com>"]

   [tool.poetry.dependencies]
   python = "^3.8"
   python-telegram-bot = "20.6"
   aiogram = "3.2.0"
   yt-dlp = "2023.11.16"
   instaloader = "4.10.1"
   requests = "2.31.0"
   aiohttp = "3.9.1"
   beautifulsoup4 = "4.12.2"
   ffmpeg-python = "0.2.0"
   python-dotenv = "1.0.0"

   [build-system]
   requires = ["poetry-core>=1.0.0"]
   build-backend = "poetry.core.masonry.api"
   ```
7. قم بإنشاء ملف `secrets.toml` وأضف توكن البوت الخاص بك:
   ```toml
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
8. انقر على زر "Run" لتشغيل البوت.

### نشر البوت على Render

1. قم بإنشاء حساب على [Render](https://render.com/) إذا لم يكن لديك حساب بالفعل.
2. انقر على "New" ثم اختر "Web Service".
3. اختر "Build and deploy from a Git repository".
4. اختر GitHub كمصدر للمستودع وقم بتوصيل حسابك.
5. حدد مستودع `telegram-media-bot`.
6. قم بتعيين الإعدادات التالية:
   - Name: telegram-media-bot
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
7. أضف متغير البيئة `BOT_TOKEN` وقيمته توكن البوت الخاص بك.
8. انقر على "Create Web Service".

## استكشاف الأخطاء وإصلاحها

### مشاكل شائعة وحلولها

1. **البوت لا يستجيب**:
   - تأكد من أن توكن البوت صحيح.
   - تأكد من أن البوت قيد التشغيل.
   - تحقق من سجلات الأخطاء للحصول على مزيد من المعلومات.

2. **فشل تحميل الوسائط**:
   - تأكد من أن الرابط صحيح ومن منصة مدعومة.
   - تأكد من أن المحتوى عام وليس خاص.
   - تحقق من تثبيت ffmpeg بشكل صحيح.

3. **مشاكل في التثبيت**:
   - تأكد من تثبيت جميع المتطلبات باستخدام `pip install -r requirements.txt`.
   - تأكد من استخدام إصدار Python المدعوم (3.8 أو أحدث).

## الخاتمة

تهانينا! لقد قمت بإعداد ونشر بوت تيليجرام متعدد الوظائف لتحميل الوسائط. يمكنك الآن استخدام البوت لتحميل الوسائط من مختلف المنصات بسهولة.

إذا كان لديك أي أسئلة أو مشاكل، يرجى فتح مشكلة في مستودع GitHub أو التواصل مع المطور.

## روابط مفيدة

- [مستودع GitHub للمشروع](https://github.com/Ti63k/telegram-media-bot)
- [وثائق API تيليجرام للبوتات](https://core.telegram.org/bots/api)
- [وثائق python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [وثائق aiogram](https://docs.aiogram.dev/)
