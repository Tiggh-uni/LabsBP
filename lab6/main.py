import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from recipe_package.calculator import RECIPES, calculate, UNIT_WEIGHT
from recipe_package.report import save_to_xls, save_to_doc
import psycopg2

# ---------- Настройки БД ----------
DB_CONFIG = {
    "dbname": "recipes_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

def save_to_db(results):
    # ... без изменений ...
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id SERIAL PRIMARY KEY,
                recipe TEXT,
                kcal REAL,
                protein REAL,
                fat REAL,
                carbs REAL,
                price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            INSERT INTO results (recipe, kcal, protein, fat, carbs, price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            results["recipe"],
            results["kcal"],
            results["protein"],
            results["fat"],
            results["carbs"],
            results["price"]
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
        return False

# ---------- Основной класс приложения ----------
class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчёт рецептов")
        self.current_result = None

        # Выбор рецепта
        ttk.Label(root, text="Выберите блюдо:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.recipe_var = tk.StringVar()
        self.recipe_combo = ttk.Combobox(root, textvariable=self.recipe_var,
                                         values=list(RECIPES.keys()), state="readonly")
        self.recipe_combo.grid(row=0, column=1, padx=5, pady=5)

        # Кнопка расчёта (теперь вызывает редактор ингредиентов)
        ttk.Button(root, text="Рассчитать", command=self.open_ingredient_editor).grid(
            row=1, column=0, columnspan=2, pady=10)

        # Отображение результата
        self.result_text = tk.Text(root, height=12, width=55, state="disabled")
        self.result_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Кнопки экспорта
        ttk.Button(root, text="Сохранить в XLS", command=self.export_xls).grid(
            row=3, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(root, text="Сохранить в DOC", command=self.export_doc).grid(
            row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(root, text="Сохранить в БД", command=self.save_db).grid(
            row=4, column=0, columnspan=2, pady=5, sticky="ew")

    # ---------- Новый метод: редактор ингредиентов ----------
    def open_ingredient_editor(self):
        """Открывает окно для ввода количества каждого ингредиента."""
        recipe_name = self.recipe_var.get()
        if not recipe_name:
            messagebox.showwarning("Внимание", "Выберите блюдо из списка")
            return

        base_recipe = RECIPES[recipe_name]   # исходные количества из словаря
        ingredients = list(base_recipe.keys())

        # Создаём дочернее окно
        editor = tk.Toplevel(self.root)
        editor.title(f"Редактирование ингредиентов: {recipe_name}")
        editor.geometry("400x300")
        editor.resizable(False, False)

        # Заголовок
        ttk.Label(editor, text="Введите количества в граммах:", font=("Arial", 10, "bold")).pack(pady=5)

        # Фрейм для полей ввода
        frame = ttk.Frame(editor)
        frame.pack(pady=5, padx=10, fill="both", expand=True)

        # Словарь для хранения переменных Entry
        self.ingredient_vars = {}

        for ing in ingredients:
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill="x", pady=2)

            # Название ингредиента
            ttk.Label(row_frame, text=ing, width=20, anchor="w").pack(side="left", padx=5)

            # Получаем базовое количество, преобразуя штуки в граммы
            base_amount = base_recipe[ing]
            if ing in UNIT_WEIGHT and not isinstance(base_amount, (int, float)):
                base_amount = UNIT_WEIGHT[ing]
            # Если это штука, но задана числом (например, 1), всё равно в граммах будем показывать
            # UNIT_WEIGHT уже содержит вес в граммах, используем его если ing в словаре
            # (для бургера булочка = 1 -> 60 г)
            if ing in UNIT_WEIGHT:
                base_amount = UNIT_WEIGHT[ing]  # всегда показываем в граммах

            # Переменная для хранения введённого значения
            var = tk.DoubleVar(value=base_amount)
            entry = ttk.Entry(row_frame, textvariable=var, width=10)
            entry.pack(side="right", padx=5)
            ttk.Label(row_frame, text="г").pack(side="right")

            self.ingredient_vars[ing] = var

        # Кнопка "Рассчитать" внутри редактора
        ttk.Button(editor, text="Рассчитать с этими количествами",
                   command=lambda: self.calculate_with_custom(recipe_name, editor)).pack(pady=10)

    def calculate_with_custom(self, recipe_name, editor_window):
        """Собирает введённые количества и запускает расчёт."""
        custom_amounts = {}
        for ing, var in self.ingredient_vars.items():
            try:
                amount = var.get()
                if amount <= 0:
                    messagebox.showwarning("Ошибка ввода", f"Количество '{ing}' должно быть положительным числом.")
                    return
                custom_amounts[ing] = amount
            except tk.TclError:
                messagebox.showwarning("Ошибка ввода", f"Некорректное значение для '{ing}'.")
                return

        # Закрываем редактор
        editor_window.destroy()

        # Выполняем расчёт с пользовательскими количествами
        try:
            self.current_result = calculate(recipe_name, custom_amounts)
            self.display_result()
        except Exception as e:
            messagebox.showerror("Ошибка расчёта", str(e))

    # ---------- Отображение результата ----------
    def display_result(self):
        res = self.current_result
        text = f"Блюдо: {res['recipe']}\n"
        text += f"Калории: {res['kcal']} ккал\n"
        text += f"Белки: {res['protein']} г, Жиры: {res['fat']} г, Углеводы: {res['carbs']} г\n"
        text += f"Стоимость: {res['price']} руб.\n\nСостав:\n"
        for ing, (grams, kcal, price) in res["breakdown"].items():
            text += f"  {ing}: {grams} г, {kcal:.1f} ккал, {price:.2f} руб.\n"
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")

    # ---------- Экспорт и БД (без изменений) ----------
    def export_xls(self):
        if not self.current_result:
            messagebox.showwarning("Нет данных", "Сначала выполните расчёт")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx")])
        if filepath:
            try:
                save_to_xls(self.current_result, filepath)
                messagebox.showinfo("Готово", f"Отчёт сохранён в {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def export_doc(self):
        if not self.current_result:
            messagebox.showwarning("Нет данных", "Сначала выполните расчёт")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".docx",
                                                filetypes=[("Word files", "*.docx")])
        if filepath:
            try:
                save_to_doc(self.current_result, filepath)
                messagebox.showinfo("Готово", f"Отчёт сохранён в {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def save_db(self):
        if not self.current_result:
            messagebox.showwarning("Нет данных", "Сначала выполните расчёт")
            return
        if save_to_db(self.current_result):
            messagebox.showinfo("БД", "Результат сохранён в базу данных")

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()            #results["kcal"],
            #results["protein"],
            #results["fat"],
            #results["carbs"],
            #results["price"]
        #))
        #conn.commit()
        #cur.close()
        #conn.close()
        #return True
    #except Exception as e:
        #messagebox.showerror("Ошибка БД", str(e))
        #return False

# ---------- Графический интерфейс ----------
class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчёт рецептов")
        self.current_result = None

        
        ttk.Label(root, text="Выберите блюдо:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.recipe_var = tk.StringVar()
        self.recipe_combo = ttk.Combobox(root, textvariable=self.recipe_var,
                                         values=list(RECIPES.keys()), state="readonly")
        self.recipe_combo.grid(row=0, column=1, padx=5, pady=5)

        
        ttk.Button(root, text="Рассчитать", command=self.calculate).grid(row=1, column=0, columnspan=2, pady=10)

        
        self.result_text = tk.Text(root, height=12, width=55, state="disabled")
        self.result_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        
        ttk.Button(root, text="Сохранить в XLS", command=self.export_xls).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(root, text="Сохранить в DOC", command=self.export_doc).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        
        ttk.Button(root, text="Сохранить в БД", command=self.save_db).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

    def calculate(self):
        recipe = self.recipe_var.get()
        if not recipe:
            messagebox.showwarning("Внимание", "Выберите блюдо из списка")
            return
        try:
            
            self.current_result = calculate(recipe)
            self.display_result()
        except Exception as e:
            messagebox.showerror("Ошибка расчёта", str(e))

    def display_result(self):
        res = self.current_result
        text = f"Блюдо: {res['recipe']}\n"
        text += f"Калории: {res['kcal']} ккал\n"
        text += f"Белки: {res['protein']} г, Жиры: {res['fat']} г, Углеводы: {res['carbs']} г\n"
        text += f"Стоимость: {res['price']} руб.\n\nСостав:\n"
        for ing, (grams, kcal, price) in res["breakdown"].items():
            text += f"  {ing}: {grams} г, {kcal:.1f} ккал, {price:.2f} руб.\n"
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")

    def export_xls(self):
        if not self.current_result:
            messagebox.showwarning("Нет данных", "Сначала выполните расчёт")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx")])
        if filepath:
            try:
                save_to_xls(self.current_result, filepath)
                messagebox.showinfo("Готово", f"Отчёт сохранён в {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def export_doc(self):
        if not self.current_result:
            messagebox.showwarning("Нет данных", "Сначала выполните расчёт")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".docx",
                                                filetypes=[("Word files", "*.docx")])
        if filepath:
            try:
                save_to_doc(self.current_result, filepath)
                messagebox.showinfo("Готово", f"Отчёт сохранён в {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def save_db(self):
        if not self.current_result:
            messagebox.showwarning("Нет данных", "Сначала выполните расчёт")
            return
        if save_to_db(self.current_result):
            messagebox.showinfo("БД", "Результат сохранён в базу данных")

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()
