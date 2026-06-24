from datetime import datetime
import json


class Expense:
    """Базовый класс расходов"""
    def __init__(self, amount: float, category: str, date: str):
        self._amount = self._validate_amount(amount)
        self._category = category
        self._date = self._validate_date(date)
    
    @property
    def amount(self):
        return self._amount
    
    @property
    def category(self):
        return self._category
    
    @property
    def date(self):
        return self._date.strftime("%Y-%m-%d")
    
    @property
    def date_obj(self):
        return self._date
    
    def _validate_amount(self, amount):
        """Проверка суммы"""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        return amount
    
    def _validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD")
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            "amount": self._amount,
            "category": self._category,
            "date": self.date
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание объекта из словаря"""
        return cls(data["amount"], data["category"], data["date"])
    
    def __str__(self):
        return f"{self.date} | {self.category}: {self.amount:.2f} руб."


class FoodExpense(Expense):
    """Расходы на еду"""
    def __init__(self, amount: float, date: str, place: str = ""):
        super().__init__(amount, "Еда", date)
        self.place = place
    
    def to_dict(self):
        data = super().to_dict()
        data["place"] = self.place
        data["type"] = "food"
        return data


class TransportExpense(Expense):
    """Расходы на транспорт"""
    def __init__(self, amount: float, date: str, transport_type: str = ""):
        super().__init__(amount, "Транспорт", date)
        self.transport_type = transport_type
    
    def to_dict(self):
        data = super().to_dict()
        data["transport_type"] = self.transport_type
        data["type"] = "transport"
        return data


class EntertainmentExpense(Expense):
    """Расходы на развлечения"""
    def __init__(self, amount: float, date: str, description: str = ""):
        super().__init__(amount, "Развлечения", date)
        self.description = description
    
    def to_dict(self):
        data = super().to_dict()
        data["description"] = self.description
        data["type"] = "entertainment"
        return data