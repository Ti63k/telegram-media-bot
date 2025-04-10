import os
import asyncio
import json
import re
import aiohttp
from downloaders.base_downloader import BaseDownloader

class TelegramDownloader(BaseDownloader):
    """
    وحدة تحميل الوسائط من Telegram
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الوسائط من رابط Telegram
        
        Args:
            url (str): رابط Telegram
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
            
            # تحليل الرابط
            if "t.me/c/" in url or "telegram.me/c/" in url:
                # رابط قناة خاصة، غير مدعوم حاليًا
                raise Exception("روابط القنوات الخاصة غير مدعومة حاليًا")
            
            # استخدام yt-dlp لتحميل الوسائط
            temp_filename = self._generate_temp_filename("telegram", ".unknown", download_folder)
            
            # تحميل الوسائط
            download_cmd = [
                "yt-dlp",
                "--no-warnings",
                "-f", "best",
                "-o", temp_filename,
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
                # إذا فشل التحميل باستخدام yt-dlp، حاول استخدام طريقة بديلة
                # للروابط العامة، يمكن استخدام API تيليجرام العامة
                
                # تحليل الرابط للحصول على معرف القناة والمنشور
                if "t.me/" in url or "telegram.me/" in url:
                    # استخراج اسم القناة ومعرف المنشور
                    parts = url.split("/")
                    channel_name = None
                    message_id = None
                    
                    for i, part in enumerate(parts):
                        if part == "t.me" or part == "telegram.me":
                            if i + 1 < len(parts):
                                channel_name = parts[i + 1]
                            if i + 2 < len(parts):
                                try:
                                    message_id = int(parts[i + 2])
                                except ValueError:
                                    pass
                    
                    if channel_name and message_id:
                        # استخدام API تيليجرام العامة للحصول على معلومات المنشور
                        api_url = f"https://t.me/{channel_name}/{message_id}?embed=1"
                        
                        async with aiohttp.ClientSession() as session:
                            async with session.get(api_url) as response:
                                if response.status == 200:
                                    html = await response.text()
                                    
                                    # البحث عن روابط الوسائط في HTML
                                    media_urls = re.findall(r'(https://cdn[0-9]\.telesco\.pe/file/[^"\']+)', html)
                                    
                                    if media_urls:
                                        for i, media_url in enumerate(media_urls):
                                            # تحديد نوع الملف
                                            if media_url.endswith(".jpg") or media_url.endswith(".jpeg") or media_url.endswith(".png"):
                                                ext = os.path.splitext(media_url)[1]
                                                file_path = self._generate_temp_filename(f"telegram_photo_{i}", ext, download_folder)
                                                media_info["type"] = "photo"
                                            elif media_url.endswith(".mp4") or media_url.endswith(".mov"):
                                                ext = os.path.splitext(media_url)[1]
                                                file_path = self._generate_temp_filename(f"telegram_video_{i}", ext, download_folder)
                                                media_info["type"] = "video"
                                            elif media_url.endswith(".mp3") or media_url.endswith(".ogg"):
                                                ext = os.path.splitext(media_url)[1]
                                                file_path = self._generate_temp_filename(f"telegram_audio_{i}", ext, download_folder)
                                                media_info["type"] = "audio"
                                            else:
                                                ext = os.path.splitext(media_url)[1] or ".bin"
                                                file_path = self._generate_temp_filename(f"telegram_file_{i}", ext, download_folder)
                                                media_info["type"] = "document"
                                            
                                            # تحميل الملف
                                            if await self._download_file(media_url, file_path):
                                                media_info["files"].append(file_path)
                                    
                                    # استخراج معلومات المنشور
                                    title_match = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
                                    if title_match:
                                        media_info["title"] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                                    
                                    author_match = re.search(r'<div class="tgme_widget_message_author[^>]*>(.*?)</div>', html, re.DOTALL)
                                    if author_match:
                                        media_info["author"] = re.sub(r'<[^>]+>', '', author_match.group(1)).strip()
                                    
                                    # إذا لم يتم العثور على وسائط، قم بحفظ المنشور كملف نصي
                                    if not media_info["files"]:
                                        text_file = self._generate_temp_filename("telegram_text", ".txt", download_folder)
                                        with open(text_file, "w", encoding="utf-8") as f:
                                            if "title" in media_info:
                                                f.write(media_info["title"])
                                        
                                        media_info["files"].append(text_file)
                                        media_info["type"] = "document"
                
                if not media_info["files"]:
                    raise Exception(f"فشل في تحميل الوسائط من تيليجرام: {stderr.decode()}")
            else:
                # تحديد نوع الملف بناءً على الامتداد
                for file in os.listdir(download_folder):
                    if file.startswith(os.path.basename(temp_filename.split('.')[0])):
                        file_path = os.path.join(download_folder, file)
                        media_info["files"].append(file_path)
                        media_info["type"] = self._get_file_type(file_path)
                
                # استخدام yt-dlp للحصول على معلومات الوسائط
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
                    # تحليل معلومات الوسائط
                    media_info_json = json.loads(stdout.decode())
                    
                    # إضافة معلومات الوسائط
                    media_info["title"] = media_info_json.get("title", "")
                    media_info["author"] = media_info_json.get("uploader", "")
                    media_info["description"] = media_info_json.get("description", "")
            
            return media_info
        
        except Exception as e:
            # إرجاع معلومات الخطأ
            return {
                "url": url,
                "error": str(e),
                "files": []
            }
