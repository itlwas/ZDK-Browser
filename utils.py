import json
import os
from PyQt6.QtWidgets import QTableWidget, QHeaderView

TABLE_STYLE = """
QTableWidget { background-color: #101010; color: #fff; border: none; font-size: 13px; font-family: Manrope; }
QHeaderView::section { background-color: #202020; color: #fff; padding: 6px; border: none; border-bottom: 1px solid #373737; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background-color: #373737; }
"""

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def create_table(headers):
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setStyleSheet(TABLE_STYLE)
    return table

def load_data():
    """
    Загружает данные из JSON-файла. Если файл отсутствует или произошла ошибка,
    возвращает словарь с пустой историей и настройками по умолчанию.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
    # Значения по умолчанию
    return {
        "history": [],
        "settings": {
            "homepage": "http://www.google.com",
            "language": "ru",
            "theme": "dark"
        }
    }

def save_data(data):
    """
    Сохраняет данные в JSON-файл.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")
