import json
import sqlite3
from datetime import datetime

import flet as ft

from sections.core import DB_PATH, EXPORTS_PATH


class RecipeManager:
    @staticmethod
    def add_recipe(name: str, image_path: str, ingredients: list, steps: list):
        """إضافة وصفة جديدة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        ingredients_str = json.dumps(ingredients, ensure_ascii=False)
        steps_str = json.dumps(steps, ensure_ascii=False)
        c.execute('''INSERT INTO recipes (name, image_path, ingredients, steps)
                     VALUES (?, ?, ?, ?)''',
                  (name, image_path, ingredients_str, steps_str))
        conn.commit()
        conn.close()

    @staticmethod
    def get_recipes():
        """الحصول على جميع الوصفات"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM recipes')
        recipes = c.fetchall()
        conn.close()
        return recipes

    @staticmethod
    def search_by_ingredient(ingredient: str) -> list:
        """البحث عن وصفات تحتوي على مكون معين"""
        recipes = RecipeManager.get_recipes()
        results = []
        for recipe in recipes:
            ingredients = json.loads(recipe[3])
            if any(ingredient.lower() in ing.lower() for ing in ingredients):
                results.append(recipe)
        return results

    @staticmethod
    def create_shopping_list(recipe_id: int) -> str:
        """إنشاء قائمة التسوق من الوصفة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT ingredients FROM recipes WHERE id = ?', (recipe_id,))
        result = c.fetchone()
        conn.close()

        if result:
            ingredients = json.loads(result[0])
            filename = EXPORTS_PATH / f"قائمة_تسوق_{recipe_id}_{datetime.now().strftime('%Y-%m-%d')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("قائمة التسوق\n")
                f.write("=" * 30 + "\n")
                for ingredient in ingredients:
                    f.write(f"☐ {ingredient}\n")
            return str(filename)
        return ""

    @staticmethod
    def delete_recipe(recipe_id: int):
        """حذف وصفة"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
        conn.commit()
        conn.close()


def build_recipes_section(app) -> ft.Control:
    """بناء قسم الوصفات"""
    def add_recipe(e):
        name = recipe_name_input.value
        ingredients = recipe_ingredients_input.value.split('\n')
        steps = recipe_steps_input.value.split('\n')

        if name and ingredients:
            RecipeManager.add_recipe(name, "", ingredients, steps)
            recipe_name_input.value = ""
            recipe_ingredients_input.value = ""
            recipe_steps_input.value = ""
            refresh_recipes()
            app.page.update()

    def refresh_recipes():
        recipes_list.controls.clear()
        recipes = RecipeManager.get_recipes()
        for recipe in recipes:
            ingredients = json.loads(recipe[3])
            recipe_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(recipe[1], size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"المكونات: {len(ingredients)}" if app.is_rtl else f"Ingredients: {len(ingredients)}", size=11),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.SHOPPING_CART,
                                tooltip="قائمة التسوق" if app.is_rtl else "Shopping List",
                                on_click=lambda e, rid=recipe[0]: create_shopping_list(rid)
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, rid=recipe[0]: (RecipeManager.delete_recipe(rid), refresh_recipes())
                            ),
                        ]),
                    ]),
                    padding=15,
                ),
                margin=ft.Margin(0, 5, 0, 5),
            )
            recipes_list.controls.append(recipe_card)
        app.page.update()

    def create_shopping_list(recipe_id: int):
        filename = RecipeManager.create_shopping_list(recipe_id)
        result_text.value = f"تم الإنشاء: {filename}" if app.is_rtl else f"Created: {filename}"
        app.page.update()

    def search_recipes(e):
        ingredient = search_input.value
        recipes_list.controls.clear()
        if ingredient:
            results = RecipeManager.search_by_ingredient(ingredient)
            for recipe in results:
                ingredients = json.loads(recipe[3])
                recipe_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(recipe[1], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"المكونات: {', '.join(ingredients[:3])}" if app.is_rtl else f"Ingredients: {', '.join(ingredients[:3])}", size=11),
                        ]),
                        padding=15,
                    ),
                )
                recipes_list.controls.append(recipe_card)
        app.page.update()

    recipe_name_input = app.make_text_field("اسم الوصفة" if app.is_rtl else "Recipe Name", width=300)
    recipe_ingredients_input = app.make_text_field(
        "المكونات (سطر لكل مكون)" if app.is_rtl else "Ingredients (one per line)",
        width=300,
        multiline=True,
    )
    recipe_steps_input = app.make_text_field(
        "الخطوات (سطر لكل خطوة)" if app.is_rtl else "Steps (one per line)",
        width=300,
        multiline=True,
    )

    add_recipe_button = ft.ElevatedButton(
        "إضافة وصفة" if app.is_rtl else "Add Recipe",
        on_click=add_recipe,
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#2563eb" if app.is_dark_mode else "#1d4ed8",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    search_input = app.make_text_field(
        "بحث عن مكون" if app.is_rtl else "Search by ingredient",
        width=300,
    )
    search_input.on_change = search_recipes

    recipes_list = ft.ListView(expand=True, spacing=10)
    result_text = ft.Text("", size=12, color="#3b82f6")

    refresh_recipes()

    return ft.Column([
        ft.Text("مخزن الوصفات" if app.is_rtl else "Recipe Store", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([recipe_name_input, add_recipe_button], wrap=True),
        ft.Row([recipe_ingredients_input, recipe_steps_input], wrap=True),
        search_input,
        result_text,
        ft.Divider(),
        recipes_list,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
