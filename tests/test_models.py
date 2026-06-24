import unittest
from datetime import datetime
from models import Expense, FoodExpense, TransportExpense, EntertainmentExpense


class TestModels(unittest.TestCase):
    
    def test_expense_creation_positive(self):
        """Позитивный тест: создание расхода"""
        expense = Expense(100, "Тест", "2026-06-24")
        self.assertEqual(expense.amount, 100)
        self.assertEqual(expense.category, "Тест")
        self.assertEqual(expense.date, "2026-06-24")
    
    def test_expense_creation_negative_amount(self):
        """Негативный тест: создание с отрицательной суммой"""
        with self.assertRaises(ValueError):
            Expense(-100, "Тест", "2026-06-24")
    
    def test_expense_creation_invalid_date(self):
        """Негативный тест: создание с неверным форматом даты"""
        with self.assertRaises(ValueError):
            Expense(100, "Тест", "24-06-2026")
    
    def test_expense_to_dict(self):
        """Тест преобразования в словарь"""
        expense = Expense(100, "Тест", "2026-06-24")
        data = expense.to_dict()
        self.assertEqual(data["amount"], 100)
        self.assertEqual(data["category"], "Тест")
        self.assertEqual(data["date"], "2026-06-24")
    
    def test_food_expense(self):
        """Тест создания расхода на еду"""
        expense = FoodExpense(100, "2026-06-24", "Супермаркет")
        self.assertEqual(expense.category, "Еда")
        self.assertEqual(expense.place, "Супермаркет")
    
    def test_transport_expense(self):
        """Тест создания расхода на транспорт"""
        expense = TransportExpense(200, "2026-06-24", "Автобус")
        self.assertEqual(expense.category, "Транспорт")
        self.assertEqual(expense.transport_type, "Автобус")
    
    def test_entertainment_expense(self):
        """Тест создания расхода на развлечения"""
        expense = EntertainmentExpense(300, "2026-06-24", "Кино")
        self.assertEqual(expense.category, "Развлечения")
        self.assertEqual(expense.description, "Кино")
    
    def test_date_property(self):
        """Тест свойства date_obj"""
        expense = Expense(100, "Тест", "2026-06-24")
        self.assertIsInstance(expense.date_obj, datetime)


if __name__ == "__main__":
    unittest.main()