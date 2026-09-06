import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import main


def test_database_backup_and_restore(tmp_path, monkeypatch):
    db_path = tmp_path / "hub.db"
    backup_dir = tmp_path / "backups"
    exports_dir = tmp_path / "exports"

    monkeypatch.setattr(main, "DB_PATH", str(db_path))
    monkeypatch.setattr(main, "BACKUP_PATH", backup_dir)
    monkeypatch.setattr(main, "EXPORTS_PATH", exports_dir)

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO tasks (name) VALUES ('demo')")
    conn.commit()
    conn.close()

    backup_path = main.DataBackupManager.create_backup("demo")
    assert Path(backup_path).exists()

    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()

    restored = main.DataBackupManager.restore_backup(backup_path)
    assert restored is True

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    assert row == 1


def test_delete_all_data_and_single_item_delete():
    db_path = Path("hub.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY, title TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO schedule (title) VALUES ('exam')")
    conn.execute("INSERT INTO products (name) VALUES ('book')")
    conn.commit()
    conn.close()

    main.ScheduleManager.delete_event(1)
    main.InvoiceManager.delete_product(1)

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM schedule").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0
    conn.close()

    main.DataBackupManager.delete_all_data()
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0
    conn.close()
