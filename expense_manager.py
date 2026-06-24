import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from models import Expense, FoodExpense, TransportExpense, EntertainmentExpense


class ExpenseManager:
    """Класс для управления расходами с сохранением в JSON"""
    
    def __init__(self, data_file: str = "data/expenses.json"):
        self.data_file = data_file
        self.expenses: List[Expense] = []
        self._backup_file = data_file + ".backup"
        self.load_data()
    
    def add_expense(self, amount: float, category: str, date: str, **kwargs) -> bool:
        try:
            expense_class = self._get_expense_class(category)
            expense = expense_class(amount, date, **kwargs)
            self.expenses.append(expense)
            self.save_data()
            return True
        except (ValueError, KeyError) as e:
            raise e
    
    def _get_expense_class(self, category: str):
        categories = {
            "Еда": FoodExpense,
            "Транспорт": TransportExpense,
            "Развлечения": EntertainmentExpense
        }
        return categories.get(category, Expense)
    
    def get_all_expenses(self) -> List[Expense]:
        return self.expenses
    
    def get_expenses_by_category(self, category: str) -> List[Expense]:
        return [e for e in self.expenses if e.category.lower() == category.lower()]
    
    def get_expenses_by_period(self, start_date: str, end_date: str) -> List[Expense]:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return [e for e in self.expenses if start <= e.date_obj <= end]
    
    def get_total_by_period(self, start_date: str, end_date: str) -> float:
        filtered = self.get_expenses_by_period(start_date, end_date)
        return sum(e.amount for e in filtered)
    
    def get_category_totals(self) -> dict:
        totals = {}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0) + expense.amount
        return totals
    
    def delete_expense(self, index: int) -> bool:
        if 0 <= index < len(self.expenses):
            deleted = self.expenses.pop(index)
            self.save_data()
            return True
        return False
    
    def save_data(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = [e.to_dict() for e in self.expenses]
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            
            with open(self._backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False
    
    def load_data(self) -> bool:
        if not os.path.exists(self.data_file):
            return True
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.expenses = []
            for item in data:
                try:
                    expense = self._create_expense_from_dict(item)
                    if expense:
                        self.expenses.append(expense)
                except Exception as e:
                    print(f"Ошибка загрузки записи: {e}")
            
            return True
        except json.JSONDecodeError:
            return self._restore_from_backup()
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
            return False
    
    def _create_expense_from_dict(self, data: Dict[str, Any]) -> Optional[Expense]:
        expense_type = data.get('type', '')
        amount = data.get('amount', 0)
        category = data.get('category', 'Другое')
        date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        if expense_type == 'food' or category == 'Еда':
            place = data.get('place', '')
            return FoodExpense(amount, date, place)
        elif expense_type == 'transport' or category == 'Транспорт':
            transport_type = data.get('transport_type', '')
            return TransportExpense(amount, date, transport_type)
        elif expense_type == 'entertainment' or category == 'Развлечения':
            description = data.get('description', '')
            return EntertainmentExpense(amount, date, description)
        else:
            return Expense(amount, category, date)
    
    def _restore_from_backup(self) -> bool:
        if not os.path.exists(self._backup_file):
            return True
        
        try:
            with open(self._backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.expenses = []
            for item in data:
                expense = self._create_expense_from_dict(item)
                if expense:
                    self.expenses.append(expense)
            
            return True
        except Exception as e:
            print(f"Ошибка восстановления: {e}")
            return False
    
    def export_to_json(self, filename: str) -> bool:
        try:
            data = [e.to_dict() for e in self.expenses]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False
    
    def import_from_json(self, filename: str) -> int:
        if not os.path.exists(filename):
            return 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for item in data:
                try:
                    expense = self._create_expense_from_dict(item)
                    if expense:
                        self.expenses.append(expense)
                        imported_count += 1
                except Exception:
                    pass
            
            self.save_data()
            return imported_count
        except Exception as e:
            print(f"Ошибка импорта: {e}")
            return 0
    
    def clear_data(self) -> bool:
        self.expenses.clear()
        return self.save_data()