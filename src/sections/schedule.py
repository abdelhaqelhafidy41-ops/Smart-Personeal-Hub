import json
import sqlite3
from datetime import datetime

import flet as ft
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sections.core import DB_PATH, EXPORTS_PATH


class ScheduleManager:
    @staticmethod
    def add_event(title: str, event_type: str, date: str, description: str = ""):
        """إضافة حدث في الجدول"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO schedule (title, type, date, description)
                     VALUES (?, ?, ?, ?)''',
                  (title, event_type, date, description))
        conn.commit()
        conn.close()

    @staticmethod
    def get_events(date: str = None) -> list:
        """الحصول على الأحداث في يوم معين"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if date:
            c.execute('SELECT * FROM schedule WHERE date = ?', (date,))
        else:
            c.execute('SELECT * FROM schedule ORDER BY date')
        events = c.fetchall()
        conn.close()
        return events

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """التحقق من أن التاريخ صحيح ويطابق YYYY-MM-DD"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def get_exam_countdown(exam_date: str):
        """حساب عدد الأيام المتبقية قبل الامتحان"""
        if not exam_date or not ScheduleManager.is_valid_date(exam_date):
            return None
        exam = datetime.strptime(exam_date, "%Y-%m-%d")
        today = datetime.now()
        return (exam - today).days

    @staticmethod
    def delete_event(event_id: int):
        """حذف حدث من الجدول الدراسي"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM schedule WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def export_schedule_to_pdf():
        """تصدير الجدول إلى PDF"""
        events = ScheduleManager.get_events()

        filename = EXPORTS_PATH / f"جدول_دراسي_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=A4)
        story = []

        story.append(Paragraph("الجدول الدراسي", getSampleStyleSheet()['Heading1']))
        story.append(Spacer(1, 12))

        if events:
            data = [["التاريخ", "النوع", "العنوان", "الوصف"]]
            for event in events:
                data.append([event[3], event[2], event[1], event[4] or ""])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("لا توجد أحداث مجدولة", getSampleStyleSheet()['Normal']))

        doc.build(story)
        return str(filename)


def build_schedule_section(app) -> ft.Control:
    """بناء قسم الجدول الدراسي"""
    def add_event(e):
        title = event_title_input.value
        event_type = event_type_dropdown.value
        date = event_date_input.value
        description = event_desc_input.value

        if title and date and ScheduleManager.is_valid_date(date):
            ScheduleManager.add_event(title, event_type, date, description)
            event_title_input.value = ""
            event_desc_input.value = ""
            event_date_input.value = ""
            event_date_input.error_text = ""
            refresh_events()
            app.page.update()
        elif title:
            event_date_input.error_text = "تاريخ غير صحيح. استخدم YYYY-MM-DD" if app.is_rtl else "Invalid date. Use YYYY-MM-DD"
            app.page.update()

    def refresh_events():
        events_list.controls.clear()
        events = ScheduleManager.get_events()
        for event in events:
            days_remaining = None
            if (event[2] == "امتحان" or event[2] == "Exam") and ScheduleManager.is_valid_date(event[3]):
                days_remaining = ScheduleManager.get_exam_countdown(event[3])
            countdown_text = f" ({days_remaining} أيام متبقية)" if isinstance(days_remaining, int) else ""
            event_card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(event[1], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"النوع: {event[2]}" if app.is_rtl else f"Type: {event[2]}", size=12),
                            ft.Text(f"التاريخ: {event[3]}{countdown_text}" if app.is_rtl else f"Date: {event[3]}{countdown_text}", size=12),
                            ft.Text(event[4] if event[4] else "", size=11, color="#64748b"),
                        ], expand=True),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            tooltip="حذف" if app.is_rtl else "Delete",
                            on_click=lambda e, eid=event[0]: (ScheduleManager.delete_event(eid), refresh_events())
                        ),
                    ]),
                    padding=15,
                ),
                margin=ft.Margin(0, 5, 0, 5),
            )
            events_list.controls.append(event_card)
        app.page.update()

    def export_pdf(e):
        filename = ScheduleManager.export_schedule_to_pdf()
        result_text.value = f"تم التصدير: {filename}" if app.is_rtl else f"Exported: {filename}"
        app.page.update()

    event_title_input = app.make_text_field("العنوان" if app.is_rtl else "Title", width=300)
    event_type_dropdown = app.make_dropdown(
        "النوع" if app.is_rtl else "Type",
        [
            ft.dropdown.Option("امتحان" if app.is_rtl else "exam", "امتحان" if app.is_rtl else "Exam"),
            ft.dropdown.Option("واجب" if app.is_rtl else "homework", "واجب" if app.is_rtl else "Homework"),
            ft.dropdown.Option("محاضرة" if app.is_rtl else "lecture", "محاضرة" if app.is_rtl else "Lecture"),
        ],
        width=250,
    )
    event_date_input = app.make_text_field("التاريخ (YYYY-MM-DD)" if app.is_rtl else "Date (YYYY-MM-DD)", width=250)
    event_desc_input = app.make_text_field("الوصف" if app.is_rtl else "Description", width=300, multiline=True)

    add_event_button = ft.ElevatedButton(
        "إضافة حدث" if app.is_rtl else "Add Event",
        on_click=add_event,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    export_pdf_button = ft.ElevatedButton(
        "تصدير PDF" if app.is_rtl else "Export PDF",
        on_click=export_pdf,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    events_list = ft.ListView(expand=True, spacing=10)
    result_text = ft.Text("", size=12, color="#3b82f6")

    refresh_events()

    return ft.Column([
        ft.Text("الجدول الدراسي" if app.is_rtl else "Schedule", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([event_title_input, event_type_dropdown, event_date_input], wrap=True),
        ft.Row([event_desc_input, add_event_button, export_pdf_button], wrap=True),
        result_text,
        ft.Divider(),
        events_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
