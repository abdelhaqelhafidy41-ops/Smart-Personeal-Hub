import sqlite3
from datetime import datetime

import flet as ft
import openpyxl

from sections.core import DB_PATH, EXPORTS_PATH


class ExpenseManager:
    @staticmethod
    def add_expense(amount: float, category: str, exp_type: str, note: str = ""):
        """إضافة دخل أو مصروف"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")
        c.execute('''INSERT INTO expenses (amount, category, type, date, note)
                     VALUES (?, ?, ?, ?, ?)''',
                  (amount, category, exp_type, date, note))
        conn.commit()
        conn.close()

    @staticmethod
    def get_balance():
        """حساب الرصيد الحالي"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM expenses WHERE type = ?', ('income',))
        income = c.fetchone()[0] or 0
        c.execute('SELECT SUM(amount) FROM expenses WHERE type = ?', ('expense',))
        expenses = c.fetchone()[0] or 0
        conn.close()
        return income - expenses

    @staticmethod
    def get_expenses() -> list:
        """الحصول على جميع المصاريف"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM expenses ORDER BY date DESC, id DESC')
        rows = c.fetchall()
        conn.close()
        return rows

    @staticmethod
    def delete_expense(expense_id: int):
        """حذف مصروف أو دخل"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_expenses_by_category():
        """الحصول على المصاريف حسب التصنيف"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT category, SUM(amount) FROM expenses WHERE type = 'expense' 
                     GROUP BY category''')
        data = c.fetchall()
        conn.close()
        return data

    @staticmethod
    def export_monthly_report(month: int, year: int):
        """تصدير التقرير الشهري إلى Excel"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT * FROM expenses WHERE strftime('%m', date) = ? 
                     AND strftime('%Y', date) = ?''',
                  (str(month).zfill(2), str(year)))
        data = c.fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"تقرير_{month}_{year}"

        headers = ["المعرف", "المبلغ", "التصنيف", "النوع", "التاريخ", "الملاحظة"]
        ws.append(headers)

        for row in data:
            ws.append(row)

        filename = EXPORTS_PATH / f"تقرير_مصاريف_{month}_{year}.xlsx"
        wb.save(filename)
        return str(filename)


def build_expenses_section(app) -> ft.Control:
    """بناء قسم المصاريف"""
    def add_expense(e):
        try:
            amount = float(expense_amount_input.value or 0)
        except ValueError:
            amount = 0
        category = expense_category_input.value
        exp_type = expense_type_dropdown.value
        note = expense_note_input.value

        if amount and category and exp_type:
            ExpenseManager.add_expense(amount, category, exp_type, note)
            expense_amount_input.value = ""
            expense_category_input.value = ""
            expense_note_input.value = ""
            refresh_expenses()
            app.page.update()
            app.build_ui()

    def refresh_expenses():
        balance = ExpenseManager.get_balance()
        balance_text.value = f"الرصيد: {balance:,.2f}" if app.is_rtl else f"Balance: {balance:,.2f}"
        expenses_list.controls.clear()
        for expense in ExpenseManager.get_expenses():
            expense_text = f"{expense[2]} : {expense[1]:,.2f}" if app.is_rtl else f"{expense[2]} : {expense[1]:,.2f}"
            row = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(expense_text, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{expense[3]} | {expense[5] or ''}" if app.is_rtl else f"{expense[3]} | {expense[5] or ''}", size=11, color="#94a3b8"),
                    ], expand=True),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        on_click=lambda e, eid=expense[0]: (ExpenseManager.delete_expense(eid), refresh_expenses())
                    )
                ]),
                padding=10,
                border_radius=12,
                bgcolor="#0f172a" if app.is_dark_mode else "#f8fafc",
                border=ft.Border.all(1, "#60a5fa" if app.is_dark_mode else "#bfdbfe"),
                margin=ft.Margin(0, 0, 8, 0),
            )
            expenses_list.controls.append(row)
        app.page.update()

    def export_report(e):
        now = datetime.now()
        filename = ExpenseManager.export_monthly_report(now.month, now.year)
        result_text.value = f"تم التصدير: {filename}" if app.is_rtl else f"Exported: {filename}"
        app.page.update()

    expense_amount_input = app.make_text_field("المبلغ" if app.is_rtl else "Amount", width=180)
    expense_category_input = app.make_text_field("التصنيف" if app.is_rtl else "Category", width=180)
    expense_type_dropdown = app.make_dropdown(
        "النوع" if app.is_rtl else "Type",
        [
            ft.dropdown.Option("income", "دخل" if app.is_rtl else "Income"),
            ft.dropdown.Option("expense", "مصروف" if app.is_rtl else "Expense"),
        ],
        width=180,
    )
    expense_note_input = app.make_text_field("ملاحظة" if app.is_rtl else "Note", width=220)

    add_expense_button = app.make_action_button("إضافة" if app.is_rtl else "Add", add_expense, width=150)
    export_button = app.make_action_button("تصدير التقرير" if app.is_rtl else "Export Report", export_report, width=190)

    balance_text = ft.Text("الرصيد: 0" if app.is_rtl else "Balance: 0", size=18, weight=ft.FontWeight.BOLD, color="#22c55e")
    result_text = ft.Text("", size=12, color="#3b82f6")
    expenses_list = ft.ListView(expand=True, spacing=5)

    refresh_expenses()

    return ft.Column([
        ft.Text("حاسبة المصاريف" if app.is_rtl else "Expense Calculator", size=24, weight=ft.FontWeight.BOLD),
        balance_text,
        ft.Row([expense_amount_input, expense_category_input, expense_type_dropdown, expense_note_input, add_expense_button], wrap=True),
        export_button,
        result_text,
        ft.Divider(),
        ft.Text("السجل" if app.is_rtl else "History", size=16, weight=ft.FontWeight.BOLD),
        expenses_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
