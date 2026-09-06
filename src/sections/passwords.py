import random
import sqlite3
import string

import flet as ft

from sections.core import DB_PATH, decrypt_password, encrypt_password


class PasswordManager:
    @staticmethod
    def add_password(website: str, email: str, password: str, note: str = ""):
        """إضافة كلمة سر جديدة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        encrypted = encrypt_password(password)
        c.execute('''INSERT INTO passwords (website, email, password, note)
                     VALUES (?, ?, ?, ?)''',
                  (website, email, encrypted, note))
        conn.commit()
        conn.close()

    @staticmethod
    def get_passwords():
        """الحصول على جميع كلمات السر"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, website, email, note FROM passwords')
        passwords = c.fetchall()
        conn.close()
        return passwords

    @staticmethod
    def get_password(password_id: int) -> str:
        """الحصول على كلمة السر المشفرة وفك تشفيرها"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT password FROM passwords WHERE id = ?', (password_id,))
        result = c.fetchone()
        conn.close()
        if result:
            return decrypt_password(result[0])
        return ""

    @staticmethod
    def generate_password(length: int = 16) -> str:
        """توليد كلمة سر قوية"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def delete_password(password_id: int):
        """حذف كلمة سر"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
        conn.commit()
        conn.close()


def build_passwords_section(app) -> ft.Control:
    """بناء قسم كلمات السر"""
    def add_password(e):
        website = pwd_website_input.value
        email = pwd_email_input.value
        password = pwd_password_input.value
        note = pwd_note_input.value

        if website and email and password:
            PasswordManager.add_password(website, email, password, note)
            pwd_website_input.value = ""
            pwd_email_input.value = ""
            pwd_password_input.value = ""
            pwd_note_input.value = ""
            refresh_passwords()
            app.page.update()
            app.build_ui()

    def generate_pwd(e):
        generated = PasswordManager.generate_password()
        pwd_password_input.value = generated
        app.page.update()

    def refresh_passwords():
        passwords_list.controls.clear()
        passwords = PasswordManager.get_passwords()
        for pwd in passwords:
            masked = "●●●●●●●●" if pwd[3] is not None else ""
            website = pwd[1]
            email = pwd[2]
            note = pwd[3] if pwd[3] else ""
            password_value = PasswordManager.get_password(pwd[0])
            pwd_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(website, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(email, size=12),
                        ft.Text(masked, size=10, color="#94a3b8"),
                        ft.Text(note, size=10, color="#64748b"),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.CONTENT_COPY_ROUNDED,
                                tooltip="نسخ الموقع" if app.is_rtl else "Copy website",
                                on_click=lambda e, value=website: copy_to_clipboard(value, "website")
                            ),
                            ft.IconButton(
                                ft.Icons.EMAIL_ROUNDED,
                                tooltip="نسخ الإيميل" if app.is_rtl else "Copy email",
                                on_click=lambda e, value=email: copy_to_clipboard(value, "email")
                            ),
                            ft.IconButton(
                                ft.Icons.LOCK_RESET_ROUNDED,
                                tooltip="نسخ كلمة المرور" if app.is_rtl else "Copy password",
                                on_click=lambda e, value=password_value: copy_to_clipboard(value, "password")
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, pid=pwd[0]: (PasswordManager.delete_password(pid), refresh_passwords())
                            ),
                        ]),
                    ]),
                    padding=15,
                ),
                margin=ft.Margin(0, 5, 0, 5),
            )
            passwords_list.controls.append(pwd_card)
        app.page.update()

    async def copy_to_clipboard(value: str, field_name: str = "password"):
        if not value:
            return
        await app.page.clipboard.set(value)
        label = {
            "website": "تم نسخ الموقع" if app.is_rtl else "Website copied",
            "email": "تم نسخ الإيميل" if app.is_rtl else "Email copied",
            "password": "تم نسخ كلمة المرور" if app.is_rtl else "Password copied",
        }.get(field_name, "تم النسخ" if app.is_rtl else "Copied")
        app.page.show_snack_bar(ft.SnackBar(ft.Text(label)))

    pwd_website_input = app.make_text_field("الموقع" if app.is_rtl else "Website", width=240)
    pwd_email_input = app.make_text_field("الإيميل" if app.is_rtl else "Email", width=240)
    pwd_password_input = app.make_text_field("كلمة السر" if app.is_rtl else "Password", width=240, password=True)
    pwd_note_input = app.make_text_field("ملاحظة" if app.is_rtl else "Note", width=240)

    add_pwd_button = app.make_action_button("إضافة" if app.is_rtl else "Add", add_password, width=150)
    generate_btn = app.make_action_button("توليد عشوائي" if app.is_rtl else "Generate", generate_pwd, width=170)

    passwords_list = ft.ListView(expand=True, spacing=10)

    refresh_passwords()

    return ft.Column([
        ft.Text("مدير كلمات السر" if app.is_rtl else "Password Manager", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([pwd_website_input, pwd_email_input, pwd_password_input, pwd_note_input], wrap=True),
        ft.Row([add_pwd_button, generate_btn], wrap=True),
        ft.Divider(),
        passwords_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
