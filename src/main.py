import json
import os

import flet as ft

from sections.books import BookLibrary, build_books_section
from sections.converter import UnitConverter, build_converter_section
from sections.core import APP_TITLE, DataBackupManager, init_database
from sections.expenses import ExpenseManager, build_expenses_section
from sections.invoices import InvoiceManager, build_invoices_section
from sections.passwords import PasswordManager, build_passwords_section
from sections.quran import QuranManager, build_quran_section
from sections.recipes import RecipeManager, build_recipes_section
from sections.schedule import ScheduleManager, build_schedule_section
from sections.settings import build_settings_section
from sections.tasks import TaskManager, build_tasks_section


class SmartHubApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = APP_TITLE
        self.page.padding = 0

        self.is_rtl = True
        self.is_dark_mode = True
        self.current_section = 0
        self.last_invoice_number = ""

        self.load_settings()
        init_database()
        self.build_ui()

    def load_settings(self):
        """تحميل الإعدادات المحفوظة من ملف محلي"""
        settings_file = "app_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.is_rtl = settings.get("is_rtl", True)
                    self.is_dark_mode = settings.get("is_dark_mode", True)
            except Exception:
                self.is_rtl = True
                self.is_dark_mode = True
        else:
            self.is_rtl = True
            self.is_dark_mode = True
        self.update_theme()

    def save_settings(self):
        """حفظ الإعدادات في ملف محلي"""
        settings = {
            "is_rtl": self.is_rtl,
            "is_dark_mode": self.is_dark_mode
        }
        with open("app_settings.json", 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False)

    def make_text_field(self, label: str, width: int = 250, multiline: bool = False, password: bool = False):
        """إنشاء TextField متناسق في جميع الأقسام"""
        field_bg = "#0f172a" if self.is_dark_mode else "#f8fafc"
        field_text = "#e2e8f0" if self.is_dark_mode else "#0f172a"
        label_color = "#94a3b8" if self.is_dark_mode else "#475569"
        border = "#60a5fa" if self.is_dark_mode else "#93c5fd"
        focused = "#60a5fa" if self.is_dark_mode else "#2563eb"
        return ft.TextField(
            label=label,
            width=width,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            password=password,
            border_radius=14,
            border_color=border,
            focused_border_color=focused,
            bgcolor=field_bg,
            color=field_text,
            filled=True,
            content_padding=12,
            label_style=ft.TextStyle(color=label_color, size=12),
            text_style=ft.TextStyle(color=field_text, size=14),
            cursor_color=focused,
            dense=True,
        )

    def make_dropdown(self, label: str, options: list, width: int = 250, on_select=None, value=None):
        """إنشاء Dropdown متناسق في جميع الأقسام"""
        field_bg = "#0f172a" if self.is_dark_mode else "#f8fafc"
        field_text = "#e2e8f0" if self.is_dark_mode else "#0f172a"
        label_color = "#94a3b8" if self.is_dark_mode else "#475569"
        border = "#60a5fa" if self.is_dark_mode else "#93c5fd"
        focused = "#60a5fa" if self.is_dark_mode else "#2563eb"
        return ft.Dropdown(
            label=label,
            width=width,
            options=options,
            value=value,
            on_select=on_select,
            border_radius=14,
            border_color=border,
            focused_border_color=focused,
            bgcolor=field_bg,
            color=field_text,
            filled=True,
            text_style=ft.TextStyle(color=field_text, size=14),
            label_style=ft.TextStyle(color=label_color, size=12),
            content_padding=12,
            dense=True,
        )

    def make_action_button(self, label: str, on_click, width: int = 180):
        """إنشاء زر متناسق في جميع الأقسام"""
        return ft.ElevatedButton(
            label,
            on_click=on_click,
            width=width,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#2563eb" if self.is_dark_mode else "#1d4ed8",
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

    def _on_hover_card(self, e):
        """إضافة حركة hover للبطاقات"""
        target_scale = 1.02 if e.data == "true" else 1.0
        e.control.scale = target_scale
        e.control.update()

    def make_card(self, content, accent_color="#2563eb"):
        """إنشاء بطاقة أنيقة مع حركة hover"""
        bg_color = "#1f2937" if self.is_dark_mode else "#ffffff"
        border_color = "#60a5fa" if self.is_dark_mode else "#dbeafe"
        shadow_color = "#00000044" if self.is_dark_mode else "#93c5fd44"

        return ft.Container(
            content=content,
            bgcolor=bg_color,
            border_radius=18,
            padding=0,
            border=ft.Border.all(1, border_color),
            shadow=ft.BoxShadow(
                blur_radius=18,
                color=shadow_color,
                offset=ft.Offset(0, 6),
                spread_radius=0,
                blur_style="normal",
            ),
            animate_scale=ft.Animation(220, "easeOutCubic"),
            animate_opacity=ft.Animation(220, "easeOutCubic"),
            scale=1,
            opacity=1,
            on_hover=self._on_hover_card,
            margin=ft.Margin(0, 0, 8, 0),
        )

    def update_theme(self):
        """تحديث الثيم"""
        if self.is_dark_mode:
            self.page.bgcolor = "#111827"
        else:
            self.page.bgcolor = "#ffffff"
        self.page.update()

    def toggle_language(self, e):
        """تبديل اللغة"""
        self.is_rtl = not self.is_rtl
        self.save_settings()
        self.page.update()
        self.build_ui()

    def toggle_theme(self, e):
        """تبديل الثيم"""
        self.is_dark_mode = not self.is_dark_mode
        self.save_settings()
        self.update_theme()
        self.build_ui()

    def build_ui(self):
        """بناء الواجهة الرئيسية"""
        self.page.clean()
        self.page.rtl = self.is_rtl

        shell_bg = "#0f172a" if self.is_dark_mode else "#f3f4f6"
        panel_bg = "#1f2937" if self.is_dark_mode else "#ffffff"
        side_bg = "#2b3344" if self.is_dark_mode else "#e0f2fe"
        accent = "#2563eb" if self.is_dark_mode else "#1d4ed8"

        app_bar = ft.AppBar(
            title=ft.Text(APP_TITLE, size=22, weight=ft.FontWeight.BOLD),
            bgcolor=accent,
            color="#ffffff",
            actions=[
                ft.IconButton(
                    ft.Icons.TRANSLATE,
                    tooltip="تبديل اللغة" if self.is_rtl else "Toggle Language",
                    on_click=self.toggle_language,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                ),
                ft.IconButton(
                    ft.Icons.BRIGHTNESS_4 if self.is_dark_mode else ft.Icons.BRIGHTNESS_7,
                    tooltip="تبديل الثيم" if self.is_rtl else "Toggle Theme",
                    on_click=self.toggle_theme,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                ),
            ],
        )

        nav_items = [
            (ft.Icons.TASK_ALT, "المهام" if self.is_rtl else "Tasks"),
            (ft.Icons.ATTACH_MONEY, "المصاريف" if self.is_rtl else "Expenses"),
            (ft.Icons.BOOK, "الكتب" if self.is_rtl else "Books"),
            (ft.Icons.PASSWORD, "كلمات السر" if self.is_rtl else "Passwords"),
            (ft.Icons.AUTORENEW, "محول الوحدات" if self.is_rtl else "Converter"),
            (ft.Icons.SCHEDULE, "الجدول" if self.is_rtl else "Schedule"),
            (ft.Icons.RESTAURANT, "الوصفات" if self.is_rtl else "Recipes"),
            (ft.Icons.RECEIPT, "الفواتير" if self.is_rtl else "Invoices"),
            (ft.Icons.MENU_BOOK, "القرآن" if self.is_rtl else "Quran"),
            (ft.Icons.SETTINGS, "الإعدادات" if self.is_rtl else "Settings"),
        ]

        nav_rail = ft.NavigationRail(
            selected_index=self.current_section,
            destinations=[ft.NavigationRailDestination(icon=item[0], label=item[1]) for item in nav_items],
            on_change=self.on_nav_change,
            bgcolor=side_bg,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=True,
            elevation=0,
        )

        section_content = self.get_section_content(self.current_section)
        if self.current_section != 9:
            content_area = ft.Column([self.build_glance_banner(), section_content], expand=True, spacing=16)
        else:
            content_area = ft.Column([section_content], expand=True, spacing=16)

        main_layout = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=nav_rail,
                        bgcolor=side_bg,
                        border_radius=22,
                        padding=12,
                        shadow=ft.BoxShadow(
                            blur_radius=20,
                            color="#00000044",
                            offset=ft.Offset(0, 4),
                            spread_radius=0,
                            blur_style="normal",
                        ),
                    ),
                    ft.VerticalDivider(width=1),
                    ft.Container(
                        content=content_area,
                        expand=True,
                        padding=20,
                        border_radius=22,
                        bgcolor=panel_bg,
                        shadow=ft.BoxShadow(
                            blur_radius=20,
                            color="#00000044",
                            offset=ft.Offset(0, 4),
                            spread_radius=0,
                            blur_style="normal",
                        ),
                        animate_scale=ft.Animation(300, "easeOutCubic"),
                        scale=1,
                    ),
                ],
                expand=True,
                spacing=12,
            ),
            bgcolor=shell_bg,
            padding=18,
            border_radius=28,
            expand=True,
        )

        self.page.add(app_bar, main_layout)

    def on_nav_change(self, e):
        """عند تغيير القسم المختار"""
        self.current_section = e.control.selected_index
        self.build_ui()

    def build_glance_banner(self) -> ft.Control:
        """بانر إحصائي عام لتحسين الواجهة في كل الأقسام"""
        tasks_stats = TaskManager.get_stats()
        total_books = len(BookLibrary.get_books())
        total_passwords = len(PasswordManager.get_passwords())
        balance = ExpenseManager.get_balance()

        summary_cards = [
            ("المهام" if self.is_rtl else "Tasks", f"{tasks_stats['completed']}/{tasks_stats['total']}", "#60a5fa"),
            ("الرصيد" if self.is_rtl else "Balance", f"{balance:,.2f}", "#4ade80"),
            ("الكتب" if self.is_rtl else "Books", str(total_books), "#a78bfa"),
            ("كلمات السر" if self.is_rtl else "Passwords", str(total_passwords), "#fbbf24"),
        ]

        cards = []
        for title, value, color in summary_cards:
            cards.append(
                self.make_card(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(title, size=12, weight=ft.FontWeight.W_600, color="#94a3b8"),
                            ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=color),
                        ], tight=True),
                        padding=16,
                    ),
                    accent_color=color,
                )
            )

        return ft.Container(content=ft.Row(cards, wrap=True, spacing=10, run_spacing=10), padding=0, margin=ft.Margin(0, 0, 12, 0))

    def get_section_content(self, section_id: int) -> ft.Control:
        """الحصول على محتوى القسم"""
        if section_id == 0:
            return build_tasks_section(self)
        if section_id == 1:
            return build_expenses_section(self)
        if section_id == 2:
            return build_books_section(self)
        if section_id == 3:
            return build_passwords_section(self)
        if section_id == 4:
            return build_converter_section(self)
        if section_id == 5:
            return build_schedule_section(self)
        if section_id == 6:
            return build_recipes_section(self)
        if section_id == 7:
            return build_invoices_section(self)
        if section_id == 8:
            return build_quran_section(self)
        if section_id == 9:
            return build_settings_section(self)
        return ft.Text("قسم غير موجود" if self.is_rtl else "Section not found")


def main(page: ft.Page):
    """الدالة الرئيسية للتطبيق"""
    SmartHubApp(page)


if __name__ == "__main__":
    ft.run(main)

