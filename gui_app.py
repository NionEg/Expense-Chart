import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from expense_manager import ExpenseManager
from chart_builder import ChartBuilder, MATPLOTLIB_AVAILABLE


class ExpenseChartApp:
    """GUI приложение Expense Chart с использованием tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Expense Chart - Управление расходами")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Менеджер данных
        self.manager = ExpenseManager()
        self.chart_builder = ChartBuilder(self.manager)
        
        # Текущий фильтр
        self.filter_category = tk.StringVar(value="Все")
        self.filter_start_date = tk.StringVar()
        self.filter_end_date = tk.StringVar()
        
        # Создание интерфейса
        self._create_menu()
        self._create_widgets()
        self._refresh_expenses()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт в JSON", command=self._export_data)
        file_menu.add_command(label="Импорт из JSON", command=self._import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Очистить все данные", command=self._clear_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._on_close)
        
        # Меню "Графики"
        chart_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Графики", menu=chart_menu)
        chart_menu.add_command(label="Круговая диаграмма", command=self._show_pie_chart)
        chart_menu.add_command(label="Столбчатая диаграмма", command=self._show_bar_chart)
        chart_menu.add_command(label="Динамика расходов", command=self._show_timeline_chart)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с фильтрами
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтры", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Категория
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=(0, 5))
        categories = ["Все"] + sorted(self._get_all_categories())
        category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category, 
                                      values=categories, state="readonly", width=15)
        category_combo.grid(row=0, column=1, padx=(0, 15))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_expenses())
        
        # Дата с
        ttk.Label(filter_frame, text="Дата с:").grid(row=0, column=2, padx=(0, 5))
        start_entry = ttk.Entry(filter_frame, textvariable=self.filter_start_date, width=12)
        start_entry.grid(row=0, column=3, padx=(0, 15))
        start_entry.bind('<KeyRelease>', lambda e: self._refresh_expenses())
        
        # Дата по
        ttk.Label(filter_frame, text="по:").grid(row=0, column=4, padx=(0, 5))
        end_entry = ttk.Entry(filter_frame, textvariable=self.filter_end_date, width=12)
        end_entry.grid(row=0, column=5, padx=(0, 15))
        end_entry.bind('<KeyRelease>', lambda e: self._refresh_expenses())
        
        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Сбросить фильтры", 
                  command=self._reset_filters).grid(row=0, column=6, padx=(0, 10))
        
        # Кнопка "Добавить"
        ttk.Button(filter_frame, text="➕ Добавить расход", 
                  command=self._add_expense_dialog).grid(row=0, column=7)
        
        # Статистика
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.stats_label = ttk.Label(stats_frame, text="Всего записей: 0 | Общая сумма: 0.00 руб.")
        self.stats_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(stats_frame, text="Обновить", 
                  command=self._refresh_expenses).pack(side=tk.RIGHT, padx=5)
        
        # Таблица с расходами
        table_frame = ttk.LabelFrame(main_frame, text="Расходы", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Создание таблицы
        columns = ("#", "Дата", "Категория", "Сумма", "Доп. информация")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("#", text="№")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма", text="Сумма (руб.)")
        self.tree.heading("Доп. информация", text="Доп. информация")
        
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")
        self.tree.column("Категория", width=120, anchor="center")
        self.tree.column("Сумма", width=100, anchor="e")
        self.tree.column("Доп. информация", width=300, anchor="w")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Правая кнопка мыши для удаления
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        # Нижняя панель с кнопками
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(bottom_frame, text="🗑 Удалить выбранный", 
                  command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        
        # Кнопки графиков
        if MATPLOTLIB_AVAILABLE:
            ttk.Button(bottom_frame, text="📊 Круговая диаграмма", 
                      command=self._show_pie_chart).pack(side=tk.LEFT, padx=5)
            ttk.Button(bottom_frame, text="📊 Столбчатая диаграмма", 
                      command=self._show_bar_chart).pack(side=tk.LEFT, padx=5)
            ttk.Button(bottom_frame, text="📈 Динамика", 
                      command=self._show_timeline_chart).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Label(bottom_frame, text="⚠️ Matplotlib не установлен. Графики недоступны.").pack(side=tk.LEFT, padx=5)
    
    def _get_all_categories(self):
        """Получение всех категорий"""
        categories = set()
        for expense in self.manager.get_all_expenses():
            categories.add(expense.category)
        return categories
    
    def _refresh_expenses(self):
        """Обновление списка расходов"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение данных
        expenses = self.manager.get_all_expenses()
        
        # Применение фильтров
        category = self.filter_category.get()
        start_date = self.filter_start_date.get().strip()
        end_date = self.filter_end_date.get().strip()
        
        if category != "Все":
            expenses = [e for e in expenses if e.category == category]
        
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                expenses = [e for e in expenses if e.date_obj >= start]
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                expenses = [e for e in expenses if e.date_obj <= end]
            except ValueError:
                pass
        
        # Сортировка по дате (новые сверху)
        expenses.sort(key=lambda x: x.date_obj, reverse=True)
        
        # Заполнение таблицы
        for i, expense in enumerate(expenses, 1):
            # Дополнительная информация
            extra_info = ""
            if hasattr(expense, 'place') and expense.place:
                extra_info = f"Место: {expense.place}"
            elif hasattr(expense, 'transport_type') and expense.transport_type:
                extra_info = f"Тип: {expense.transport_type}"
            elif hasattr(expense, 'description') and expense.description:
                extra_info = f"Описание: {expense.description}"
            
            self.tree.insert("", tk.END, values=(
                i,
                expense.date,
                expense.category,
                f"{expense.amount:.2f}",
                extra_info
            ), tags=(str(i-1),))
        
        # Обновление статистики
        total = sum(e.amount for e in expenses)
        self.stats_label.config(text=f"Всего записей: {len(expenses)} | Общая сумма: {total:.2f} руб.")
    
    def _reset_filters(self):
        """Сброс фильтров"""
        self.filter_category.set("Все")
        self.filter_start_date.set("")
        self.filter_end_date.set("")
        self._refresh_expenses()
    
    def _add_expense_dialog(self):
        """Диалог добавления расхода"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить расход")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрирование диалога
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 350) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Поля ввода
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Сумма
        ttk.Label(frame, text="Сумма:").grid(row=0, column=0, sticky="w", pady=5)
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(frame, textvariable=amount_var, width=30)
        amount_entry.grid(row=0, column=1, sticky="w", pady=5)
        amount_entry.focus()
        
        # Категория
        ttk.Label(frame, text="Категория:").grid(row=1, column=0, sticky="w", pady=5)
        categories = ["Еда", "Транспорт", "Развлечения", "Другое"]
        category_var = tk.StringVar(value="Другое")
        category_combo = ttk.Combobox(frame, textvariable=category_var, 
                                      values=categories, state="readonly", width=27)
        category_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # Дата
        ttk.Label(frame, text="Дата:").grid(row=2, column=0, sticky="w", pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(frame, textvariable=date_var, width=30)
        date_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Дополнительное поле (меняется в зависимости от категории)
        ttk.Label(frame, text="Дополнительно:").grid(row=3, column=0, sticky="w", pady=5)
        extra_var = tk.StringVar()
        extra_entry = ttk.Entry(frame, textvariable=extra_var, width=30)
        extra_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        def update_extra_label(*args):
            category = category_var.get()
            labels = {
                "Еда": "Место покупки:",
                "Транспорт": "Тип транспорта:",
                "Развлечения": "Описание:",
                "Другое": "Комментарий:"
            }
            frame.grid_slaves(row=3, column=0)[0].config(text=labels.get(category, "Комментарий:"))
        
        category_var.trace('w', update_extra_label)
        update_extra_label()
        
        def add_expense():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Ошибка", "Сумма должна быть положительной")
                    return
                
                category = category_var.get()
                date = date_var.get()
                
                # Проверка даты
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат даты. Используйте YYYY-MM-DD")
                    return
                
                # Добавление расхода
                kwargs = {}
                extra = extra_var.get().strip()
                if extra:
                    if category == "Еда":
                        kwargs["place"] = extra
                    elif category == "Транспорт":
                        kwargs["transport_type"] = extra
                    elif category == "Развлечения":
                        kwargs["description"] = extra
                    else:
                        kwargs["comment"] = extra
                
                self.manager.add_expense(amount, category, date, **kwargs)
                dialog.destroy()
                self._refresh_expenses()
                messagebox.showinfo("Успех", "Расход успешно добавлен!")
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму")
        
        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Добавить", command=add_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Обработка Enter
        dialog.bind('<Return>', lambda e: add_expense())
    
    def _delete_selected(self):
        """Удаление выбранного расхода"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        
        # Получение индекса
        item = selection[0]
        values = self.tree.item(item, 'values')
        index = int(values[0]) - 1
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
            if self.manager.delete_expense(index):
                self._refresh_expenses()
                messagebox.showinfo("Успех", "Расход удален")
    
    def _show_context_menu(self, event):
        """Контекстное меню"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Удалить", command=self._delete_selected)
        menu.post(event.x_root, event.y_root)
    
    def _show_pie_chart(self):
        """Показать круговую диаграмму"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Ошибка", "Matplotlib не установлен")
            return
        
        if not self.manager.get_all_expenses():
            messagebox.showwarning("Внимание", "Нет данных для построения графика")
            return
        
        # Создание нового окна
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Круговая диаграмма")
        chart_window.geometry("600x600")
        
        canvas = self.chart_builder.create_category_chart(chart_window)
        if canvas:
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showerror("Ошибка", "Не удалось построить график")
            chart_window.destroy()
    
    def _show_bar_chart(self):
        """Показать столбчатую диаграмму"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Ошибка", "Matplotlib не установлен")
            return
        
        if not self.manager.get_all_expenses():
            messagebox.showwarning("Внимание", "Нет данных для построения графика")
            return
        
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Столбчатая диаграмма")
        chart_window.geometry("700x600")
        
        canvas = self.chart_builder.create_category_bar_chart(chart_window)
        if canvas:
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showerror("Ошибка", "Не удалось построить график")
            chart_window.destroy()
    
    def _show_timeline_chart(self):
        """Показать график динамики"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Ошибка", "Matplotlib не установлен")
            return
        
        if not self.manager.get_all_expenses():
            messagebox.showwarning("Внимание", "Нет данных для построения графика")
            return
        
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Динамика расходов")
        chart_window.geometry("800x600")
        
        canvas = self.chart_builder.create_timeline_chart(chart_window)
        if canvas:
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showerror("Ошибка", "Не удалось построить график")
            chart_window.destroy()
    
    def _export_data(self):
        """Экспорт данных в JSON"""
        if not self.manager.get_all_expenses():
            messagebox.showwarning("Внимание", "Нет данных для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Экспорт данных"
        )
        
        if filename:
            if self.manager.export_to_json(filename):
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
            else:
                messagebox.showerror("Ошибка", "Ошибка при экспорте данных")
    
    def _import_data(self):
        """Импорт данных из JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Импорт данных"
        )
        
        if filename:
            count = self.manager.import_from_json(filename)
            if count > 0:
                self._refresh_expenses()
                messagebox.showinfo("Успех", f"Импортировано {count} записей")
            else:
                messagebox.showwarning("Внимание", "Не удалось импортировать данные")
    
    def _clear_data(self):
        """Очистка всех данных"""
        if not self.manager.get_all_expenses():
            messagebox.showwarning("Внимание", "Нет данных для очистки")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все данные?"):
            if self.manager.clear_data():
                self._refresh_expenses()
                messagebox.showinfo("Успех", "Все данные удалены")
    
    def _show_about(self):
        """О программе"""
        messagebox.showinfo(
            "О программе",
            "📊 Expense Chart\n\n"
            "Версия: 2.0 (GUI)\n"
            "Автор: Иванов Иван\n\n"
            "Приложение для управления личными расходами\n"
            "с возможностью построения графиков и диаграмм.\n\n"
            f"Matplotlib: {'✅ Установлен' if MATPLOTLIB_AVAILABLE else '❌ Не установлен'}"
        )
    
    def _on_close(self):
        """Закрытие приложения"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.quit()
            self.root.destroy()


def main():
    """Точка входа в приложение"""
    try:
        root = tk.Tk()
        app = ExpenseChartApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()