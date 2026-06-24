"""
Expense Chart - GUI приложение для управления расходами
"""

import sys
import tkinter as tk

# Проверка установки matplotlib
try:
    import matplotlib
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False
    print("⚠️ Matplotlib не установлен. Для построения графиков выполните:")
    print("   pip install matplotlib")
    print()

from gui_app import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)