import json
import sqlite3
from datetime import datetime

import flet as ft
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sections.core import DB_PATH, EXPORTS_PATH


class InvoiceManager:
    @staticmethod
    def add_product(name: str, price: float, category: str = "عام"):
        """إضافة منتج"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO products (name, price, category) VALUES (?, ?, ?)',
                  (name, price, category))
        conn.commit()
        conn.close()

    @staticmethod
    def get_products() -> list:
        """الحصول على جميع المنتجات"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM products')
        products = c.fetchall()
        conn.close()
        return products

    @staticmethod
    def delete_product(product_id: int):
        """حذف منتج من قائمة الفواتير"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_last_invoice_number() -> str:
        """الحصول على آخر رقم فاتورة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1')
        result = c.fetchone()
        conn.close()
        return result[0] if result else ""

    @staticmethod
    def create_invoice(items: list) -> tuple:
        """إنشاء فاتورة جديدة"""
        total = 0
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        invoice_data = []
        for product_id, quantity in items:
            c.execute('SELECT price FROM products WHERE id = ?', (product_id,))
            result = c.fetchone()
            if result:
                price = result[0]
                item_total = price * quantity
                total += item_total
                invoice_data.append({"product_id": product_id, "quantity": quantity, "price": price})

        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date = datetime.now().strftime("%Y-%m-%d")
        items_str = json.dumps(invoice_data, ensure_ascii=False)
        profit = total * 0.2

        c.execute('''INSERT INTO invoices (invoice_number, date, total, profit, items)
                     VALUES (?, ?, ?, ?, ?)''',
                  (invoice_number, date, total, profit, items_str))
        conn.commit()
        conn.close()

        return invoice_number, total, profit

    @staticmethod
    def export_invoice_to_pdf(invoice_number: str):
        """تصدير الفاتورة إلى PDF"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
        invoice = c.fetchone()
        conn.close()

        if not invoice:
            return None

        filename = EXPORTS_PATH / f"فاتورة_{invoice_number}.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []

        story.append(Paragraph(f"الفاتورة رقم: {invoice_number}", getSampleStyleSheet()['Heading1']))
        story.append(Paragraph(f"التاريخ: {invoice[2]}", getSampleStyleSheet()['Normal']))
        story.append(Spacer(1, 12))

        items = json.loads(invoice[5])
        data = [["المنتج", "السعر", "الكمية", "الإجمالي"]]
        for item in items:
            data.append([
                str(item['product_id']),
                str(item['price']),
                str(item['quantity']),
                str(item['price'] * item['quantity'])
            ])

        data.append(["", "", "الإجمالي:", str(invoice[3])])
        data.append(["", "", "الربح:", str(invoice[4])])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(table)

        doc.build(story)
        return str(filename)


def build_invoices_section(app) -> ft.Control:
    """بناء قسم الفواتير"""
    def add_product(e):
        name = product_name_input.value
        try:
            price = float(product_price_input.value or 0)
        except (TypeError, ValueError):
            return
        category = product_category_input.value

        if name and price:
            InvoiceManager.add_product(name, price, category)
            product_name_input.value = ""
            product_price_input.value = ""
            product_category_input.value = ""
            refresh_products()
            app.page.update()

    def refresh_products():
        products_list.controls.clear()
        products = InvoiceManager.get_products()
        for idx, product in enumerate(products):
            product_row = ft.Row([
                ft.Checkbox(label=product[1], value=False),
                ft.Text(f"السعر: {product[2]}" if app.is_rtl else f"Price: {product[2]}", expand=True),
                ft.Text(product[3]),
                ft.IconButton(
                    ft.Icons.DELETE,
                    tooltip="حذف" if app.is_rtl else "Delete",
                    on_click=lambda e, pid=product[0]: (InvoiceManager.delete_product(pid), refresh_products())
                )
            ], spacing=10)
            products_list.controls.append(product_row)
        app.page.update()

    def create_invoice(e):
        selected_items = []
        products = InvoiceManager.get_products()
        for idx, control in enumerate(products_list.controls):
            if isinstance(control, ft.Row) and len(control.controls) > 0 and control.controls[0].value:
                if idx < len(products):
                    selected_items.append((products[idx][0], int(quantity_input.value or 1)))

        if selected_items:
            invoice_number, total, profit = InvoiceManager.create_invoice(selected_items)
            app.last_invoice_number = invoice_number
            result_text.value = f"الفاتورة: {invoice_number} | الإجمالي: {total}" if app.is_rtl else f"Invoice: {invoice_number} | Total: {total}"
            app.page.update()
        else:
            result_text.value = "اختر منتجاً" if app.is_rtl else "Select a product"
            app.page.update()

    def export_invoice(e):
        invoice_number = app.last_invoice_number or InvoiceManager.get_last_invoice_number()
        if invoice_number:
            filename = InvoiceManager.export_invoice_to_pdf(invoice_number)
            if filename:
                result_text.value = f"تم التصدير: {filename}" if app.is_rtl else f"Exported: {filename}"
        else:
            result_text.value = "لا توجد فاتورة" if app.is_rtl else "No invoice available"
        app.page.update()

    product_name_input = app.make_text_field("اسم المنتج" if app.is_rtl else "Product Name", width=240)
    product_price_input = app.make_text_field("السعر" if app.is_rtl else "Price", width=150)
    product_category_input = app.make_text_field("التصنيف" if app.is_rtl else "Category", width=180)
    quantity_input = app.make_text_field("الكمية" if app.is_rtl else "Quantity", width=120)

    add_product_button = app.make_action_button("إضافة منتج" if app.is_rtl else "Add Product", add_product, width=170)
    create_invoice_button = app.make_action_button("إنشاء فاتورة" if app.is_rtl else "Create Invoice", create_invoice, width=170)
    export_invoice_button = app.make_action_button("تصدير PDF" if app.is_rtl else "Export PDF", export_invoice, width=170)

    products_list = ft.ListView(expand=True, spacing=5)
    result_text = ft.Text("", size=12, color="#3b82f6")

    refresh_products()

    return ft.Column([
        ft.Text("برنامج الفواتير" if app.is_rtl else "Invoice Manager", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([product_name_input, product_price_input, product_category_input, add_product_button], wrap=True),
        ft.Row([quantity_input, create_invoice_button, export_invoice_button], wrap=True),
        result_text,
        ft.Divider(),
        ft.Text("المنتجات:" if app.is_rtl else "Products:", size=14, weight=ft.FontWeight.BOLD),
        products_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
