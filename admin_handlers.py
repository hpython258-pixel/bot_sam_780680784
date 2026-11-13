# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from config import ADMIN_IDS
from database import (
    get_stats, add_category, get_categories, get_category_name, 
    delete_category, add_file_to_category, get_files_by_category, delete_file
)

# حالات المحادثة
ADDING_BUTTON, UPLOADING_FILE = range(2)

# ذاكرة مؤقتة لمتابعة مسار الأدمن الحالي
admin_nav_state = {} 
admin_action_data = {} 

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ عذراً، لوحة التحكم مخصصة للمشرفين فقط.")
        return
    
    admin_nav_state[user_id] = 0 
    await show_admin_menu(update.message, user_id, edit=False)

async def show_admin_menu(message_obj, user_id, edit=True):
    current_parent = admin_nav_state.get(user_id, 0)
    current_name = get_category_name(current_parent)
    sub_categories = get_categories(current_parent)
    
    keyboard = []
    for cat_id, cat_name in sub_categories:
        keyboard.append([
            InlineKeyboardButton(f"📁 {cat_name}", callback_data=f"adm_nav_{cat_id}"),
            InlineKeyboardButton("🗑️ حذف", callback_data=f"adm_delcat_{cat_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("➕ إضافة زر جديد هنا", callback_data=f"adm_addbtn_{current_parent}"),
        InlineKeyboardButton("📥 رفع ملف داخل هذا القسم", callback_data=f"adm_upl_{current_parent}")
    ])
    
    if current_parent != 0:
        keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية للأدمن", callback_data="adm_nav_0")])
    else:
        keyboard.append([InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats")])

    text = (
        f"👑 **لوحة تحكم المشرفين الديناميكية**\n"
        f"📍 أنت الآن في قسم: `{current_name}`\n\n"
        "اختر ما تريد فعله:"
    )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if edit:
        await message_obj.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await message_obj.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        return

    if data == "admin_stats":
        users_count, files_count = get_stats()
        text = f"📊 **الإحصائيات:**\n👥 المستخدمين: {users_count}\n📁 الملفات: {files_count}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="adm_nav_0")]])
        await query.message.edit_text(text, reply_markup=kb)

    elif data.startswith("adm_nav_"):
        target_id = int(data.replace("adm_nav_", ""))
        admin_nav_state[user_id] = target_id
        await show_admin_menu(query.message, user_id, edit=True)

    elif data.startswith("adm_delcat_"):
        cat_id = int(data.replace("adm_delcat_", ""))
        delete_category(cat_id)
        await query.message.edit_text("✅ تم حذف القسم وكل ما بداخله بنجاح!")
        await show_admin_menu(query.message, user_id, edit=False)

# --- محادثة إضافة زر جديد ---
async def start_adding_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    parent_id = int(query.data.replace("adm_addbtn_", ""))
    
    admin_action_data[user_id] = parent_id
    await query.message.edit_text(
        "✏️ **أرسل الآن اسم الزر الجديد الذي تريد إضافته:**\n(مثلاً: المستوى الأول، رياضيات، نماذج اختبار... إلخ)\n\nلإلغاء العملية أرسل /cancel",
        parse_mode="Markdown"
    )
    return ADDING_BUTTON

async def receive_new_button_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    button_name = update.message.text.strip()
    parent_id = admin_action_data.get(user_id, 0)
    
    if button_name == "/cancel":
        await update.message.reply_text("❌ تم إلغاء العملية.")
        admin_nav_state[user_id] = parent_id
        await show_admin_menu(update.message, user_id, edit=False)
        return ConversationHandler.END

    add_category(parent_id, button_name)
    
    await update.message.reply_text(f"✅ تم إضافة الزر الجديد **[{button_name}]** بنجاح!")
    admin_nav_state[user_id] = parent_id
    await show_admin_menu(update.message, user_id, edit=False)
    return ConversationHandler.END

# --- محادثة رفع ملف داخل القسم ---
async def start_upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    parent_id = int(query.data.replace("adm_upl_", ""))
    
    admin_action_data[user_id] = parent_id
    await query.message.edit_text(
        "📥 **أرسل الملف (PDF، مستند، صورة، أو فيديو) لرفعه داخل هذا القسم:**\n(تأكد من كتابة اسم الملف في وصف الرسالة Caption)\n\nلإلغاء العملية أرسل /cancel",
        parse_mode="Markdown"
    )
    return UPLOADING_FILE

async def receive_file_in_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    category_id = admin_action_data.get(user_id, 0)
    
    if message.text and message.text.strip() == "/cancel":
        await message.reply_text("❌ تم إلغاء العملية.")
        admin_nav_state[user_id] = category_id
        await show_admin_menu(message, user_id, edit=False)
        return ConversationHandler.END

    file_id = None
    file_type = None
    file_name = message.caption or "ملف تعليمي"
    
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
        file_name = message.document.file_name or file_name
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    
    if file_id:
        add_file_to_category(category_id, file_id, file_name, file_type)
        await message.reply_text("✅ تم رفع وحفظ الملف بنجاح داخل هذا الزر!")
        admin_nav_state[user_id] = category_id
        await show_admin_menu(message, user_id, edit=False)
    else:
        await message.reply_text("❌ يرجى إرسال ملف صحيح (مستند PDF، صورة، أو فيديو) أو إرسال /cancel للإلغاء.")
        return UPLOADING_FILE
    
    return ConversationHandler.END

async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.")
    return ConversationHandler.END
