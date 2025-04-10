import os
import asyncio
import json
import re
from downloaders.base_downloader import BaseDownloader

class FacebookDownloader(BaseDownloader):
    """
    وحدة تحميل الوسائط من Facebook
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الوسائط من رابط Facebook
        
        Args:
            url (str): رابط Facebook
            download_folder (str): مجلد التنزيل
            
        Returns:
            dict: معلومات الوسائط المحملة
        """
        try:
            # التأكد من وجود مجلد التنزيل
            os.makedirs(download_folder, exist_ok=True)
            
            # تحضير معلومات الوسائط
            media_info = {
                "url": url,
                "files": [],
                "type": "video"  # Facebook غالبًا ما يكون فيديو
            }
            
            # تحديد اسم الملف المؤقت
            temp_filename = self._generate_temp_filename("facebook", ".mp4", download_folder)
            
            # استخدام yt-dlp لتحميل الفيديو
            download_cmd = [
                "yt-dlp",
                "--no-warnings",
                "-f", "best",
                "-o", temp_filename,
                "--no-playlist",
                url
            ]
            
            # تنفيذ أمر التحميل
            download_process = await asyncio.create_subprocess_exec(
                *download_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await download_process.communicate()
            
            if download_process.returncode != 0:
                raise Exception(f"فشل في تحميل الفيديو: {stderr.decode()}")
            
            # استخدام yt-dlp للحصول على معلومات الفيديو
            info_cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                url
            ]
            
            info_process = await asyncio.create_subprocess_exec(
                *info_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await info_process.communicate()
            
            if info_process.returncode == 0:
                # تحليل معلومات الفيديو
                video_info = json.loads(stdout.decode())
                
                # إضافة معلومات الوسائط
                media_info["title"] = video_info.get("title", "")
                media_info["author"] = video_info.get("uploader", "")
                media_info["description"] = video_info.get("description", "")
            
            # إضافة الملف إلى قائمة الملفات
            media_info["files"].append(temp_filename)
            
            return media_info
        
        except Exception as e:
            # إرجاع معلومات الخطأ
            return {
                "url": url,
                "error": str(e),
                "files": []
            }
