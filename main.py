import os
import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from aiogram.utils.markdown import hbold
import re

from config import BOT_TOKEN, BOT_MESSAGES, DOWNLOAD_FOLDER, ALLOWED_USERS, DB_PATH, PLATFORMS, ADMIN_USERS
from utils.url_utils import extract_platform_from_url, clean_url, is_valid_url
from utils.db_utils import init_db, is_user_allowed, add_allowed_user, remove_allowed_user, log_download, get_download_stats

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء مجلد التنزيلات المؤقتة إذا لم يكن موجودًا
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# إنشاء البوت والمرسل
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# تهيئة قاعدة البيانات
init_db()

# التحقق من صلاحية المستخدم
async def check_user_access(message: types.Message):
    user_id = message.from_user.id
    if ALLOWED_USERS and not is_user_allowed(user_id):
        await message.answer(BOT_MESSAGES["access_denied"])
        return False
    return True

# معالج أمر البدء
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not await check_user_access(message):
        return
    
    # إضافة المستخدم إلى قاعدة البيانات إذا لم يكن موجودًا
    user_id = message.from_user.id
    username = message.from_user.username
    add_allowed_user(user_id, username)
    
    await message.answer(BOT_MESSAGES["start"])

# معالج أمر المساعدة
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    if not await check_user_access(message):
        return
    
    await message.answer(BOT_MESSAGES["help"])

# معالج أمر حول البوت
@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    if not await check_user_access(message):
        return
    
    await message.answer(BOT_MESSAGES["about"])

# معالج أمر الإحصائيات (للمشرفين فقط)
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    
    # التحقق مما إذا كان المستخدم مشرفًا
    if user_id not in ADMIN_USERS:
        await message.answer("عذرًا، هذا الأمر متاح للمشرفين فقط.")
        return
    
    # الحصول على إحصائيات التحميل
    stats = get_download_stats()
    
    # إعداد رسالة الإحصائيات
    stats_message = "📊 إحصائيات البوت:\n\n"
    stats_message += f"إجمالي عدد التحميلات: {stats['total']}\n"
    stats_message += f"عدد التحميلات الناجحة: {stats['successful']}\n\n"
    
    if stats['by_platform']:
        stats_message += "التحميلات حسب المنصة:\n"
        for platform, count in stats['by_platform'].items():
            stats_message += f"- {platform}: {count}\n"
    
    await message.answer(stats_message)

# معالج أمر إضافة مستخدم (للمشرفين فقط)
@dp.message(Command("adduser"))
async def cmd_add_user(message: types.Message):
    user_id = message.from_user.id
    
    # التحقق مما إذا كان المستخدم مشرفًا
    if user_id not in ADMIN_USERS:
        await message.answer("عذرًا، هذا الأمر متاح للمشرفين فقط.")
        return
    
    # استخراج معرف المستخدم المراد إضافته
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.answer("الاستخدام الصحيح: /adduser [معرف_المستخدم]")
        return
    
    try:
        target_user_id = int(command_parts[1])
        
        # إضافة المستخدم إلى قائمة المستخدمين المسموح لهم
        if add_allowed_user(target_user_id, added_by=user_id):
            await message.answer(f"تمت إضافة المستخدم {target_user_id} إلى قائمة المستخدمين المسموح لهم.")
        else:
            await message.answer("حدث خطأ أثناء إضافة المستخدم.")
    except ValueError:
        await message.answer("معرف المستخدم يجب أن يكون رقمًا.")

# معالج أمر إزالة مستخدم (للمشرفين فقط)
@dp.message(Command("removeuser"))
async def cmd_remove_user(message: types.Message):
    user_id = message.from_user.id
    
    # التحقق مما إذا كان المستخدم مشرفًا
    if user_id not in ADMIN_USERS:
        await message.answer("عذرًا، هذا الأمر متاح للمشرفين فقط.")
        return
    
    # استخراج معرف المستخدم المراد إزالته
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.answer("الاستخدام الصحيح: /removeuser [معرف_المستخدم]")
        return
    
    try:
        target_user_id = int(command_parts[1])
        
        # إزالة المستخدم من قائمة المستخدمين المسموح لهم
        if remove_allowed_user(target_user_id):
            await message.answer(f"تمت إزالة المستخدم {target_user_id} من قائمة المستخدمين المسموح لهم.")
        else:
            await message.answer("حدث خطأ أثناء إزالة المستخدم.")
    except ValueError:
        await message.answer("معرف المستخدم يجب أن يكون رقمًا.")

