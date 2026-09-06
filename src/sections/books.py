import shutil
import sqlite3
from datetime import datetime

import flet as ft

from sections.core import COVERS_PATH, DB_PATH


class BookLibrary:
    @staticmethod
    def add_book(title: str, author: str, cover_path: str, progress: float,
                 start_date: str, end_date: str, rating: float):
        """إضافة كتاب جديد"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO books (title, author, cover_path, progress,
                     start_date, end_date, rating)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (title, author, cover_path, progress, start_date, end_date, rating))
        conn.commit()
        conn.close()

    @staticmethod
    def get_books():
        """الحصول على جميع الكتب"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM books')
        books = c.fetchall()
        conn.close()
        return books

    @staticmethod
    def update_book(book_id: int, progress: float, rating: float = None):
        """تحديث تقدم الكتاب والتقييم"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if rating is not None:
            c.execute('UPDATE books SET progress = ?, rating = ? WHERE id = ?',
                      (progress, rating, book_id))
        else:
            c.execute('UPDATE books SET progress = ? WHERE id = ?', (progress, book_id))
        conn.commit()
        conn.close()

    @staticmethod
    def edit_book(book_id: int, title: str, author: str, progress: float, start_date: str, end_date: str, rating: float):
        """تعديل بيانات كتاب"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''UPDATE books SET title = ?, author = ?, progress = ?, start_date = ?, end_date = ?, rating = ?
                     WHERE id = ?''',
                  (title, author, progress, start_date, end_date, rating, book_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_book(book_id: int):
        """حذف كتاب"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def save_cover(source_path: str, book_id: int) -> str:
        """حفظ صورة الغلاف"""
        dest_path = COVERS_PATH / f"cover_{book_id}_{datetime.now().timestamp()}.png"
        shutil.copy(source_path, str(dest_path))
        return str(dest_path)


def build_books_section(app) -> ft.Control:
    """بناء قسم الكتب"""
    editing_book_id = None

    def clear_fields():
        book_title_input.value = ""
        book_author_input.value = ""
        book_progress_input.value = ""
        book_rating_input.value = ""
        book_start_date_input.value = ""
        book_end_date_input.value = ""
        nonlocal editing_book_id
        editing_book_id = None
        add_book_button.text = "إضافة كتاب" if app.is_rtl else "Add Book"
        app.page.update()

    def add_book(e):
        title = book_title_input.value
        author = book_author_input.value
        progress = float(book_progress_input.value or 0)
        rating = float(book_rating_input.value or 0)
        start_date = book_start_date_input.value
        end_date = book_end_date_input.value

        if title and author:
            if editing_book_id is not None:
                BookLibrary.edit_book(editing_book_id, title, author, progress, start_date, end_date, rating)
            else:
                BookLibrary.add_book(title, author, "", progress, start_date, end_date, rating)
            clear_fields()
            refresh_books()
            app.page.update()
            app.build_ui()

    def refresh_books():
        books_list.controls.clear()
        books = BookLibrary.get_books()
        for book in books:
            is_read = float(book[4] or 0) >= 100
            book_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(book[1], size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"المؤلف: {book[2]}" if app.is_rtl else f"Author: {book[2]}", size=12),
                        ft.ProgressBar(value=min(max(float(book[4] or 0) / 100, 0), 1)),
                        ft.Text(f"التقدم: {book[4]}%" if app.is_rtl else f"Progress: {book[4]}%", size=10),
                        ft.Text(f"التقييم: {book[7]}/5 ⭐" if app.is_rtl else f"Rating: {book[7]}/5 ⭐", size=10),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT, on_click=lambda e, b=book: fill_book_for_edit(b)),
                            ft.IconButton(ft.Icons.DELETE, on_click=lambda e, bid=book[0]: (BookLibrary.delete_book(bid), refresh_books())),
                            ft.IconButton(ft.Icons.DONE_ALL, on_click=lambda e, bid=book[0]: (BookLibrary.update_book(bid, 100, float(book[7] or 5)), refresh_books())),
                        ]),
                    ]),
                    padding=15,
                ),
                margin=ft.Margin(0, 5, 0, 5),
            )
            books_list.controls.append(book_card)
        app.page.update()

    def fill_book_for_edit(book):
        nonlocal editing_book_id
        editing_book_id = book[0]
        book_title_input.value = book[1]
        book_author_input.value = book[2]
        book_progress_input.value = str(book[4])
        book_rating_input.value = str(book[7])
        book_start_date_input.value = book[5] or ""
        book_end_date_input.value = book[6] or ""
        add_book_button.text = "حفظ التعديل" if app.is_rtl else "Save Edit"
        app.page.update()

    book_title_input = app.make_text_field("عنوان الكتاب" if app.is_rtl else "Book Title", width=260)
    book_author_input = app.make_text_field("المؤلف" if app.is_rtl else "Author", width=260)
    book_progress_input = app.make_text_field("التقدم %" if app.is_rtl else "Progress %", width=180)
    book_rating_input = app.make_text_field("التقييم" if app.is_rtl else "Rating", width=180)
    book_start_date_input = app.make_text_field("تاريخ البداية" if app.is_rtl else "Start Date", width=180)
    book_end_date_input = app.make_text_field("تاريخ النهاية" if app.is_rtl else "End Date", width=180)

    add_book_button = app.make_action_button("إضافة كتاب" if app.is_rtl else "Add Book", add_book, width=170)
    books_list = ft.ListView(expand=True, spacing=10)

    refresh_books()

    return ft.Column([
        ft.Text("مكتبة الكتب" if app.is_rtl else "Book Library", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([book_title_input, book_author_input, book_progress_input, book_rating_input], wrap=True),
        ft.Row([book_start_date_input, book_end_date_input, add_book_button], wrap=True),
        ft.Divider(),
        books_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
