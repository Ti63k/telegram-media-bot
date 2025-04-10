import re
from config import PLATFORMS

def extract_platform_from_url(url):
    """
    استخراج اسم المنصة من الرابط
    
    Args:
        url (str): الرابط المراد تحليله
        
    Returns:
        str: اسم المنصة أو None إذا لم يتم التعرف على المنصة
    """
    url = url.lower()
    
    for platform, info in PLATFORMS.items():
        for pattern in info["url_patterns"]:
            if pattern in url:
                return platform
    
    return None

def clean_url(url):
    """
    تنظيف الرابط من أي معلمات تتبع أو معلمات غير ضرورية
    
    Args:
        url (str): الرابط المراد تنظيفه
        
    Returns:
        str: الرابط بعد التنظيف
    """
    # إزالة معلمات UTM وغيرها من معلمات التتبع
    url = re.sub(r'[?&]utm_[^&]*', '', url)
    
    # تنظيف روابط YouTube
    if 'youtube.com' in url or 'youtu.be' in url:
        # الاحتفاظ فقط بمعرف الفيديو
        if 'youtube.com/watch' in url:
            video_id = re.search(r'v=([^&]+)', url)
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id.group(1)}"
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0].split('#')[0]
            return f"https://www.youtube.com/watch?v={video_id}"
    
    # تنظيف روابط Instagram
    elif 'instagram.com' in url:
        # إزالة معلمات الاستعلام
        url = url.split('?')[0]
    
    # تنظيف روابط TikTok
    elif 'tiktok.com' in url:
        # الاحتفاظ بالرابط الأساسي فقط
        if 'vm.tiktok.com' in url:
            # تحويل الروابط المختصرة إلى الروابط الكاملة
            # سيتم التعامل مع هذا في وحدة التحميل
            pass
        else:
            # إزالة معلمات الاستعلام
            url = url.split('?')[0]
    
    # تنظيف روابط Twitter/X
    elif 'twitter.com' in url or 'x.com' in url:
        # إزالة معلمات الاستعلام
        url = url.split('?')[0]
    
    # تنظيف روابط Facebook
    elif 'facebook.com' in url or 'fb.com' in url or 'fb.watch' in url:
        # الاحتفاظ بالرابط الأساسي فقط
        # معالجة خاصة ستتم في وحدة التحميل
        pass
    
    return url

def is_valid_url(url):
    """
    التحقق من صحة الرابط
    
    Args:
        url (str): الرابط المراد التحقق منه
        
    Returns:
        bool: True إذا كان الرابط صحيحًا، False إذا لم يكن
    """
    # نمط بسيط للتحقق من صحة الرابط
    pattern = r'^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(/[^\s]*)?$'
    return bool(re.match(pattern, url))

def extract_video_id(url, platform):
    """
    استخراج معرف الفيديو من الرابط
    
    Args:
        url (str): الرابط المراد استخراج معرف الفيديو منه
        platform (str): اسم المنصة
        
    Returns:
        str: معرف الفيديو أو None إذا لم يتم استخراج المعرف
    """
    if platform == "youtube":
        # استخراج معرف فيديو YouTube
        if 'youtube.com/watch' in url:
            video_id = re.search(r'v=([^&]+)', url)
            if video_id:
                return video_id.group(1)
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0].split('#')[0]
    
    elif platform == "instagram":
        # استخراج معرف منشور Instagram
        if '/p/' in url:
            return url.split('/p/')[1].split('/')[0]
        elif '/reel/' in url:
            return url.split('/reel/')[1].split('/')[0]
        elif '/tv/' in url:
            return url.split('/tv/')[1].split('/')[0]
    
    elif platform == "tiktok":
        # استخراج معرف فيديو TikTok
        if '/video/' in url:
            return url.split('/video/')[1].split('?')[0].split('/')[0]
    
    elif platform == "twitter":
        # استخراج معرف تغريدة Twitter
        if '/status/' in url:
            return url.split('/status/')[1].split('?')[0].split('/')[0]
    
    elif platform == "facebook":
        # استخراج معرف منشور Facebook
        if '/videos/' in url:
            return url.split('/videos/')[1].split('?')[0].split('/')[0]
        elif 'fb.watch/' in url:
            return url.split('fb.watch/')[1].split('?')[0].split('/')[0]
    
    return None
