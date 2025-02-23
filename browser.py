import os
from PyQt6.QtCore import QUrl, Qt, QDateTime
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QToolBar, QToolButton, QMenu, QPushButton, QTableWidgetItem, QLabel, QComboBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

from widgets import CustomTabWidget
from utils import create_table, load_data, save_data

# Новый класс для кастомной панели заголовка окна
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: #0e0e0e;")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        # Метка заголовка
        self.title_label = QLabel("LightWork Browser", self)
        self.title_label.setStyleSheet("color: #fff; font: bold 14px;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        # Кнопка сворачивания окна
        self.min_btn = QToolButton(self)
        self.min_btn.setIcon(QIcon(f"{self.parent_window.theme_icon_folder}/minimize.png"))
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.setStyleSheet("background: transparent;")
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.min_btn)

        # Кнопка разворачивания/восстановления окна
        self.max_btn = QToolButton(self)
        self.max_btn.setIcon(QIcon(f"{self.parent_window.theme_icon_folder}/maximize.png"))
        self.max_btn.setFixedSize(32, 32)
        self.max_btn.setStyleSheet("background: transparent;")
        self.max_btn.clicked.connect(self.parent_window.toggle_maximize)
        layout.addWidget(self.max_btn)

        # Кнопка закрытия окна
        self.close_btn = QToolButton(self)
        self.close_btn.setIcon(QIcon(f"{self.parent_window.theme_icon_folder}/close.png"))
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setStyleSheet(
            "background: transparent;"
            "QToolButton:hover {background-color: #d10808;}"
            "QToolButton:pressed {background-color: #ff3232;}"
        )
        self.close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_btn)

    def update_maximize_icon(self):
        if self.parent_window.isMaximized():
            self.max_btn.setIcon(QIcon(f"{self.parent_window.theme_icon_folder}/restore.png"))
        else:
            self.max_btn.setIcon(QIcon(f"{self.parent_window.theme_icon_folder}/maximize.png"))

    # Реализация перетаскивания окна за область заголовка
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(self.parent_window.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    # Обработка двойного клика по панели для переключения состояния окна
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_window.toggle_maximize()
            self.update_maximize_icon()
            event.accept()


class BrowserTab(QWidget):
    def __init__(self, parent_browser):
        super().__init__()
        self.parent_browser = parent_browser
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.browser = QWebEngineView()
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или строку поиска...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar = QToolBar()
        self.toolbar2 = QToolBar()
        self.add_left_buttons()
        self.add_right_buttons()
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.addWidget(self.toolbar)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.toolbar2)
        self.layout().addLayout(nav_layout)
        self.layout().addWidget(self.browser)
        self.browser.titleChanged.connect(self.update_tab_title)
        self.browser.iconChanged.connect(self.update_tab_icon)
        self.browser.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))
        self.browser.page().profile().downloadRequested.connect(self.handle_download)

    def add_left_buttons(self):
        for icon, func in [("back", self.browser.back),
                           ("forward", self.browser.forward),
                           ("reload", self.browser.reload),
                           ("add", self.open_new_tab)]:
            act = QAction(QIcon(f"{self.parent_browser.theme_icon_folder}/{icon}.png"), "", self)
            act.triggered.connect(func)
            self.toolbar.addAction(act)

    def add_right_buttons(self):
        btn = QToolButton(self)
        btn.setIcon(QIcon(f"{self.parent_browser.theme_icon_folder}/menu.png"))
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        btn.setStyleSheet(
            "QToolButton {background-color:#0e0e0e; color:#fff; border:none; border-radius:8px;}"
            "QToolButton:hover {background-color:#2c2c2c; border:1px solid #373737;}"
        )
        btn.setMenu(self.create_menu())
        self.toolbar2.addWidget(btn)

    def create_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu {background-color:#101010; color:#fff; border:none; border-radius:4px; padding:6px;}"
            "QMenu::item {padding:6px; border-radius:8px;}"
            "QMenu::item:selected {background-color:#313131;}"
        )
        for text, slot in [("Загрузки", self.parent_browser.open_downloads),
                           ("История", self.parent_browser.open_history),
                           ("Настройки", self.parent_browser.open_settings)]:
            act = QAction(text, self)
            act.triggered.connect(slot)
            menu.addAction(act)
        return menu

    def update_tab_title(self, title):
        idx = self.parent_browser.tabs.indexOf(self)
        if idx != -1:
            self.parent_browser.tabs.setTabText(idx, title[:10])

    def update_tab_icon(self, icon):
        idx = self.parent_browser.tabs.indexOf(self)
        if idx != -1:
            self.parent_browser.tabs.setTabIcon(idx, icon)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
        if '.' not in url:
            url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))
        self.update_history()

    def open_new_tab(self):
        self.parent_browser.add_tab()

    def update_history(self):
        try:
            title = self.browser.title()
            url = self.browser.url().toString()
            date = QDateTime.currentDateTime().toString()
            if title and url:
                self.parent_browser.add_history_entry(title, url, date)
                self.parent_browser.update_history_table()
        except Exception as e:
            print(f"Ошибка истории: {e}")

    def handle_download(self, download: QWebEngineDownloadRequest):
        try:
            from PyQt6.QtWidgets import QFileDialog
            dlg = QFileDialog(self)
            dlg.setWindowTitle("Сохранить файл как...")
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dlg.setDirectory(os.getcwd())
            dlg.setNameFilter("Все файлы (*.*)")
            dlg.selectFile(download.downloadFileName())
            if dlg.exec():
                path = dlg.selectedFiles()[0]
                download.setDownloadDirectory(os.path.dirname(path))
                download.setDownloadFileName(os.path.basename(path))
                download.accept()
                self.parent_browser.add_download_entry(os.path.basename(path), download.totalBytes())
                download.finished.connect(lambda: self.parent_browser.update_download_status(
                    self.parent_browser.download_table.rowCount() - 1, "Завершено"))
                print(f"Скачивание начато: {path}")
            else:
                download.cancel()
                print("Скачивание отменено")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LightWork Browser")
        self.setGeometry(300, 300, 1280, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.tabs = CustomTabWidget(self)
        self.setCentralWidget(self.tabs)
        # Загрузка сохранённых данных
        data = load_data()
        self.history_data = data.get("history", [])
        self.settings_data = data.get("settings", {"homepage": "http://www.google.com", "language": "ru", "theme": "dark"})
        # Установка темы на основе настроек
        self.apply_theme()
        self.download_table = None
        # Инициализация кастомной панели заголовка
        self.title_bar = TitleBar(self)
        self.setMenuWidget(self.title_bar)
        self.add_tab()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.title_bar.update_maximize_icon()

    def setup_download_tab(self):
        downloads_tab = QWidget()
        downloads_tab.setLayout(QVBoxLayout())
        self.download_table = create_table(["Имя файла", "Размер", "Дата", "Статус"])
        downloads_tab.layout().addWidget(self.download_table)
        self.tabs.add_tab(downloads_tab, "Загрузки")

    def setup_history_tab(self):
        history_tab = QWidget()
        history_tab.setLayout(QVBoxLayout())
        self.history_table = create_table(["Название сайта", "Ссылка", "Дата посещения"])
        history_tab.layout().addWidget(self.history_table)
        self.update_history_table()
        self.tabs.add_tab(history_tab, "История")

    def add_download_entry(self, filename, size, status="В процессе"):
        row = self.download_table.rowCount()
        self.download_table.insertRow(row)
        size_mb = f"{size/(1024*1024):.2f} MB" if size else "—"
        for col, text in enumerate([filename, size_mb, QDateTime.currentDateTime().toString(), status]):
            self.download_table.setItem(row, col, QTableWidgetItem(text))

    def update_download_status(self, row, status):
        self.download_table.setItem(row, 3, QTableWidgetItem(status))

    def update_history_table(self):
        if not hasattr(self, 'history_table'):
            return
        while self.history_table.rowCount():
            self.history_table.removeRow(0)
        for entry in self.history_data:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(entry["title"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry["url"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry["date"]))

    def add_history_entry(self, title, url, date):
        self.history_data.append({"title": title, "url": url, "date": date})
        self.save_data()

    def open_history(self):
        self.add_special_tab("История", "history")

    def open_downloads(self):
        self.add_special_tab("Загрузки", "downloads")

    def open_settings(self):
        self.add_special_tab("Настройки", "settings")

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QWidget {background-color:#0e0e0e; color:#fff; font-family:Manrope; font-size:13px; border:none; padding:0;}
        QTabWidget::pane {background-color:#0e0e0e; padding:2px 0 0 0;}
        QTabBar {background-color:#0e0e0e; padding:2px; margin:4px;}
        QTabBar::tab {background-color:#0e0e0e; color:#fff; padding:5px; border-radius:8px; margin:4px;}
        QTabBar::tab:selected {background-color:#2c2c2c; border-radius:8px;}
        QTabBar::tab:hover {background-color:#1e1e1e; border:0 solid #373737;}
        QLineEdit {background-color:#000; color:#a5a5a5; padding:5px; border-radius:8px; font-family:Manrope; font-size:13px;}
        QToolBar, QToolButton {background-color:#0e0e0e; color:#fff; border:none; margin:0 5px; border-radius:8px;}
        QToolButton:hover {background-color:#2c2c2c; border:none;}
        QToolTip {background-color:#212121; color:#fff; font-size:13px; border:none; border-radius:8px; padding:2px; font-family:Manrope;}
        """)
        self.theme_icon_folder = "assets/icons_dark_theme"

    def apply_light_theme(self):
        self.setStyleSheet("""
        QWidget {background-color:#ffffff; color:#000; font-family:Manrope; font-size:13px; border:none; padding:0;}
        QTabWidget::pane {background-color:#ffffff; padding:2px 0 0 0;}
        QTabBar {background-color:#ffffff; padding:2px; margin:4px;}
        QTabBar::tab {background-color:#ffffff; color:#000; padding:5px; border-radius:8px; margin:4px; border: 1px solid #ccc;}
        QTabBar::tab:selected {background-color:#e0e0e0; border-radius:8px;}
        QTabBar::tab:hover {background-color:#f0f0f0; border:1px solid #aaa;}
        QLineEdit {background-color:#f5f5f5; color:#000; padding:5px; border-radius:8px; font-family:Manrope; font-size:13px; border:1px solid #ccc;}
        QToolBar, QToolButton {background-color:#ffffff; color:#000; border:none; margin:0 5px; border-radius:8px;}
        QToolButton:hover {background-color:#e0e0e0; border:none;}
        QToolTip {background-color:#f0f0f0; color:#000; font-size:13px; border:none; border-radius:8px; padding:2px; font-family:Manrope;}
        """)
        self.theme_icon_folder = "assets/icons_light_theme"

    def apply_theme(self):
        if self.settings_data.get("theme", "dark") == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def add_tab(self, url=None):
        # Используем домашнюю страницу из настроек, если URL не передан
        if url is None:
            url = self.settings_data.get("homepage", "http://www.google.com")
        tab = BrowserTab(self)
        tab.browser.setUrl(QUrl(url))
        idx = self.tabs.add_tab(tab, "Новая вкладка")
        self.tabs.setCurrentIndex(idx)

    def add_special_tab(self, title, tab_type):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == title:
                self.tabs.setCurrentIndex(i)
                return
        if tab_type == "history":
            self.setup_history_tab()
        elif tab_type == "settings":
            self.setup_settings_tab()
        elif tab_type == "downloads":
            self.setup_download_tab()

    def setup_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()
        settings_tab.setLayout(layout)
        # Настройка домашней страницы
        homepage_label = QLabel("Домашняя страница:")
        homepage_edit = QLineEdit()
        homepage_edit.setText(self.settings_data.get("homepage", "http://www.google.com"))
        layout.addWidget(homepage_label)
        layout.addWidget(homepage_edit)
        # Настройка локализации
        lang_label = QLabel("Локализация:")
        lang_combo = QComboBox()
        lang_combo.addItem("Русский", "ru")
        lang_combo.addItem("English", "en")
        lang_value = self.settings_data.get("language", "ru")
        index = lang_combo.findData(lang_value)
        if index != -1:
            lang_combo.setCurrentIndex(index)
        layout.addWidget(lang_label)
        layout.addWidget(lang_combo)
        # Настройка темы
        theme_label = QLabel("Тема:")
        theme_combo = QComboBox()
        theme_combo.addItem("Темная", "dark")
        theme_combo.addItem("Светлая", "light")
        theme_value = self.settings_data.get("theme", "dark")
        index = theme_combo.findData(theme_value)
        if index != -1:
            theme_combo.setCurrentIndex(index)
        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)
        # Кнопка сохранения настроек
        save_button = QPushButton("Сохранить настройки")
        layout.addWidget(save_button)

        def save_settings():
            self.settings_data["homepage"] = homepage_edit.text().strip() or "http://www.google.com"
            self.settings_data["language"] = lang_combo.currentData()
            self.settings_data["theme"] = theme_combo.currentData()
            self.save_data()
            self.apply_theme()
        save_button.clicked.connect(save_settings)
        self.tabs.add_tab(settings_tab, "Настройки")

    def save_data(self):
        data = {
            "history": self.history_data,
            "settings": self.settings_data
        }
        save_data(data)

    def closeEvent(self, event):
        self.save_data()
        event.accept()

    def mousePressEvent(self, event):
        # Перетаскивание окна осуществляется через TitleBar, поэтому здесь оставляем базовую обработку
        event.accept()

    def mouseMoveEvent(self, event):
        event.accept()
