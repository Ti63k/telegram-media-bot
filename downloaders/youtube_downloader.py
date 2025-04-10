import os
import asyncio
import subprocess
import json
import re
from downloaders.base_downloader import BaseDownloader

class YouTubeDownloader(BaseDownloader):
    """
    وحدة تحميل الوسائط من YouTube
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الوسائط من رابط YouTube
        
        Args:
            url (str): رابط YouTube
            download_folder (str): مجلد التنزيل
            
        Returns:
            dict: معلومات الوسائط المحملة
        """
        try:
            # التأكد من وجود مجلد التنزيل
            os.makedirs(download_folder, exist_ok=True)
            
            # تحديد ما إذا كان المستخدم يريد تحميل الصوت فقط
            audio_only = False
            if url.endswith("audio"):
                audio_only = True
                url = url[:-6]  # إزالة "audio" من نهاية الرابط
            
            # تحضير معلومات الوسائط
            media_info = {
                "url": url,
                "files": [],
                "type": "audio" if audio_only else "video"
            }
            
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
            
            if info_process.returncode != 0:
                raise Exception(f"فشل في الحصول على معلومات الفيديو: {stderr.decode()}")
            
            # تحليل معلومات الفيديو
            video_info = json.loads(stdout.decode())
            
            # إضافة معلومات الوسائط
            media_info["title"] = video_info.get("title", "")
            media_info["author"] = video_info.get("uploader", "")
            media_info["description"] = video_info.get("description", "")
            
            # تحديد اسم الملف المؤقت
            temp_filename = self._generate_temp_filename(
                "youtube",
                ".mp3" if audio_only else ".mp4",
                download_folder
            )
            
            # تحضير أمر التحميل
            if audio_only:
                # تحميل الصوت فقط
                download_cmd = [
                    "yt-dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",
                    "-o", temp_filename,
                    "--no-playlist",
                    url
                ]
            else:
                # تحميل الفيديو
                download_cmd = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "-o", temp_filename,
                    "--no-playlist",
                    "--merge-output-format", "mp4",
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
