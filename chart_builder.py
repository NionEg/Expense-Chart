import sys
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Matplotlib не установлен. Для построения графиков выполните:")
    print("   pip install matplotlib")

from expense_manager import ExpenseManager


class ChartBuilder:
    """Класс для построения графиков расходов"""
    
    def __init__(self, manager: ExpenseManager):
        self.manager = manager
        
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️ Внимание: matplotlib не установлен. Графики недоступны.")
    
    def _check_matplotlib(self) -> bool:
        if not MATPLOTLIB_AVAILABLE:
            return False
        return True
    
    def create_category_chart(self, parent=None, title: str = "Расходы по категориям"):
        """Создание круговой диаграммы"""
        if not self._check_matplotlib():
            return None
        
        totals = self.manager.get_category_totals()
        
        if not totals:
            return None
        
        categories = list(totals.keys())
        values = list(totals.values())
        
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.set_title(title)
            ax.axis('equal')
            
            if parent:
                canvas = FigureCanvasTkAgg(fig, parent)
                canvas.draw()
                return canvas
            else:
                plt.show()
                return None
                
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None
    
    def create_category_bar_chart(self, parent=None, title: str = "Расходы по категориям"):
        """Создание столбчатой диаграммы"""
        if not self._check_matplotlib():
            return None
        
        totals = self.manager.get_category_totals()
        
        if not totals:
            return None
        
        categories = list(totals.keys())
        values = list(totals.values())
        
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(categories, values, color='skyblue', edgecolor='black')
            ax.set_title(title)
            ax.set_xlabel('Категории')
            ax.set_ylabel('Сумма (руб.)')
            
            # Добавление значений на столбцы
            for i, v in enumerate(values):
                ax.text(i, v + max(values) * 0.01, f'{v:.2f}', ha='center')
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            fig.tight_layout()
            
            if parent:
                canvas = FigureCanvasTkAgg(fig, parent)
                canvas.draw()
                return canvas
            else:
                plt.show()
                return None
                
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None
    
    def create_timeline_chart(self, parent=None, start_date: str = None, 
                             end_date: str = None, title: str = "Динамика расходов"):
        """Создание графика динамики расходов"""
        if not self._check_matplotlib():
            return None
        
        if start_date and end_date:
            expenses = self.manager.get_expenses_by_period(start_date, end_date)
        else:
            expenses = self.manager.get_all_expenses()
        
        if not expenses:
            return None
        
        try:
            # Сортировка по дате
            expenses.sort(key=lambda x: x.date_obj)
            
            dates = [e.date for e in expenses]
            amounts = [e.amount for e in expenses]
            categories = [e.category for e in expenses]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Цвета для разных категорий
            unique_categories = list(set(categories))
            colors = plt.cm.tab10(range(len(unique_categories)))
            color_map = {cat: colors[i] for i, cat in enumerate(unique_categories)}
            
            # Построение графика
            for i, expense in enumerate(expenses):
                ax.bar(i, expense.amount, color=color_map[expense.category], 
                       label=expense.category if i == 0 or expense.category != expenses[i-1].category else "")
            
            ax.set_xlabel('Дата')
            ax.set_ylabel('Сумма (руб.)')
            ax.set_title(title)
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45)
            ax.legend()
            fig.tight_layout()
            
            if parent:
                canvas = FigureCanvasTkAgg(fig, parent)
                canvas.draw()
                return canvas
            else:
                plt.show()
                return None
                
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None