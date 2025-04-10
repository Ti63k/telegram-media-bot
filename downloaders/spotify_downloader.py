import os
import asyncio
import json
import re
from downloaders.base_downloader import BaseDownloader

class SpotifyDownloader(BaseDownloader):
    """
    وحدة تحميل الصوتيات من Spotify
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الصوتيات من رابط Spotify
        
        Args:
            url (str): رابط Spotify
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
            temp_filename = self._generate_temp_filename("spotify", ".mp3", download_folder)
            
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
                # إذا فشل التحميل المباشر، حاول البحث عن الأغنية على YouTube
                # استخراج معلومات الأغنية من الرابط
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
                    # تحليل معلومات الأغنية
                    track_info = json.loads(stdout.decode())
                    
                    # إضافة معلومات الوسائط
                    media_info["title"] = track_info.get("title", "")
                    media_info["author"] = track_info.get("uploader", "")
                    media_info["description"] = track_info.get("description", "")
                    
                    # البحث عن الأغنية على YouTube
                    search_query = f"{media_info['title']} {media_info['author']}"
                    
                    # استخدام yt-dlp للبحث عن الأغنية على YouTube
                    search_cmd = [
                        "yt-dlp",
                        "ytsearch1:" + search_query,
                        "--get-id",
                        "--no-warnings"
                    ]
                    
                    search_process = await asyncio.create_subprocess_exec(
                        *search_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await search_process.communicate()
                    
                    if search_process.returncode == 0 and stdout:
                        # الحصول على معرف الفيديو
                        video_id = stdout.decode().strip()
                        
                        if video_id:
                            # تحميل الأغنية من YouTube
                            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            download_cmd = [
                                "yt-dlp",
                                "--no-warnings",
                                "-f", "bestaudio",
                                "--extract-audio",
                                "--audio-format", "mp3",
                                "--audio-quality", "0",
                                "-o", temp_filename,
                                "--no-playlist",
                                youtube_url
                            ]
                            
                            download_process = await asyncio.create_subprocess_exec(
                                *download_cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            
                            stdout, stderr = await download_process.communicate()
                            
                            if download_process.returncode != 0:
                                raise Exception(f"فشل في تحميل الصوت من YouTube: {stderr.decode()}")
                        else:
                            raise Exception("لم يتم العثور على الأغنية على YouTube")
                    else:
                        raise Exception(f"فشل في البحث عن الأغنية على YouTube: {stderr.decode()}")
                else:
                    raise Exception(f"فشل في الحصول على معلومات الأغنية: {stderr.decode()}")
            else:
                # استخدام yt-dlp للحصول على معلومات الأغنية
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
                    # تحليل معلومات الأغنية
                    track_info = json.loads(stdout.decode())
                    
                    # إضافة معلومات الوسائط
                    media_info["title"] = track_info.get("title", "")
                    media_info["author"] = track_info.get("uploader", "")
                    media_info["description"] = track_info.get("description", "")
            
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
