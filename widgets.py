from PyQt6.QtWidgets import QTabWidget, QTabBar, QPushButton
from PyQt6.QtGui import QIcon

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
    def close_tab(self, index):
        self.parent().tabCloseRequested.emit(index)
    def add_custom_close_button(self, index):
        btn = QPushButton()
        # Используем тему из родительского окна
        btn.setIcon(QIcon(f"{self.parent().parent().theme_icon_folder}/close_small.png"))
        btn.setStyleSheet("background: transparent; border: none;")
        btn.clicked.connect(lambda: self.close_tab(index))
        self.setTabButton(index, QTabBar.ButtonPosition.RightSide, btn)

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))
        self.tabCloseRequested.connect(self.remove_tab)
    def add_tab(self, widget, title):
        index = self.addTab(widget, title)
        self.tabBar().add_custom_close_button(index)
        return index
    def remove_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
