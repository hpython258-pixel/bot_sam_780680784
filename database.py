# -*- coding: utf-8 -*-
import sqlite3

DB_NAME = "agriculture_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # جدول المستخدمين للإحصائيات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    """)
    
    # جدول الأقسام والأزرار الديناميكية (Category / Menu Tree)
    # parent_id = 0 يعني زر رئيسي في القائمة الأولى، وإذا كان رقماً آخر فمعناه أنه زر فرعي تحته
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER DEFAULT 0,
            name TEXT NOT NULL
        )
    """)
    
    # جدول الملفات المرتبطة بالأزرار الديناميكية
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            file_id TEXT,
            file_name TEXT,
            file_type TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", 
                   (user_id, username, full_name))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM files")
    files_count = cursor.fetchone()[0]
    conn.close()
    return users_count, files_count

# --- دوال إدارة الأزرار والأقسام الديناميكية ---
def add_category(parent_id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (parent_id, name) VALUES (?, ?)", (parent_id, name))
    conn.commit()
    cat_id = cursor.lastrowid
    conn.close()
    return cat_id

def get_categories(parent_id=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories WHERE parent_id = ?", (parent_id,))
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_category_name(cat_id):
    if cat_id == 0:
        return "الرئيسية"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE id = ?", (cat_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else "غير معروف"

def delete_category(cat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ? OR parent_id = ?", (cat_id, cat_id))
    conn.commit()
    conn.close()

# --- دوال إدارة الملفات داخل الأزرار ---
def add_file_to_category(category_id, file_id, file_name, file_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO files (category_id, file_id, file_name, file_type)
        VALUES (?, ?, ?, ?)
    """, (category_id, file_id, file_name, file_type))
    conn.commit()
    conn.close()

def get_files_by_category(category_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, file_type, file_id FROM files WHERE category_id = ?", (category_id,))
    files = cursor.fetchall()
    conn.close()
    return files

def delete_file(file_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE id=?", (file_id,))
    conn.commit()
    conn.close()