# معالج الروابط
@dp.message(F.text)
async def handle_url(message: types.Message):
    if not await check_user_access(message):
        return
    
    # التحقق مما إذا كانت الرسالة تحتوي على رابط
    text = message.text.strip()
    
    # البحث عن الروابط في النص
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        return
    
    for url in urls:
        # تنظيف الرابط
        url = clean_url(url)
        
        # التحقق من صحة الرابط
        if not is_valid_url(url):
            continue
        
        # التحقق مما إذا كان الرابط من منصة مدعومة
        platform = extract_platform_from_url(url)
        if not platform:
            await message.answer(BOT_MESSAGES["unsupported_url"])
            continue
        
        # إرسال رسالة المعالجة
        processing_msg = await message.answer(BOT_MESSAGES["processing"])
        
        try:
            # استيراد وحدة التحميل المناسبة
            module_path = PLATFORMS[platform]["module"]
            module_parts = module_path.split('.')
            module_name = module_parts[-1]
            
            # استيراد ديناميكي للوحدة المناسبة
            downloader_module = __import__(module_path, fromlist=[module_name])
            downloader_class_name = f"{platform.capitalize()}Downloader"
            downloader_class = getattr(downloader_module, downloader_class_name)
            downloader = downloader_class()
            
            # تحميل الوسائط
            media_info = await downloader.download(url, DOWNLOAD_FOLDER)
            
            if not media_info or not media_info.get("files"):
                await processing_msg.edit_text(BOT_MESSAGES["download_error"])
                log_download(message.from_user.id, platform, url, "error")
                continue
            
            # إرسال رسالة نجاح التحميل
            await processing_msg.edit_text(BOT_MESSAGES["download_success"])
            
            # إرسال معلومات الوسائط إذا كانت متوفرة
            caption = ""
            if media_info.get("title"):
                caption += f"{hbold('العنوان:')} {media_info['title']}\n"
            if media_info.get("author"):
                caption += f"{hbold('المؤلف:')} {media_info['author']}\n"
            if media_info.get("description"):
                desc = media_info['description']
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                caption += f"{hbold('الوصف:')} {desc}\n"
            if media_info.get("url"):
                caption += f"{hbold('المصدر:')} {media_info['url']}\n"
            
            # إرسال الملفات
            for file_path in media_info["files"]:
                file_type = media_info.get("type", "unknown")
                
                try:
                    if file_type == "photo":
                        await message.answer_photo(FSInputFile(file_path), caption=caption)
                    elif file_type == "video":
                        await message.answer_video(FSInputFile(file_path), caption=caption)
                    elif file_type == "audio":
                        await message.answer_audio(FSInputFile(file_path), caption=caption)
                    elif file_type == "document":
                        await message.answer_document(FSInputFile(file_path), caption=caption)
                    else:
                        await message.answer_document(FSInputFile(file_path), caption=caption)
                    
                    # مسح الملف بعد الإرسال
                    caption = ""  # إرسال التعليق مرة واحدة فقط
                except Exception as e:
                    logger.error(f"Error sending file {file_path}: {e}")
                    await message.answer(f"حدث خطأ أثناء إرسال الملف: {e}")
            
            # تسجيل التحميل الناجح
            log_download(message.from_user.id, platform, url, "success")
            
            # تنظيف الملفات المؤقتة
            for file_path in media_info["files"]:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error removing file {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await processing_msg.edit_text(f"{BOT_MESSAGES['download_error']}\nالخطأ: {str(e)}")
            log_download(message.from_user.id, platform, url, "error")
        
        finally:
            # تنظيف مجلد التنزيلات المؤقتة
            try:
                for filename in os.listdir(DOWNLOAD_FOLDER):
                    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception as e:
                logger.error(f"Error cleaning temp folder: {e}")

# وظيفة بدء تشغيل البوت
async def main():
    # حذف الملفات المؤقتة عند بدء التشغيل
    try:
        if os.path.exists(DOWNLOAD_FOLDER):
            for filename in os.listdir(DOWNLOAD_FOLDER):
                file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning temp folder at startup: {e}")
    
    # بدء البوت
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
