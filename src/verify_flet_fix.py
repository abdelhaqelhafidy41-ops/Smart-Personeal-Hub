import flet as ft
from main import SmartHubApp

obj = type('Dummy', (), {'is_dark_mode': True, 'is_rtl': True})()
field = SmartHubApp.make_text_field(obj, 'Test', 250)
dropdown = SmartHubApp.make_dropdown(obj, 'Status', [('A', 'A')], 250)
print(type(field).__name__, field.content_padding)
print(type(dropdown).__name__, dropdown.content_padding)
