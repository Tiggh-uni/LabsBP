# main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from scraper import NewsScraper, NetworkError, ParsingError, InvalidURLError


class NewsScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Новостной скрейпер")
        self.root.geometry("900x600")
        
        # Хранилище данных
        self.current_headlines = []
        
        # Создание интерфейса
        self.setup_ui()
        
    def setup_ui(self):
        # Верхняя панель с URL
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="URL новостного сайта:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.url_entry = ttk.Entry(top_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.url_entry.insert(0, "https://www.bbc.com/news")
        
        # Панель с кнопками
        button_frame = ttk.Frame(self.root, padding="5")
        button_frame.pack(fill=tk.X)
        
        self.scrape_btn = ttk.Button(
            button_frame, 
            text="Получить заголовки", 
            command=self.start_scraping
        )
        self.scrape_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(
            button_frame, 
            text="Сохранить в файл", 
            command=self.save_to_file,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Очистить", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Таблица для результатов
        table_frame = ttk.Frame(self.root, padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаём Treeview с прокруткой
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("#", "Заголовок", "Ссылка"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # Настройка колонок
        self.tree.heading("#", text="#")
        self.tree.heading("Заголовок", text="Заголовок")
        self.tree.heading("Ссылка", text="Ссылка")
        
        self.tree.column("#", width=50, anchor=tk.CENTER)
        self.tree.column("Заголовок", width=500)
        self.tree.column("Ссылка", width=300)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def start_scraping(self):
        """Запускает скрейпинг в отдельном потоке."""
        url = self.url_entry.get().strip()
        if not url:
            self.status_var.set("❌ Введите URL")
            return
        
        # Блокируем кнопки на время загрузки
        self.scrape_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_headlines = []
        self.status_var.set("Загрузка заголовков...")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self._scrape_worker, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _scrape_worker(self, url):
        """Рабочий поток для скрейпинга."""
        scraper = NewsScraper(url)
        try:
            headlines = scraper.fetch_headlines(limit=30)
            self.current_headlines = headlines
            
            # Обновляем таблицу в основном потоке
            self.root.after(0, self._update_table, headlines)
            
        except (NetworkError, ParsingError, InvalidURLError) as e:
            self.root.after(0, self._show_error, str(e))
        except Exception as e:
            self.root.after(0, self._show_error, f"Неожиданная ошибка: {e}")
    
    def _update_table(self, headlines):
        """Заполняет таблицу результатами."""
        for idx, item in enumerate(headlines, 1):
            # Обрезаем длинные ссылки для отображения
            link = item['link']
            if len(link) > 60:
                link = link[:57] + "..."
            
            self.tree.insert("", tk.END, values=(idx, item['title'], link))
        
        self.status_var.set(f"✅ Загружено {len(headlines)} заголовков")
        self.scrape_btn.config(state=tk.NORMAL)
        if headlines:
            self.save_btn.config(state=tk.NORMAL)
    
    def _show_error(self, error_msg):
        """Отображает ошибку."""
        self.status_var.set(f"⚠️ Ошибка: {error_msg[:80]}")
        self.scrape_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        messagebox.showerror("Ошибка скрейпинга", error_msg)
    
    def save_to_file(self):
        """Сохраняет заголовки в файл."""
        if not self.current_headlines:
            self.status_var.set("Нет данных для сохранения")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                title="Сохранить новости",
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
                initialfile="news_headlines.txt"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for idx, item in enumerate(self.current_headlines, 1):
                        f.write(f"{idx}. {item['title']}\n")
                        f.write(f"   {item['link']}\n\n")
                
                self.status_var.set(f"💾 Сохранено в {os.path.basename(file_path)}")
                messagebox.showinfo("Успех", f"Файл сохранён:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))
    
    def clear_results(self):
        """Очищает таблицу и данные."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_headlines = []
        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set("Данные очищены")


def main():
    root = tk.Tk()
    app = NewsScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()