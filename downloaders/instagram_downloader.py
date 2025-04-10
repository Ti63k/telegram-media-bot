import os
import asyncio
import json
import re
import tempfile
import instaloader
from instaloader import Post, Profile, StoryItem
from downloaders.base_downloader import BaseDownloader

class InstagramDownloader(BaseDownloader):
    """
    وحدة تحميل الوسائط من Instagram
    """
    
    async def download(self, url, download_folder):
        """
        تحميل الوسائط من رابط Instagram
        
        Args:
            url (str): رابط Instagram
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
                "type": "photo"  # سيتم تحديثه لاحقًا إذا كان فيديو
            }
            
            # إنشاء كائن instaloader
            L = instaloader.Instaloader(
                dirname_pattern=download_folder,
                filename_pattern="{shortcode}_{target}",
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False
            )
            
            # تحديد نوع المحتوى (منشور، ريلز، ستوري، IGTV)
            if '/p/' in url:  # منشور عادي
                shortcode = url.split('/p/')[1].split('/')[0]
                post = Post.from_shortcode(L.context, shortcode)
                
                # تنفيذ التحميل في عملية منفصلة
                await self._download_post(L, post, download_folder, media_info)
                
            elif '/reel/' in url:  # ريلز
                shortcode = url.split('/reel/')[1].split('/')[0]
                post = Post.from_shortcode(L.context, shortcode)
                
                # تنفيذ التحميل في عملية منفصلة
                await self._download_post(L, post, download_folder, media_info)
                media_info["type"] = "video"
                
            elif '/tv/' in url or '/igtv/' in url:  # IGTV
                shortcode = url.split('/tv/')[1].split('/')[0] if '/tv/' in url else url.split('/igtv/')[1].split('/')[0]
                post = Post.from_shortcode(L.context, shortcode)
                
                # تنفيذ التحميل في عملية منفصلة
                await self._download_post(L, post, download_folder, media_info)
                media_info["type"] = "video"
                
            elif '/stories/' in url:  # ستوري
                # استخراج اسم المستخدم ومعرف الستوري
                username = url.split('/stories/')[1].split('/')[0]
                
                # تنفيذ التحميل في عملية منفصلة
                await self._download_story(L, username, download_folder, media_info)
            
            else:
                raise Exception("رابط Instagram غير مدعوم")
            
            return media_info
        
        except Exception as e:
            # إرجاع معلومات الخطأ
            return {
                "url": url,
                "error": str(e),
                "files": []
            }
    
    async def _download_post(self, loader, post, download_folder, media_info):
        """
        تحميل منشور Instagram
        
        Args:
            loader (instaloader.Instaloader): كائن instaloader
            post (instaloader.Post): كائن المنشور
            download_folder (str): مجلد التنزيل
            media_info (dict): معلومات الوسائط
        """
        # إضافة معلومات المنشور
        media_info["title"] = post.caption if post.caption else ""
        media_info["author"] = post.owner_username
        media_info["description"] = post.caption if post.caption else ""
        
        # تحديد ما إذا كان المنشور يحتوي على فيديو
        if post.is_video:
            media_info["type"] = "video"
        
        # تنفيذ التحميل في عملية منفصلة
        loop = asyncio.get_event_loop()
        
        def download_post():
            temp_files = []
            
            try:
                # تحميل المنشور
                if post.typename == "GraphSidecar":  # منشور متعدد الوسائط
                    for node in post.get_sidecar_nodes():
                        if node.is_video:
                            # تحميل الفيديو
                            filename = f"{post.shortcode}_{node.shortcode}.mp4"
                            file_path = os.path.join(download_folder, filename)
                            loader.download_video(node, post.owner_profile, filename=filename)
                            temp_files.append(file_path)
                            media_info["type"] = "video"
                        else:
                            # تحميل الصورة
                            filename = f"{post.shortcode}_{node.shortcode}.jpg"
                            file_path = os.path.join(download_folder, filename)
                            loader.download_pic(node, post.owner_profile, filename=filename)
                            temp_files.append(file_path)
                else:
                    # منشور فردي
                    if post.is_video:
                        # تحميل الفيديو
                        filename = f"{post.shortcode}.mp4"
                        file_path = os.path.join(download_folder, filename)
                        loader.download_video(post, post.owner_profile, filename=filename)
                        temp_files.append(file_path)
                        media_info["type"] = "video"
                    else:
                        # تحميل الصورة
                        filename = f"{post.shortcode}.jpg"
                        file_path = os.path.join(download_folder, filename)
                        loader.download_pic(post, post.owner_profile, filename=filename)
                        temp_files.append(file_path)
            
            except Exception as e:
                print(f"خطأ في تحميل المنشور: {e}")
            
            return temp_files
        
        # تنفيذ التحميل في عملية منفصلة
        files = await loop.run_in_executor(None, download_post)
        
        # إضافة الملفات إلى قائمة الملفات
        media_info["files"].extend(files)
    
    async def _download_story(self, loader, username, download_folder, media_info):
        """
        تحميل ستوري Instagram
        
        Args:
            loader (instaloader.Instaloader): كائن instaloader
            username (str): اسم المستخدم
            download_folder (str): مجلد التنزيل
            media_info (dict): معلومات الوسائط
        """
        # إضافة معلومات الستوري
        media_info["title"] = f"ستوري {username}"
        media_info["author"] = username
        media_info["description"] = f"ستوري من حساب {username}"
        
        # تنفيذ التحميل في عملية منفصلة
        loop = asyncio.get_event_loop()
        
        def download_story():
            temp_files = []
            
            try:
                # الحصول على ملف تعريف المستخدم
                profile = Profile.from_username(loader.context, username)
                
                # تحميل الستوريات
                for story in loader.get_stories([profile.userid]):
                    for item in story.get_items():
                        if item.is_video:
                            # تحميل الفيديو
                            filename = f"{username}_story_{item.mediaid}.mp4"
                            file_path = os.path.join(download_folder, filename)
                            loader.download_storyitem(item, filename=filename)
                            temp_files.append(file_path)
                            media_info["type"] = "video"
                        else:
                            # تحميل الصورة
                            filename = f"{username}_story_{item.mediaid}.jpg"
                            file_path = os.path.join(download_folder, filename)
                            loader.download_storyitem(item, filename=filename)
                            temp_files.append(file_path)
            
            except Exception as e:
                print(f"خطأ في تحميل الستوري: {e}")
            
            return temp_files
        
        # تنفيذ التحميل في عملية منفصلة
        files = await loop.run_in_executor(None, download_story)
        
        # إضافة الملفات إلى قائمة الملفات
        media_info["files"].extend(files)
