import sqlite3
from datetime import datetime, timedelta

import flet as ft

from sections.core import DB_PATH
from sections.schedule import ScheduleManager


class TaskManager:
    @staticmethod
    def add_task(name: str, description: str, due_date: str, priority: str):
        """إضافة مهمة جديدة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        created_date = datetime.now().strftime("%Y-%m-%d")
        c.execute('''INSERT INTO tasks (name, description, due_date, priority, completed, created_date)
                     VALUES (?, ?, ?, ?, 0, ?)''',
                  (name, description, due_date, priority, created_date))
        conn.commit()
        conn.close()

    @staticmethod
    def get_tasks(filter_type: str = "all") -> list:
        """الحصول على المهام بناءً على نوع الفلترة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        if filter_type == "today":
            c.execute('SELECT * FROM tasks WHERE due_date = ? AND completed = 0', (today,))
        elif filter_type == "week":
            week_start = datetime.now()
            week_end = week_start + timedelta(days=7)
            c.execute('''SELECT * FROM tasks WHERE due_date BETWEEN ? AND ? AND completed = 0''',
                      (week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
        elif filter_type == "completed":
            c.execute('SELECT * FROM tasks WHERE completed = 1')
        else:
            c.execute('SELECT * FROM tasks')

        tasks = c.fetchall()
        conn.close()
        return tasks

    @staticmethod
    def complete_task(task_id: int):
        """وضع علامة على المهمة كمنجزة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_task(task_id: int):
        """حذف مهمة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats():
        """الحصول على إحصائيات المهام"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM tasks WHERE completed = 1')
        completed = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM tasks')
        total = c.fetchone()[0]
        conn.close()
        return {"completed": completed, "total": total}


def build_tasks_section(app) -> ft.Control:
    """بناء قسم المهام"""
    def add_task(e):
        name = task_name_input.value
        description = task_desc_input.value
        due_date = task_date_input.value
        priority = priority_dropdown.value

        if name and (not due_date or ScheduleManager.is_valid_date(due_date)):
            TaskManager.add_task(name, description, due_date, priority)
            task_name_input.value = ""
            task_desc_input.value = ""
            task_date_input.value = ""
            refresh_tasks()
            app.build_ui()
        elif name:
            task_date_input.error_text = "تاريخ غير صحيح. استخدم YYYY-MM-DD" if app.is_rtl else "Invalid date. Use YYYY-MM-DD"
            app.page.update()

    def refresh_tasks():
        tasks_list.controls.clear()
        filter_type = filter_dropdown.value or "all"
        tasks = TaskManager.get_tasks(filter_type)

        for task in tasks:
            task_card = app.make_card(
                ft.Container(
                    content=ft.Column([
                        ft.Text(task[1], size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(task[2], size=12, color="#64748b"),
                        ft.Row([
                            ft.Text(f"التاريخ: {task[3]}" if app.is_rtl else f"Date: {task[3]}", size=10),
                            ft.Text(f"الأولوية: {task[4]}" if app.is_rtl else f"Priority: {task[4]}", size=10),
                        ]),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.CHECK,
                                on_click=lambda e, tid=task[0]: (TaskManager.complete_task(tid), app.build_ui())
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, tid=task[0]: (TaskManager.delete_task(tid), app.build_ui())
                            ),
                        ]),
                    ]),
                    padding=15,
                )
            )
            tasks_list.controls.append(task_card)

        stats = TaskManager.get_stats()
        stats_text.value = f"المنجز: {stats['completed']}/{stats['total']}" if app.is_rtl else f"Completed: {stats['completed']}/{stats['total']}"
        app.page.update()

    task_name_input = app.make_text_field("اسم المهمة" if app.is_rtl else "Task Name", width=300)
    task_desc_input = app.make_text_field("الوصف" if app.is_rtl else "Description", width=300, multiline=True)
    task_date_input = app.make_text_field("التاريخ (YYYY-MM-DD)" if app.is_rtl else "Date (YYYY-MM-DD)", width=300)
    priority_dropdown = app.make_dropdown(
        "الأولوية" if app.is_rtl else "Priority",
        [
            ft.dropdown.Option("عادي" if app.is_rtl else "Normal"),
            ft.dropdown.Option("مهم" if app.is_rtl else "Important"),
            ft.dropdown.Option("عاجل" if app.is_rtl else "Urgent"),
        ],
        width=300,
    )

    filter_dropdown = app.make_dropdown(
        "فلترة" if app.is_rtl else "Filter",
        [
            ft.dropdown.Option("all", "الكل" if app.is_rtl else "All"),
            ft.dropdown.Option("today", "اليوم" if app.is_rtl else "Today"),
            ft.dropdown.Option("week", "هذا الأسبوع" if app.is_rtl else "This Week"),
            ft.dropdown.Option("completed", "المنجزة" if app.is_rtl else "Completed"),
        ],
        width=200,
        on_select=lambda e: refresh_tasks(),
    )

    tasks_list = ft.ListView(expand=True, spacing=10)
    stats_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    add_button = ft.ElevatedButton(
        "إضافة مهمة" if app.is_rtl else "Add Task",
        on_click=add_task,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    refresh_tasks()

    return ft.Column([
        ft.Text("منظم المهام" if app.is_rtl else "Task Manager", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([task_name_input, task_desc_input, task_date_input, priority_dropdown, add_button], wrap=True),
        filter_dropdown,
        stats_text,
        ft.Divider(),
        tasks_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
