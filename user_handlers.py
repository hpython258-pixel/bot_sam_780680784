# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_user, get_categories, get_files_by_category, get_category_name

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.full_name)
    
    # جلب الأزرار الرئيسية (المستوى الأول، وغيرها التي أنشأتها)
    categories = get_categories(parent_id=0)
    
    keyboard = []
    for cat_id, cat_name in categories:
        keyboard.append([InlineKeyboardButton(f"🎓 {cat_name}", callback_data=f"user_cat_{cat_id}")])
    
    if not keyboard:
        keyboard.append([InlineKeyboardButton("🚧 البوت قيد الإعداد من قبل الإدارة", callback_data="none")])

    text = f"مرحباً بك يا أسطورة ({user.full_name}) في بوت كلية الزراعة - جامعة صنعاء 🎓\nاختر من الأقسام أدناه:"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_user_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "none":
        return

    if data.startswith("user_cat_"):
        cat_id = int(data.replace("user_cat_", ""))
        cat_name = get_category_name(cat_id)
        
        # 1. فحص هل هذا الزر تحته أزرار فرعية أخرى؟
        sub_categories = get_categories(cat_id)
        # 2. فحص هل هذا الزر تحته ملفات مرفوعة؟
        files = get_files_by_category(cat_id)
        
        keyboard = []
        
        # إذا وُجدت أزرار فرعية (أزرار داخل أزرار)
        for sub_id, sub_name in sub_categories:
            keyboard.append([InlineKeyboardButton(f"📁 {sub_name}", callback_data=f"user_cat_{sub_id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="user_home")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # عرض القسم مع الملفات إن وجدت
        text = f"📂 قسم: **{cat_name}**\nاختر ما يناسبك:"
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)
        
        # إرسال الملفات الموجودة في هذا القسم مباشرة إن وجدت
        if files:
            await query.message.reply_text(f"📄 الملفات المتوفرة في قسم ({cat_name}):")
            for f in files:
                _, file_name, file_type, file_id = f
                if file_type == "document":
                    await context.bot.send_document(chat_id=query.message.chat_id, document=file_id, caption=file_name)
                elif file_type == "photo":
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=file_id, caption=file_name)
                elif file_type == "video":
                    await context.bot.send_video(chat_id=query.message.chat_id, video=file_id, caption=file_name)
        elif not sub_categories:
            await query.message.reply_text("❌ لا توجد ملفات حالياً في هذا القسم.")

    elif data == "user_home":
        categories = get_categories(parent_id=0)
        keyboard = []
        for cat_id, cat_name in categories:
            keyboard.append([InlineKeyboardButton(f"🎓 {cat_name}", callback_data=f"user_cat_{cat_id}")])
        
        await query.message.edit_text("مرحباً بك في القائمة الرئيسية لبوكلية الزراعة 🎓", reply_markup=InlineKeyboardMarkup(keyboard))
