from PyQt6.QtWidgets import QTableWidget, QHeaderView

TABLE_STYLE = """
QTableWidget { background-color: #101010; color: #fff; border: none; font-size: 13px; font-family: Manrope; }
QHeaderView::section { background-color: #202020; color: #fff; padding: 6px; border: none; border-bottom: 1px solid #373737; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background-color: #373737; }
"""

def create_table(headers):
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setStyleSheet(TABLE_STYLE)
    return table