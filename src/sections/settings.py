import flet as ft

from sections.core import DataBackupManager


def build_settings_section(app) -> ft.Control:
    """بناء قسم الإعدادات"""
    def refresh_backups():
        backups = DataBackupManager.list_backups()
        backup_options = [ft.dropdown.Option(str(path), path.name) for path in backups]
        backup_dropdown.options = backup_options
        if backup_options:
            backup_dropdown.value = str(backups[0])
        else:
            backup_dropdown.value = None
        app.page.update()

    def create_backup(e):
        backup_path = DataBackupManager.create_backup(backup_name_input.value or "backup")
        status_text.value = f"تم إنشاء نسخة احتياطية: {backup_path}" if app.is_rtl else f"Backup created: {backup_path}"
        refresh_backups()
        app.page.update()

    def export_backup(e):
        selected = backup_dropdown.value
        if not selected:
            status_text.value = "لا توجد نسخة احتياطية" if app.is_rtl else "No backup available"
            app.page.update()
            return
        exported = DataBackupManager.export_backup(selected)
        status_text.value = f"تم تصدير النسخة: {exported}" if app.is_rtl else f"Backup exported: {exported}"
        app.page.update()

    def restore_backup(e):
        selected = backup_dropdown.value
        if not selected:
            status_text.value = "لا توجد نسخة احتياطية" if app.is_rtl else "No backup available"
            app.page.update()
            return
        success = DataBackupManager.restore_backup(selected)
        status_text.value = "تمت الاستعادة بنجاح" if (success and app.is_rtl) else ("Restore successful" if success else "فشل الاستعادة" if app.is_rtl else "Restore failed")
        app.page.update()

    def delete_backup_selected(e):
        selected = backup_dropdown.value
        if not selected:
            status_text.value = "لا توجد نسخة احتياطية" if app.is_rtl else "No backup available"
            app.page.update()
            return
        DataBackupManager.delete_backup(selected)
        status_text.value = "تم حذف النسخة الاحتياطية" if app.is_rtl else "Backup deleted"
        refresh_backups()
        app.page.update()

    def delete_all_data(e):
        DataBackupManager.delete_all_data()
        status_text.value = "تم حذف جميع البيانات" if app.is_rtl else "All data has been deleted"
        app.page.update()

    def toggle_lang(e):
        app.is_rtl = not app.is_rtl
        app.save_settings()
        app.build_ui()

    def toggle_theme(e):
        app.is_dark_mode = not app.is_dark_mode
        app.save_settings()
        app.update_theme()
        app.build_ui()

    backup_name_input = app.make_text_field("اسم النسخة الاحتياطية" if app.is_rtl else "Backup name", width=260)
    backup_dropdown = app.make_dropdown("النسخ الاحتياطية" if app.is_rtl else "Backups", [], width=260)
    status_text = ft.Text("", size=12, color="#3b82f6")
    theme_toggle = ft.Switch(value=app.is_dark_mode, on_change=toggle_theme)
    lang_toggle = ft.Switch(value=app.is_rtl, on_change=toggle_lang)

    refresh_backups()

    return ft.Column([
        ft.Text("إعدادات التطبيق" if app.is_rtl else "App Settings", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Column([
                ft.Text("الوضع الداكن" if app.is_rtl else "Dark Mode", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("تشغيل/إيقاف المظهر الليلي" if app.is_rtl else "Enable or disable the dark theme", size=12, color="#94a3b8"),
            ], expand=True),
            theme_toggle,
        ], spacing=10),
        ft.Row([
            ft.Column([
                ft.Text("العربية / English" if app.is_rtl else "Arabic / English", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("تبديل اتجاه الواجهة" if app.is_rtl else "Toggle interface direction", size=12, color="#94a3b8"),
            ], expand=True),
            lang_toggle,
        ], spacing=10),
        ft.Divider(),
        ft.Text("النسخ الاحتياطية" if app.is_rtl else "Backup & Restore", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([
            backup_name_input,
            ft.ElevatedButton("حفظ نسخة" if app.is_rtl else "Save Backup", on_click=create_backup,
                style=ft.ButtonStyle(
                    color="#ffffff",
                    bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
                    shape=ft.RoundedRectangleBorder(radius=12),
                )),
        ], wrap=True),
        ft.Row([
            backup_dropdown,
            ft.ElevatedButton("تصدير" if app.is_rtl else "Export", on_click=export_backup,
                style=ft.ButtonStyle(
                    color="#ffffff",
                    bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
                    shape=ft.RoundedRectangleBorder(radius=12),
                )),
            ft.ElevatedButton("استعادة" if app.is_rtl else "Restore", on_click=restore_backup,
                style=ft.ButtonStyle(
                    color="#ffffff",
                    bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
                    shape=ft.RoundedRectangleBorder(radius=12),
                )),
            ft.ElevatedButton("حذف النسخة" if app.is_rtl else "Delete Backup", on_click=delete_backup_selected,
                style=ft.ButtonStyle(
                    color="#ffffff",
                    bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
                    shape=ft.RoundedRectangleBorder(radius=12),
                )),
        ], wrap=True),
        ft.ElevatedButton("حذف كل البيانات" if app.is_rtl else "Delete All Data", on_click=delete_all_data, color="#ffffff", bgcolor="#ef4444"),
        status_text,
        ft.Divider(),
        ft.Text("الحالة الحالية" if app.is_rtl else "Current status", size=16, weight=ft.FontWeight.BOLD),
        ft.Text(
            f"اللغة: {'عربي' if app.is_rtl else 'English'} | النمط: {'داكن' if app.is_dark_mode else 'فاتح'}" if app.is_rtl else
            f"Language: {'Arabic' if app.is_rtl else 'English'} | Theme: {'Dark' if app.is_dark_mode else 'Light'}",
            size=13,
            color="#3b82f6",
        )
    ], expand=True, spacing=16)
