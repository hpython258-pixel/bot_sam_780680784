# -*- coding: utf-8 -*-
import logging
import sys
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from config import BOT_TOKEN
from database import init_db
from user_handlers import start_command, handle_user_navigation
from admin_handlers import (
    admin_command, admin_callback, start_adding_button, receive_new_button_name,
    start_upload_file, receive_file_in_category, cancel_conv, ADDING_BUTTON, UPLOADING_FILE
)

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("AgricultureBot")

def main():
    init_db()
    logger.info("🗄️ تم تجهيز قاعدة البيانات الديناميكية بنجاح...")

    application = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()

    # 1. محادثة إضافة زر جديد ديناميكياً (بدون per_message لتستقبل النصوص بحرية)
    add_button_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_adding_button, pattern="^adm_addbtn_")],
        states={
            ADDING_BUTTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_button_name)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)]
    )

    # 2. محادثة رفع ملف داخل القسم
    upload_file_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_upload_file, pattern="^adm_upl_")],
        states={
            UPLOADING_FILE: [MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.TEXT, receive_file_in_category)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)]
    )

    # تسجيل المحادثات أولاً
    application.add_handler(add_button_conv)
    application.add_handler(upload_file_conv)
    
    # الأوامر العامة والأزرار الأخرى
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^(adm_|admin_)"))
    application.add_handler(CallbackQueryHandler(handle_user_navigation))

    logger.info("🚀 البوت الديناميكي الشجري يعمل الآن بكفاءة وبدون أي تحذيرات أو تعليق...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
