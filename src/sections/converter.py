import sqlite3

import flet as ft

from sections.core import DB_PATH


class UnitConverter:
    LENGTH_UNITS = {"متر": 1, "كيلومتر": 1000, "سنتيمتر": 0.01, "ملي": 0.001, "ميل": 1609.34, "قدم": 0.3048}
    WEIGHT_UNITS = {"كيلوجرام": 1, "جرام": 0.001, "طن": 1000, "باوند": 0.453592}
    TEMPERATURE = {"سيليزيوس": lambda x: x, "فهرنهايت": lambda x: (x * 9/5) + 32, "كلفن": lambda x: x + 273.15}
    TIME_UNITS = {"ثانية": 1, "دقيقة": 60, "ساعة": 3600, "يوم": 86400}

    @staticmethod
    def convert_length(value: float, from_unit: str, to_unit: str) -> float:
        """تحويل الطول"""
        base_value = value * UnitConverter.LENGTH_UNITS[from_unit]
        return base_value / UnitConverter.LENGTH_UNITS[to_unit]

    @staticmethod
    def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
        """تحويل الوزن"""
        base_value = value * UnitConverter.WEIGHT_UNITS[from_unit]
        return base_value / UnitConverter.WEIGHT_UNITS[to_unit]

    @staticmethod
    def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
        """تحويل درجة الحرارة"""
        if from_unit == "سيليزيوس":
            celsius = value
        elif from_unit == "فهرنهايت":
            celsius = (value - 32) * 5/9
        elif from_unit == "كلفن":
            celsius = value - 273.15

        if to_unit == "سيليزيوس":
            return celsius
        elif to_unit == "فهرنهايت":
            return (celsius * 9/5) + 32
        elif to_unit == "كلفن":
            return celsius + 273.15

    @staticmethod
    def convert_time(value: float, from_unit: str, to_unit: str) -> float:
        """تحويل الوقت"""
        base_value = value * UnitConverter.TIME_UNITS[from_unit]
        return base_value / UnitConverter.TIME_UNITS[to_unit]

    @staticmethod
    def add_currency_rate(currency: str, rate: float):
        """إضافة سعر صرف للعملة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM rates WHERE currency = ?', (currency,))
        c.execute('INSERT INTO rates (currency, rate) VALUES (?, ?)', (currency, rate))
        conn.commit()
        conn.close()

    @staticmethod
    def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
        """تحويل العملات"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT rate FROM rates WHERE currency = ?', (from_currency,))
        from_rate = c.fetchone()
        c.execute('SELECT rate FROM rates WHERE currency = ?', (to_currency,))
        to_rate = c.fetchone()
        conn.close()

        if from_rate and to_rate:
            return (amount / from_rate[0]) * to_rate[0]
        return 0

    @staticmethod
    def add_conversion_history(from_value: str, to_value: str, result: float):
        """إضافة سجل التحويل"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        date = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT INTO history (from_value, to_value, result, date)
                     VALUES (?, ?, ?, ?)''',
                  (from_value, to_value, result, date))
        conn.commit()
        conn.close()

    @staticmethod
    def get_conversion_history() -> list:
        """الحصول على آخر 10 عمليات تحويل"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM history ORDER BY id DESC LIMIT 10')
        history = c.fetchall()
        conn.close()
        return history


def build_converter_section(app) -> ft.Control:
    """بناء قسم محول الوحدات"""
    def convert_value(e):
        try:
            value = float(input_value.value)
            from_unit = from_unit_dropdown.value
            to_unit = to_unit_dropdown.value
            converter_type = converter_type_dropdown.value

            if converter_type == "length":
                result = UnitConverter.convert_length(value, from_unit, to_unit)
            elif converter_type == "weight":
                result = UnitConverter.convert_weight(value, from_unit, to_unit)
            elif converter_type == "temperature":
                result = UnitConverter.convert_temperature(value, from_unit, to_unit)
            elif converter_type == "time":
                result = UnitConverter.convert_time(value, from_unit, to_unit)
            else:
                result = 0

            result_text.value = f"النتيجة: {result:.4f}" if app.is_rtl else f"Result: {result:.4f}"
            UnitConverter.add_conversion_history(f"{value} {from_unit}", f"{result} {to_unit}", result)
            app.page.update()
        except Exception:
            result_text.value = "خطأ في الحساب" if app.is_rtl else "Error in calculation"
            app.page.update()

    def update_units(e):
        converter_type = converter_type_dropdown.value
        if converter_type == "length":
            units = list(UnitConverter.LENGTH_UNITS.keys())
        elif converter_type == "weight":
            units = list(UnitConverter.WEIGHT_UNITS.keys())
        elif converter_type == "temperature":
            units = list(UnitConverter.TEMPERATURE.keys())
        elif converter_type == "time":
            units = list(UnitConverter.TIME_UNITS.keys())
        else:
            units = []

        from_unit_dropdown.options = [ft.dropdown.Option(u, u) for u in units]
        to_unit_dropdown.options = [ft.dropdown.Option(u, u) for u in units]
        if units:
            from_unit_dropdown.value = units[0]
            to_unit_dropdown.value = units[1] if len(units) > 1 else units[0]
        app.page.update()

    def refresh_history():
        history_list.controls.clear()
        history = UnitConverter.get_conversion_history()
        for record in history:
            history_list.controls.append(
                ft.Text(f"{record[1]} -> {record[2]} = {record[3]:.4f} ({record[4]})", size=11)
            )
        app.page.update()

    input_value = app.make_text_field("القيمة" if app.is_rtl else "Value", width=250)

    converter_type_dropdown = app.make_dropdown(
        "النوع" if app.is_rtl else "Type",
        [
            ft.dropdown.Option("length", "الطول" if app.is_rtl else "Length"),
            ft.dropdown.Option("weight", "الوزن" if app.is_rtl else "Weight"),
            ft.dropdown.Option("temperature", "الحرارة" if app.is_rtl else "Temperature"),
            ft.dropdown.Option("time", "الوقت" if app.is_rtl else "Time"),
        ],
        width=200,
        on_select=update_units,
    )

    from_unit_dropdown = app.make_dropdown("من" if app.is_rtl else "From", [], width=200)
    to_unit_dropdown = app.make_dropdown("إلى" if app.is_rtl else "To", [], width=200)

    convert_button = ft.ElevatedButton(
        "تحويل" if app.is_rtl else "Convert",
        on_click=convert_value,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color="#22c55e")
    history_list = ft.ListView(expand=True, spacing=5)

    update_units(None)
    refresh_history()

    return ft.Column([
        ft.Text("محول الوحدات" if app.is_rtl else "Unit Converter", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([input_value, converter_type_dropdown, from_unit_dropdown, to_unit_dropdown, convert_button], wrap=True),
        result_text,
        ft.Divider(),
        ft.Text("آخر 10 عمليات:" if app.is_rtl else "Last 10 conversions:", size=14, weight=ft.FontWeight.BOLD),
        history_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
