# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 كلية الزراعة", callback_data="colledge_main")]
    ])

def main_sections_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 المستوى الأول", callback_data="level_1")],
        [InlineKeyboardButton("📚 المستوى الثاني", callback_data="level_2")],
        [InlineKeyboardButton("🎓 التخصصات", callback_data="specialties")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_start")]
    ])

def level_one_terms_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 الترم الأول", callback_data="term_1")],
        [InlineKeyboardButton("📖 الترم الثاني", callback_data="term_2")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="colledge_main")]
    ])

def subjects_keyboard(term_key):
    # المواد الخاصة بالمستوى الأول لكل ترم
    if term_key == "term_1":
        subjects = ["رياضيات", "كيمياء", "نبات عام", "لغة عربية", "حاسوب", "ثقافة إسلامية"]
    else:
        subjects = ["فيزياء", "كيمياء عضوية", "علم الحيوان", "مبادئ الإحصاء", "جيولوجيا", "الزراعة في البيئة اليمنية", "لغة عربية"]
    
    keyboard = []
    for sub in subjects:
        keyboard.append([InlineKeyboardButton(sub, callback_data=f"sub_{sub}")])
    
    back_target = "level_1"
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def sections_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 نماذج اختبار", callback_data="sec_exams")],
        [InlineKeyboardButton("📚 الكتب / ملخصات", callback_data="sec_books")],
        [InlineKeyboardButton("✨ الجديد", callback_data="sec_new")],
        [InlineKeyboardButton("🔙 رجوع للمواد", callback_data="term_1")] # أو حسب الترم الحالي
    ])

def back_keyboard(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data=callback_data)]
    ])

def admin_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 رفع ملف جديد", callback_data="admin_upload")],
        [InlineKeyboardButton("🗑️ حذف ملف", callback_data="admin_delete")],
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats")]
    ])
