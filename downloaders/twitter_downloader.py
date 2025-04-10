import os
import asyncio
import json
import re
from downloaders.base_downloader import BaseDownloader

class TwitterDownloader(BaseDownloader):
    """
    وحدة تحميل الوسائط من Twitter/X
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الوسائط من رابط Twitter/X
        
        Args:
            url (str): رابط Twitter/X
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
                "type": "unknown"  # سيتم تحديثه لاحقًا
            }
            
            # استخدام yt-dlp للحصول على معلومات التغريدة
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
                raise Exception(f"فشل في الحصول على معلومات التغريدة: {stderr.decode()}")
            
            # تحليل معلومات التغريدة
            tweet_info = json.loads(stdout.decode())
            
            # إضافة معلومات الوسائط
            media_info["title"] = tweet_info.get("title", "")
            media_info["author"] = tweet_info.get("uploader", "")
            media_info["description"] = tweet_info.get("description", "")
            
            # تحديد نوع الوسائط
            if tweet_info.get("extractor_key") == "TwitterSpaces":
                # إذا كانت مساحة صوتية
                media_info["type"] = "audio"
                temp_filename = self._generate_temp_filename("twitter_space", ".mp3", download_folder)
                
                # تحميل المساحة الصوتية
                download_cmd = [
                    "yt-dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "-o", temp_filename,
                    url
                ]
            else:
                # تحقق من وجود وسائط في التغريدة
                has_video = False
                has_image = False
                
                # تحقق من وجود فيديو
                if "formats" in tweet_info and tweet_info["formats"]:
                    has_video = True
                    media_info["type"] = "video"
                    temp_filename = self._generate_temp_filename("twitter_video", ".mp4", download_folder)
                    
                    # تحميل الفيديو
                    download_cmd = [
                        "yt-dlp",
                        "-f", "best",
                        "-o", temp_filename,
                        url
                    ]
                # تحقق من وجود صور
                elif "thumbnails" in tweet_info and tweet_info["thumbnails"]:
                    has_image = True
                    media_info["type"] = "photo"
                    
                    # تحميل الصور
                    for i, thumbnail in enumerate(tweet_info["thumbnails"]):
                        if "url" in thumbnail:
                            img_filename = self._generate_temp_filename(f"twitter_image_{i}", ".jpg", download_folder)
                            await self._download_file(thumbnail["url"], img_filename)
                            media_info["files"].append(img_filename)
                    
                    # إذا تم تحميل الصور بنجاح، أرجع النتيجة
                    if media_info["files"]:
                        return media_info
                    
                    # إذا لم يتم تحميل أي صور، حاول تحميل التغريدة كنص
                    media_info["type"] = "document"
                    temp_filename = self._generate_temp_filename("twitter_text", ".txt", download_folder)
                    
                    # كتابة نص التغريدة في ملف
                    with open(temp_filename, "w", encoding="utf-8") as f:
                        f.write(f"تغريدة من {tweet_info.get('uploader', 'مستخدم')}\n\n")
                        f.write(tweet_info.get("description", ""))
                    
                    media_info["files"].append(temp_filename)
                    return media_info
                else:
                    # إذا لم يكن هناك وسائط، حاول تحميل التغريدة كنص
                    media_info["type"] = "document"
                    temp_filename = self._generate_temp_filename("twitter_text", ".txt", download_folder)
                    
                    # كتابة نص التغريدة في ملف
                    with open(temp_filename, "w", encoding="utf-8") as f:
                        f.write(f"تغريدة من {tweet_info.get('uploader', 'مستخدم')}\n\n")
                        f.write(tweet_info.get("description", ""))
                    
                    media_info["files"].append(temp_filename)
                    return media_info
            
            # تنفيذ أمر التحميل (للفيديو أو الصوت)
            if "download_cmd" in locals():
                download_process = await asyncio.create_subprocess_exec(
                    *download_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await download_process.communicate()
                
                if download_process.returncode != 0:
                    raise Exception(f"فشل في تحميل الوسائط: {stderr.decode()}")
                
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
