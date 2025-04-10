import os
import asyncio
import aiohttp
import re
import json
import tempfile
from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    """
    الفئة الأساسية لجميع وحدات التحميل
    """
    
    @abstractmethod
    async def download(self, url, download_folder):
        """
        تحميل الوسائط من الرابط
        
        Args:
            url (str): الرابط المراد تحميل الوسائط منه
            download_folder (str): مجلد التنزيل
            
        Returns:
            dict: معلومات الوسائط المحملة
        """
        pass
    
    async def _download_file(self, url, file_path):
        """
        تحميل ملف من رابط
        
        Args:
            url (str): رابط الملف
            file_path (str): مسار حفظ الملف
            
        Returns:
            bool: True إذا تم التحميل بنجاح، False إذا لم يتم
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        return True
                    return False
        except Exception:
            return False
    
    def _get_file_type(self, file_path):
        """
        تحديد نوع الملف بناءً على امتداده
        
        Args:
            file_path (str): مسار الملف
            
        Returns:
            str: نوع الملف (photo, video, audio, document)
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return "photo"
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return "video"
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            return "audio"
        else:
            return "document"
    
    def _generate_temp_filename(self, prefix, ext, download_folder):
        """
        إنشاء اسم ملف مؤقت
        
        Args:
            prefix (str): بادئة اسم الملف
            ext (str): امتداد الملف
            download_folder (str): مجلد التنزيل
            
        Returns:
            str: مسار الملف المؤقت
        """
        # التأكد من وجود مجلد التنزيل
        os.makedirs(download_folder, exist_ok=True)
        
        # إنشاء اسم ملف فريد
        filename = f"{prefix}_{os.urandom(4).hex()}{ext}"
        return os.path.join(download_folder, filename)
