import sqlite3
from config import DB_PATH

def init_db():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول اللازمة إذا لم تكن موجودة
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # إنشاء جدول المستخدمين المسموح لهم
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS allowed_users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        added_by INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # إنشاء جدول سجل التحميل
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS download_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        platform TEXT,
        url TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def is_user_allowed(user_id):
    """
    التحقق مما إذا كان المستخدم مسموحًا له باستخدام البوت
    
    Args:
        user_id (int): معرف المستخدم في تيليجرام
        
    Returns:
        bool: True إذا كان المستخدم مسموحًا له، False إذا لم يكن
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # التحقق من وجود المستخدم في قاعدة البيانات
    cursor.execute("SELECT user_id FROM allowed_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    # إذا كانت قائمة المستخدمين المسموح لهم فارغة، فالجميع مسموح لهم
    if not result:
        from config import ALLOWED_USERS
        if not ALLOWED_USERS:
            return True
        return False
    
    return True

def add_allowed_user(user_id, username=None, added_by=None):
    """
    إضافة مستخدم إلى قائمة المستخدمين المسموح لهم
    
    Args:
        user_id (int): معرف المستخدم في تيليجرام
        username (str, optional): اسم المستخدم
        added_by (int, optional): معرف المستخدم الذي أضاف هذا المستخدم
        
    Returns:
        bool: True إذا تمت الإضافة بنجاح، False إذا لم تتم
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO allowed_users (user_id, username, added_by) VALUES (?, ?, ?)",
            (user_id, username, added_by)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def remove_allowed_user(user_id):
    """
    إزالة مستخدم من قائمة المستخدمين المسموح لهم
    
    Args:
        user_id (int): معرف المستخدم في تيليجرام
        
    Returns:
        bool: True إذا تمت الإزالة بنجاح، False إذا لم تتم
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM allowed_users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def log_download(user_id, platform, url, status):
    """
    تسجيل عملية تحميل في قاعدة البيانات
    
    Args:
        user_id (int): معرف المستخدم في تيليجرام
        platform (str): المنصة التي تم التحميل منها
        url (str): الرابط الذي تم تحميله
        status (str): حالة التحميل (نجاح/فشل)
        
    Returns:
        bool: True إذا تم التسجيل بنجاح، False إذا لم يتم
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO download_logs (user_id, platform, url, status) VALUES (?, ?, ?, ?)",
            (user_id, platform, url, status)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_download_stats():
    """
    الحصول على إحصائيات التحميل
    
    Returns:
        dict: قاموس يحتوي على إحصائيات التحميل
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # إجمالي عدد التحميلات
        cursor.execute("SELECT COUNT(*) FROM download_logs")
        total_downloads = cursor.fetchone()[0]
        
        # عدد التحميلات الناجحة
        cursor.execute("SELECT COUNT(*) FROM download_logs WHERE status = 'success'")
        successful_downloads = cursor.fetchone()[0]
        
        # عدد التحميلات حسب المنصة
        cursor.execute("SELECT platform, COUNT(*) FROM download_logs GROUP BY platform")
        platform_stats = {platform: count for platform, count in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total": total_downloads,
            "successful": successful_downloads,
            "by_platform": platform_stats
        }
    except Exception:
        return {
            "total": 0,
            "successful": 0,
            "by_platform": {}
        }
