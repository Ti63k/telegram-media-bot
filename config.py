import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env إذا كان موجودًا
load_dotenv()

# توكن البوت
BOT_TOKEN = "8006339119:AAFinBzThL-0P21KhphTKY_-QgldynCfPRk"

# قائمة المستخدمين المسموح لهم باستخدام البوت (Whitelist)
# يمكن تعديلها لاحقًا من خلال أوامر المشرف
ALLOWED_USERS = []  # قائمة فارغة تعني أن البوت متاح للجميع

# مسار قاعدة البيانات
DB_PATH = "bot_data.db"

# إعدادات التحميل
DOWNLOAD_FOLDER = "temp_downloads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 ميجابايت (الحد الأقصى لحجم الملف في تيليجرام)

# إعدادات المشرفين
ADMIN_USERS = []  # قائمة معرفات المشرفين

# رسائل البوت
BOT_MESSAGES = {
    "start": "مرحبًا بك في بوت تحميل الوسائط! 🎬\n\nأرسل لي رابطًا من Instagram أو TikTok أو YouTube أو Facebook أو Twitter أو Telegram أو SoundCloud أو Spotify وسأقوم بتحميل الوسائط وإرسالها إليك.\n\nاستخدم /help للحصول على مزيد من المعلومات.",
    "help": "كيفية استخدام البوت:\n\n1. أرسل رابطًا من أي من المنصات المدعومة.\n2. انتظر قليلاً ريثما أقوم بتحميل الوسائط.\n3. ستصلك الوسائط المطلوبة بأعلى جودة متاحة.\n\nالمنصات المدعومة:\n• Instagram (منشورات، ريلز، ستوريات، IGTV)\n• TikTok (فيديوهات بدون علامة مائية)\n• YouTube (فيديوهات، Shorts، صوت فقط)\n• Facebook (فيديوهات عامة)\n• Twitter/X (صور، فيديوهات)\n• Telegram (روابط لملفات أو منشورات عامة)\n• SoundCloud وSpotify (صوتيات)\n\nالأوامر المتاحة:\n/start - بدء استخدام البوت\n/help - عرض هذه المساعدة\n/about - معلومات عن البوت",
    "about": "بوت تحميل الوسائط v1.0\n\nبوت متعدد الوظائف لتحميل الوسائط من مختلف المنصات الاجتماعية وإرسالها مباشرة عبر تيليجرام.\n\nتم تطويره باستخدام Python وaiogram.",
    "processing": "جاري معالجة الرابط... ⏳",
    "download_success": "تم تحميل الوسائط بنجاح! جاري الإرسال... 📤",
    "download_error": "عذرًا، حدث خطأ أثناء تحميل الوسائط. يرجى التأكد من صحة الرابط والمحاولة مرة أخرى. 🚫",
    "unsupported_url": "عذرًا، الرابط غير مدعوم. يرجى التأكد من أن الرابط من إحدى المنصات المدعومة. 🚫",
    "access_denied": "عذرًا، ليس لديك صلاحية استخدام هذا البوت. 🔒",
    "file_too_large": "عذرًا، حجم الملف كبير جدًا. سيتم تقسيمه وإرساله على أجزاء. 📦",
}

# إعدادات المنصات
PLATFORMS = {
    "instagram": {
        "url_patterns": ["instagram.com", "instagr.am"],
        "module": "downloaders.instagram_downloader"
    },
    "tiktok": {
        "url_patterns": ["tiktok.com", "vm.tiktok.com"],
        "module": "downloaders.tiktok_downloader"
    },
    "youtube": {
        "url_patterns": ["youtube.com", "youtu.be"],
        "module": "downloaders.youtube_downloader"
    },
    "facebook": {
        "url_patterns": ["facebook.com", "fb.com", "fb.watch"],
        "module": "downloaders.facebook_downloader"
    },
    "twitter": {
        "url_patterns": ["twitter.com", "x.com"],
        "module": "downloaders.twitter_downloader"
    },
    "telegram": {
        "url_patterns": ["t.me", "telegram.me"],
        "module": "downloaders.telegram_downloader"
    },
    "soundcloud": {
        "url_patterns": ["soundcloud.com"],
        "module": "downloaders.soundcloud_downloader"
    },
    "spotify": {
        "url_patterns": ["spotify.com", "open.spotify.com"],
        "module": "downloaders.spotify_downloader"
    }
}
