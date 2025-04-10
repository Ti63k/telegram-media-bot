import os
import asyncio
import json
import re
from downloaders.base_downloader import BaseDownloader

class SoundCloudDownloader(BaseDownloader):
    """
    وحدة تحميل الصوتيات من SoundCloud
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الصوتيات من رابط SoundCloud
        
        Args:
            url (str): رابط SoundCloud
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
                "type": "audio"
            }
            
            # تحديد اسم الملف المؤقت
            temp_filename = self._generate_temp_filename("soundcloud", ".mp3", download_folder)
            
            # استخدام yt-dlp لتحميل الصوت
            download_cmd = [
                "yt-dlp",
                "--no-warnings",
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
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
                raise Exception(f"فشل في تحميل الصوت: {stderr.decode()}")
            
            # استخدام yt-dlp للحصول على معلومات الصوت
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
                # تحليل معلومات الصوت
                audio_info = json.loads(stdout.decode())
                
                # إضافة معلومات الوسائط
                media_info["title"] = audio_info.get("title", "")
                media_info["author"] = audio_info.get("uploader", "")
                media_info["description"] = audio_info.get("description", "")
            
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
