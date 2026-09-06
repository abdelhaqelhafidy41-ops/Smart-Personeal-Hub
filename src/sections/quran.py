import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path

import flet as ft

from sections.core import DB_PATH


class QuranManager:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DEFAULT_QURAN_FILE = PROJECT_ROOT / "quran-json" / "dist" / "quran.json"
    DEFAULT_QURAN_EN_FILE = PROJECT_ROOT / "quran-json" / "dist" / "quran_transliteration.json"
    LEGACY_QURAN_FILE = Path(__file__).resolve().parents[1] / "quran.json"
    QURAN_FILE = DEFAULT_QURAN_FILE if DEFAULT_QURAN_FILE.exists() else LEGACY_QURAN_FILE

    @staticmethod
    def get_quran_file(language: str = "arabic"):
        if language == "english":
            candidates = [
                QuranManager.PROJECT_ROOT / "quran-json" / "dist" / "quran_transliteration.json",
                QuranManager.PROJECT_ROOT / "quran-json" / "dist" / "quran_en.json",
                Path(__file__).resolve().parents[1] / "quran_en.json",
                Path(__file__).resolve().parents[1] / "quran_transliteration.json",
            ]
            for path in candidates:
                if path.exists():
                    return path
            return QuranManager.DEFAULT_QURAN_EN_FILE
        candidates = [
            Path(QuranManager.QURAN_FILE),
            QuranManager.DEFAULT_QURAN_FILE,
            QuranManager.LEGACY_QURAN_FILE,
        ]
        for quran_path in candidates:
            if Path(quran_path).exists():
                return Path(quran_path)
        return QuranManager.DEFAULT_QURAN_FILE

    @staticmethod
    def load_quran_data(language: str = "arabic") -> list:
        """تحميل بيانات القرآن من JSON حسب اللغة المختارة"""
        quran_path = QuranManager.get_quran_file(language)
        if not quran_path.exists():
            return []
        with open(quran_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("surahs"), list):
                return data["surahs"]
            if isinstance(data, list):
                return data
        return []

    @staticmethod
    def set_daily_target(surah_number: int, target: int):
        """تعيين الورد اليومي للسورة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute('DELETE FROM quran_progress WHERE surah_number = ? AND date = ?',
                  (surah_number, today))
        c.execute('''INSERT INTO quran_progress (surah_number, daily_target, completed, date)
                     VALUES (?, ?, 0, ?)''',
                  (surah_number, target, today))
        conn.commit()
        conn.close()

    @staticmethod
    def mark_verses_completed(surah_number: int, completed_count: int):
        """تحديث عدد الآيات المكتملة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute('''UPDATE quran_progress SET completed = ? 
                     WHERE surah_number = ? AND date = ?''',
                  (completed_count, surah_number, today))
        conn.commit()
        conn.close()

    @staticmethod
    def get_progress() -> dict:
        """الحصول على التقدم الحالي"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT surah_number, daily_target, completed FROM quran_progress')
        data = c.fetchall()
        conn.close()

        progress = {}
        for row in data:
            surah = row[0]
            target = row[1]
            completed = row[2]
            progress_percent = (completed / target * 100) if target > 0 else 0
            progress[surah] = {"target": target, "completed": completed, "percent": progress_percent}

        return progress

    @staticmethod
    def test_completion(surah_number: int, partial_verse: str, full_verse: str) -> bool:
        """اختبار إكمال الآية"""
        return full_verse.startswith(partial_verse)


def build_quran_section(app) -> ft.Control:
    """بناء قسم القرآن مع ثلاثة أقسام: الحفظ، القراءة، الاختبار"""

    def normalize_text(value: str) -> str:
        return " ".join((value or "").split()).strip()

    def get_quran_language() -> str:
        value = (quran_language_dropdown.value or "arabic").lower()
        return "english" if value == "english" else "arabic"

    def load_surahs():
        language = get_quran_language()
        surahs_dropdown.options = []
        test_surah_dropdown.options = []
        quran_data = QuranManager.load_quran_data(language)
        for surah in quran_data:
            surah_id = int(surah.get('id', 1))
            label = f"{surah_id}. {surah.get('translation') if language == 'english' else surah.get('name', 'سورة')}"
            option = ft.dropdown.Option(str(surah_id), label)
            surahs_dropdown.options.append(option)
            test_surah_dropdown.options.append(option)
        if not surahs_dropdown.value and surahs_dropdown.options:
            surahs_dropdown.value = str(1)
        if not test_surah_dropdown.value and test_surah_dropdown.options:
            test_surah_dropdown.value = str(1)
        refresh_reading_panel()
        refresh_test_prompt()
        app.page.update()

    def get_selected_surah():
        quran_data = QuranManager.load_quran_data(get_quran_language())
        surah_id = int(surahs_dropdown.value or 1)
        for surah in quran_data:
            if int(surah.get('id', 1)) == surah_id:
                return surah
        return quran_data[0] if quran_data else {}

    def get_test_surah():
        surah_id = int(test_surah_dropdown.value or 1)
        quran_data = QuranManager.load_quran_data(get_quran_language())
        for surah in quran_data:
            if int(surah.get('id', 1)) == surah_id:
                return surah
        return quran_data[0] if quran_data else {}

    def get_verse_display_text(surah: dict, verse_index: int) -> str:
        if not surah:
            return ""
        verses = surah.get('verses', [])
        if not verses or verse_index < 0 or verse_index >= len(verses):
            return ""
        verse = verses[verse_index]
        if get_quran_language() == 'english':
            return (
                verse.get('translation')
                or verse.get('transliteration')
                or verse.get('text')
                or ""
            ).strip()
        return (verse.get('text') or '').strip()

    def refresh_reading_panel():
        surah = get_selected_surah()
        language = get_quran_language()
        if language == 'english':
            reading_name.value = f"{surah.get('translation', surah.get('transliteration', ''))} - {surah.get('transliteration', '')}"
            reading_meta.value = f"{surah.get('type', '')} | Verses: {surah.get('total_verses', 0)}"
        else:
            reading_name.value = f"{surah.get('name', '')} - {surah.get('transliteration', '')}"
            reading_meta.value = f"{surah.get('type', '')} | عدد الآيات: {surah.get('total_verses', 0)}"

        lines = []
        for verse in surah.get('verses', []):
            verse_id = verse.get('id', '')
            verse_text = get_verse_display_text(surah, int(verse_id) - 1) if verse_id else ""
            lines.append(f"{verse_id}. {verse_text}" if verse_text else str(verse_id))

        reading_text.value = "  " + "  ".join(lines)
        reading_text.text_align = ft.TextAlign.RIGHT if language == 'arabic' else ft.TextAlign.LEFT
        reading_text.color = "#e2e8f0" if app.is_dark_mode else "#0f172a"
        app.page.update()

    def set_target(e):
        surah_num = int(surahs_dropdown.value or 1)
        target = int(daily_target_input.value or 10)
        QuranManager.set_daily_target(surah_num, target)
        target_result_text.value = f"تم تعيين الورد: {target} آية" if app.is_rtl else f"Target set: {target} verses"
        app.page.update()

    def mark_completed(e):
        surah_num = int(surahs_dropdown.value or 1)
        completed = int(completed_input.value or 0)
        QuranManager.mark_verses_completed(surah_num, completed)
        progress = QuranManager.get_progress()
        if surah_num in progress:
            p = progress[surah_num]
            progress_result_text.value = f"التقدم: {p['completed']}/{p['target']} ({p['percent']:.1f}%)" if app.is_rtl else f"Progress: {p['completed']}/{p['target']} ({p['percent']:.1f}%)"
        app.page.update()

    def test_completion(e):
        surah = get_test_surah()
        verses = surah.get('verses', [])
        ayah_number = int(test_ayah_dropdown.value or 1)
        if ayah_number < 1 or ayah_number >= len(verses):
            ayah_number = 1
        expected = normalize_text(get_verse_display_text(surah, ayah_number))
        answer = normalize_text(test_answer_input.value or '')

        if answer == expected:
            test_result_text.value = "✓ صحيح" if app.is_rtl else "✓ Correct"
            test_result_text.color = "#22c55e"
        else:
            test_result_text.value = f"✗ خطأ - الإجابة الصحيحة: {expected}" if app.is_rtl else f"✗ Incorrect - Correct answer: {expected}"
            test_result_text.color = "#ef4444"
        app.page.update()

    def refresh_test_prompt():
        surah = get_test_surah()
        verses = surah.get('verses', [])
        if not verses:
            test_prompt_text.value = ""
            return

        options = [ft.dropdown.Option(str(i + 1), f"الآية {i + 1}" if get_quran_language() == 'arabic' else f"Verse {i + 1}") for i in range(1, len(verses))]
        test_ayah_dropdown.options = options
        if not test_ayah_dropdown.value and options:
            test_ayah_dropdown.value = str(1)

        ayah_number = int(test_ayah_dropdown.value or 1)
        if ayah_number < 1 or ayah_number >= len(verses):
            ayah_number = 1
        test_ayah_dropdown.value = str(ayah_number)

        current_ayah = get_verse_display_text(surah, ayah_number - 1)
        test_prompt_text.value = f"الآية الحالية: {current_ayah}\nأكمل الآية التالية:" if get_quran_language() == 'arabic' else f"Current verse: {current_ayah}\nComplete the next verse:"
        test_answer_input.value = ""
        test_answer_input.hint_text = "اكتب الآية التالية" if get_quran_language() == 'arabic' else "Write the next verse"
        test_result_text.value = ""
        app.page.update()

    def select_random_test_ayah():
        surah = get_test_surah()
        verses = surah.get('verses', [])
        if len(verses) < 2:
            return
        chosen_index = random.randint(1, len(verses) - 1)
        test_ayah_dropdown.value = str(chosen_index)
        refresh_test_prompt()
        app.page.update()

    quran_language_dropdown = ft.Dropdown(
        width=180,
        value="arabic",
        options=[
            ft.dropdown.Option("arabic", "العربية"),
            ft.dropdown.Option("english", "English"),
        ],
    )
    quran_language_dropdown.on_change = lambda e: load_surahs()

    surahs_dropdown = app.make_dropdown(
        "السورة" if app.is_rtl else "Surah",
        [],
        width=260,
        on_select=lambda e: refresh_reading_panel(),
    )

    daily_target_input = app.make_text_field("عدد الآيات اليومية" if app.is_rtl else "Daily Verses", width=200)
    set_target_button = ft.ElevatedButton(
        "تعيين الورد" if app.is_rtl else "Set Target",
        on_click=set_target,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )
    target_result_text = ft.Text("", size=12, color="#3b82f6")

    completed_input = app.make_text_field("عدد الآيات المكتملة" if app.is_rtl else "Completed Verses", width=200)
    mark_button = ft.ElevatedButton(
        "تحديث التقدم" if app.is_rtl else "Update Progress",
        on_click=mark_completed,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )
    progress_result_text = ft.Text("", size=12, color="#22c55e")

    reading_name = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
    reading_meta = ft.Text("", size=12, color="#94a3b8")
    reading_text = ft.Text("", selectable=True, size=16)

    test_surah_dropdown = app.make_dropdown(
        "السورة" if app.is_rtl else "Surah",
        [],
        width=260,
        on_select=lambda e: refresh_test_prompt(),
    )
    test_ayah_dropdown = app.make_dropdown(
        "الآية" if app.is_rtl else "Ayah",
        [],
        width=180,
        on_select=lambda e: refresh_test_prompt(),
    )
    test_prompt_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, selectable=True)
    test_answer_input = app.make_text_field("اكتب الآية التالية" if app.is_rtl else "Write the next verse", width=420, multiline=True)
    test_button = ft.ElevatedButton(
        "تحقق" if app.is_rtl else "Check",
        on_click=test_completion,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )
    random_ayah_button = ft.ElevatedButton(
        "آية عشوائية" if app.is_rtl else "Random Ayah",
        on_click=lambda e: select_random_test_ayah(),
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#0f766e" if app.is_dark_mode else "#14b8a6",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )
    test_result_text = ft.Text("", size=12)

    memorize_tab = ft.Column([
        ft.Text("الحفظ" if app.is_rtl else "Memorization", size=22, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Column([
                ft.Row([surahs_dropdown, daily_target_input, set_target_button], wrap=True),
                target_result_text,
                ft.Row([completed_input, mark_button], wrap=True),
                progress_result_text,
            ], spacing=12),
            padding=18,
            border_radius=18,
            bgcolor="#f8fafc" if not app.is_dark_mode else "#111827",
            border=ft.Border.all(1, "#e2e8f0" if not app.is_dark_mode else "#334155"),
        ),
    ], expand=True, spacing=12, scroll=ft.ScrollMode.AUTO)

    reading_tab = ft.Column([
        ft.Text("القراءة" if app.is_rtl else "Reading", size=22, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Row([
                ft.Text("اللغة" if app.is_rtl else "Language", weight=ft.FontWeight.BOLD),
                quran_language_dropdown,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=12,
            border_radius=16,
            bgcolor="#f8fafc" if not app.is_dark_mode else "#111827",
            border=ft.Border.all(1, "#cbd5e1" if not app.is_dark_mode else "#475569"),
        ),
        ft.Row([surahs_dropdown], wrap=True),
        ft.Container(
            content=ft.Column([
                reading_name,
                reading_meta,
                ft.Container(
                    content=ft.Column([reading_text], expand=True),
                    expand=True,
                    padding=16,
                    border_radius=16,
                    bgcolor="#f8fafc" if not app.is_dark_mode else "#0f172a",
                    border=ft.Border.all(1, "#60a5fa" if app.is_dark_mode else "#bfdbfe"),
                ),
            ], spacing=10),
            padding=14,
            border_radius=18,
            bgcolor="#ffffff" if not app.is_dark_mode else "#111827",
            border=ft.Border.all(1, "#dbeafe" if not app.is_dark_mode else "#334155"),
        ),
    ], expand=True, spacing=12, scroll=ft.ScrollMode.AUTO)

    test_tab = ft.Column([
        ft.Text("الإختبار" if app.is_rtl else "Test", size=22, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("اللغة" if app.is_rtl else "Language", weight=ft.FontWeight.BOLD),
                    quran_language_dropdown,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([test_surah_dropdown, test_ayah_dropdown, random_ayah_button], wrap=True),
                ft.Container(
                    content=ft.Column([
                        test_prompt_text,
                        test_answer_input,
                        ft.Row([test_button], wrap=True),
                        test_result_text,
                    ], spacing=12),
                    padding=16,
                    border_radius=18,
                    bgcolor="#f8fafc" if not app.is_dark_mode else "#0f172a",
                    border=ft.Border.all(1, "#d1fae5" if not app.is_dark_mode else "#2dd4bf"),
                ),
            ], spacing=12),
            padding=16,
            border_radius=18,
            bgcolor="#ffffff" if not app.is_dark_mode else "#111827",
            border=ft.Border.all(1, "#dbeafe" if not app.is_dark_mode else "#334155"),
        ),
    ], expand=True, spacing=12, scroll=ft.ScrollMode.AUTO)

    load_surahs()

    selected_tab_index = {"value": 0}

    def switch_tab(index: int):
        selected_tab_index["value"] = index
        tab_views = [memorize_tab, reading_tab, test_tab]
        active_view.content = tab_views[index]
        for i, btn in enumerate(tab_buttons):
            btn.bgcolor = "#2563eb" if i == index else "#334155"
            btn.color = "#ffffff"
        app.page.update()

    tab_buttons = [
        ft.ElevatedButton(
            "الحفظ" if app.is_rtl else "Memorization",
            on_click=lambda e, i=0: switch_tab(i),
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        ),
        ft.ElevatedButton(
            "القراءة" if app.is_rtl else "Reading",
            on_click=lambda e, i=1: switch_tab(i),
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#334155",
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        ),
        ft.ElevatedButton(
            "الإختبار" if app.is_rtl else "Test",
            on_click=lambda e, i=2: switch_tab(i),
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#334155",
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        ),
    ]

    active_view = ft.Container(content=memorize_tab, expand=True)
    switch_tab(0)

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Text("تطبيق القرآن الكريم" if app.is_rtl else "Quran App", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, color="#fbbf24"),
                        ft.Text("المحتوى" if app.is_rtl else "Content", size=12, color="#94a3b8"),
                    ], spacing=6),
                    padding=8,
                    border_radius=12,
                    bgcolor="#fef3c7" if not app.is_dark_mode else "#3f2d12",
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=8,
            margin=ft.Margin(0, 0, 0, 0),
        ),
        ft.Row(tab_buttons, wrap=True, spacing=10),
        active_view,
    ], expand=True, spacing=16)
