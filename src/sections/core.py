import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet

APP_TITLE = "المركز الشخصي الذكي - Smart Personal Hub"
DB_PATH = "hub.db"
BACKUP_PATH = Path("backups")
ASSETS_PATH = Path("assets")
EXPORTS_PATH = Path("exports")
COVERS_PATH = ASSETS_PATH / "covers"
RECIPES_PATH = ASSETS_PATH / "recipes"
CHARTS_PATH = ASSETS_PATH / "charts"

for path in [ASSETS_PATH, EXPORTS_PATH, BACKUP_PATH, COVERS_PATH, RECIPES_PATH, CHARTS_PATH]:
    path.mkdir(parents=True, exist_ok=True)


def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT,
                  due_date TEXT, priority TEXT, completed BOOLEAN, created_date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY, amount REAL, category TEXT,
                  type TEXT, date TEXT, note TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT,
                  cover_path TEXT, progress REAL, start_date TEXT,
                  end_date TEXT, rating REAL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS passwords
                 (id INTEGER PRIMARY KEY, website TEXT, email TEXT,
                  password TEXT, note TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS rates
                 (id INTEGER PRIMARY KEY, currency TEXT, rate REAL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY, from_value TEXT, to_value TEXT,
                  result REAL, date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS schedule
                 (id INTEGER PRIMARY KEY, title TEXT, type TEXT,
                  date TEXT, description TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                 (id INTEGER PRIMARY KEY, name TEXT, image_path TEXT,
                  ingredients TEXT, steps TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS invoices
                 (id INTEGER PRIMARY KEY, invoice_number TEXT, date TEXT,
                  total REAL, profit REAL, items TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS quran_progress
                 (id INTEGER PRIMARY KEY, surah_number INTEGER,
                  daily_target INTEGER, completed INTEGER, date TEXT)''')

    conn.commit()
    conn.close()


def get_cipher_key():
    """الحصول على مفتاح التشفير"""
    key_file = "cipher.key"
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    else:
        with open(key_file, "rb") as f:
            key = f.read()
    return key


def encrypt_password(password: str) -> str:
    """تشفير كلمة السر"""
    cipher = Fernet(get_cipher_key())
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """فك تشفير كلمة السر"""
    cipher = Fernet(get_cipher_key())
    return cipher.decrypt(encrypted_password.encode()).decode()


class DataBackupManager:
    """إدارة النسخ الاحتياطية واستعادتها"""

    @staticmethod
    def list_backups() -> list:
        BACKUP_PATH.mkdir(parents=True, exist_ok=True)
        return sorted(BACKUP_PATH.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)

    @staticmethod
    def create_backup(name: str = "backup") -> str:
        BACKUP_PATH.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in str(name).strip() or "backup")
        safe_name = safe_name.strip("_") or "backup"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_PATH / f"{safe_name}_{timestamp}.db"
        shutil.copy2(DB_PATH, str(backup_file))
        return str(backup_file)

    @staticmethod
    def export_backup(backup_path: str, target_dir: str = None) -> str:
        source = Path(backup_path)
        destination_dir = Path(target_dir) if target_dir else EXPORTS_PATH / "backups"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source.name
        shutil.copy2(source, destination)
        return str(destination)

    @staticmethod
    def restore_backup(backup_path: str) -> bool:
        source = Path(backup_path)
        if not source.exists():
            return False
        shutil.copy2(source, DB_PATH)
        init_database()
        return True

    @staticmethod
    def delete_backup(backup_path: str) -> bool:
        source = Path(backup_path)
        if not source.exists():
            return False
        source.unlink()
        return True

    @staticmethod
    def delete_all_data() -> None:
        init_database()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        tables = [
            "tasks", "expenses", "books", "passwords", "rates", "history",
            "schedule", "recipes", "products", "invoices", "quran_progress"
        ]
        for table in tables:
            c.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()
