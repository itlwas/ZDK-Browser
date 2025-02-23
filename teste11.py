import sys
import os

from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout, QToolBar, QLabel, QPushButton,
    QMenu, QToolButton, QTabBar, QStyleOption, QStyle, QSpacerItem, QSizePolicy, QFileDialog, QTableWidgetItem,
    QHeaderView, QTableWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QDateTime
from PyQt6.QtGui import QIcon, QAction


class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

    def close_tab(self, index):
        self.parent().tabCloseRequested.emit(index)

    def add_custom_close_button(self, index):
        close_button = QPushButton()
        close_button.setIcon(QIcon("assets/icons_dark_theme/close_small.png"))
        close_button.setStyleSheet("background: transparent; border: none;")
        close_button.clicked.connect(lambda: self.close_tab(index))
        self.setTabButton(index, QTabBar.ButtonPosition.RightSide, close_button)


class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))
        self.tabCloseRequested.connect(self.close_tab)

    def add_tab(self, widget, title):
        index = super().addTab(widget, title)
        self.tabBar().add_custom_close_button(index)
        return index

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)


class BrowserTab(QWidget):
    def __init__(self, parent_browser):
        super().__init__()
        self.parent_browser = parent_browser

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.browser = QWebEngineView()

        self.nav_buttons_layout = QHBoxLayout()
        self.nav_buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или строку поиска...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.toolbar = QToolBar()
        self.toolbar2 = QToolBar()
        self.add_left_tool_buttons()
        self.add_right_tool_buttons()

        self.nav_buttons_layout.addWidget(self.toolbar)
        self.nav_buttons_layout.addWidget(self.url_bar)
        self.nav_buttons_layout.addWidget(self.toolbar2)

        self.layout.addLayout(self.nav_buttons_layout)
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

        self.browser.titleChanged.connect(self.update_tab_title)
        self.browser.iconChanged.connect(self.update_tab_icon)
        self.browser.urlChanged.connect(self.update_url_bar)

        self.browser.page().profile().downloadRequested.connect(self.handle_download)

    def add_left_tool_buttons(self):
        back_btn = QAction(QIcon("assets/icons_dark_theme/back.png"), "", self)
        back_btn.triggered.connect(self.browser.back)
        self.toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon("assets/icons_dark_theme/forward.png"), "", self)
        forward_btn.triggered.connect(self.browser.forward)
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction(QIcon("assets/icons_dark_theme/reload.png"), "", self)
        reload_btn.triggered.connect(self.browser.reload)
        self.toolbar.addAction(reload_btn)

        new_tab_btn = QAction(QIcon("assets/icons_dark_theme/add.png"), "", self)
        new_tab_btn.triggered.connect(self.open_new_tab)
        self.toolbar.addAction(new_tab_btn)

    def add_right_tool_buttons(self):
        menu_button = QToolButton(self)
        menu_button.setIcon(QIcon("assets/icons_dark_theme/menu.png"))
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu_button.setStyleSheet("""
                    QToolButton {
                        background-color: #0e0e0e;
                        color: #fff;
                        border: none;
                        border-radius: 8px;
                    }
                    QToolButton:hover {
                        background-color: #2c2c2c;
                        border-radius: 8px;
                        border: 1px solid #373737;
                    }
                    QToolButton::menu-indicator {
                        width: 0px;
                    }
                """)
        menu_button.setMenu(self.create_menu())
        self.toolbar2.addWidget(menu_button)

    def populate_history_table(self):
        """Заполняет таблицу тестовыми данными."""
        test_data = [
            {"title": "Google", "url": "https://www.google.com", "date": "2025-01-21 10:00:00"},
            {"title": "YouTube", "url": "https://www.youtube.com", "date": "2025-01-21 10:30:00"},
            {"title": "Wikipedia", "url": "https://www.wikipedia.org", "date": "2025-01-21 11:00:00"}
        ]

        self.parent_browser.history_data = test_data  # Присваиваем тестовые данные
        self.parent_browser.update_history_table()  # Обновляем таблицу с историей

    def update_history_table(self):
        """Обновляет таблицу с историей на вкладке."""
        try:
            for i in range(self.parent_browser.history_table.rowCount()):
                self.parent_browser.history_table.removeRow(i)

            for entry in self.parent_browser.history_data:
                row = self.parent_browser.history_table.rowCount()
                self.parent_browser.history_table.insertRow(row)
                self.parent_browser.history_table.setItem(row, 0, QTableWidgetItem(entry["title"]))
                self.parent_browser.history_table.setItem(row, 1, QTableWidgetItem(entry["url"]))
                self.parent_browser.history_table.setItem(row, 2, QTableWidgetItem(entry["date"]))
        except Exception as e:
            print(f"Ошибка при обновлении таблицы истории: {e}")

    def update_history(self):
        """Добавляет запись в историю после загрузки страницы."""
        try:
            title = self.browser.title()
            url = self.browser.url().toString()
            date = QDateTime.currentDateTime().toString()

            if title and url:
                # Добавляем запись в историю
                self.parent_browser.add_history_entry(title, url, date)

                # Обновляем таблицу с историей
                self.parent_browser.update_history_table()
        except Exception as e:
            print(f"Ошибка при обновлении истории: {e}")

    def navigate_to_url(self):
        url = self.url_bar.text()

        if not url:
            print("URL не введен!")
            return

        if '.' not in url:
            url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        self.browser.setUrl(QUrl(url))

        # Обновляем историю и таблицу при переходе на новый сайт
        self.update_history()

    def open_new_tab(self):
        self.parent_browser.add_tab()

    def create_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #101010;
                color: #fff;
                border: 0px solid #101010;
                border-radius: 4px;
                padding: 6px 6px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 6px 6px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background-color: #313131;
                color: #fff;
            }
        """)

        downloads_action = QAction("Загрузки", self)
        downloads_action.triggered.connect(self.parent_browser.open_downloads)
        menu.addAction(downloads_action)

        history_action = QAction("История", self)
        history_action.triggered.connect(self.parent_browser.open_history)
        menu.addAction(history_action)

        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.parent_browser.open_settings)
        menu.addAction(settings_action)

        return menu

    def update_tab_title(self, title):
        current_index = self.parent_browser.tabs.indexOf(self)
        if current_index != -1:
            self.parent_browser.tabs.setTabText(current_index, title[:10])

    def update_tab_icon(self, icon):
        current_index = self.parent_browser.tabs.indexOf(self)
        if current_index != -1:
            self.parent_browser.tabs.setTabIcon(current_index, icon)

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())


    def handle_download(self, download: QWebEngineDownloadRequest):
        try:
            # Открываем диалог выбора файла
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("Сохранить файл как...")
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setDirectory(os.getcwd())  # Начальная папка
            file_dialog.setNameFilter("Все файлы (*.*)")

            default_filename = download.downloadFileName()
            file_dialog.selectFile(default_filename)

            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]

                # Устанавливаем путь для загрузки
                download.setDownloadDirectory(os.path.dirname(save_path))
                download.setDownloadFileName(os.path.basename(save_path))
                download.accept()

                # Добавляем запись в таблицу загрузок
                self.add_download_entry(
                    filename=os.path.basename(save_path),
                    size=download.totalBytes(),
                    status="В процессе"
                )

                # Слушаем обновления загрузки
                download.finished.connect(
                    lambda: self.update_download_status(
                        row=self.download_table.rowCount() - 1,
                        status="Завершено"
                    )
                )

                # Логируем начало загрузки
                print(f"Скачивание начато: {save_path}")
            else:
                download.cancel()
                print("Скачивание отменено пользователем")
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LightWork Browser")
        self.setGeometry(300, 300, 1280, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        self.tabs = CustomTabWidget()
        self.setCentralWidget(self.tabs)
        self.centralWidget().setContentsMargins(0, 0, 0, 0)

        self.add_tab()

        self.apply_dark_theme()

        # Главный компоновочный layout
        main_layout = QHBoxLayout()

        # Добавляем QWidget (слева)
        self.left_widget = QWidget(self)
        self.left_layout = QHBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        main_layout.addWidget(self.left_widget)

        # Добавляем title bar (справа)
        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar_layout.addStretch(1)

        self.download_data = []
        # Список для хранения информации о загрузках
        self.download_table = None  # Таблица загрузок

        self.history_data = [
            {"title": "Google", "url": "https://www.google.com", "date": "2025-01-01 10:00:00"},
            {"title": "YouTube", "url": "https://www.youtube.com", "date": "2025-01-01 10:00:00"},
            {"title": "Wikipedia", "url": "https://www.wikipedia.org", "date": "2025-01-01 10:00:00"}
        ]

        # Создаем кнопки для управления окном
        self.minimize_button = QPushButton(QIcon("assets/icons_dark_theme/minimize.png"), "", self)
        self.minimize_button.setStyleSheet("""
                    QPushButton {
                        background-color: #0e0e0e;
                        color: #fff;
                        border: none;
                        margin: 0px; /* Убираем отступы */
                        padding: 0px; /* Убираем внутренние отступы */
                    }
                    QPushButton:hover {
                        background-color: #2f2f2f;
                        border: none;
                    }
                    QPushButton:pressed {
                        background-color: #484848;
                    }
                """)
        self.minimize_button.setFixedSize(32, 32)  # Размер кнопки
        self.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar_layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton(QIcon("assets/icons_dark_theme/maximize.png"), "", self)
        self.maximize_button.setStyleSheet("""
                    QPushButton {
                        background-color: #0e0e0e;
                        color: #fff;
                        border: none;
                        margin: 0px; /* Убираем отступы */
                        padding: 0px; /* Убираем внутренние отступы */
                    }
                    QPushButton:hover {
                        background-color: #2f2f2f;
                        border: none;
                    }
                    QPushButton:pressed {
                        background-color: #484848;
                    }
                """)
        self.maximize_button.setFixedSize(32, 32)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.title_bar_layout.addWidget(self.maximize_button)

        self.close_button = QPushButton(QIcon("assets/icons_dark_theme/close.png"), "", self)
        self.close_button.setStyleSheet("""
                    QPushButton {
                        background-color: #0e0e0e;
                        color: #fff;
                        border: none;
                        margin: 0px; /* Убираем отступы */
                        padding: 0px; /* Убираем внутренние отступы */
                    }
                    QPushButton:hover {
                        background-color: #d10808;
                        border: none;
                    }
                    QPushButton:pressed {
                        background-color: #ff3232;
                    }
                """)
        self.close_button.setFixedSize(32, 32)
        self.close_button.clicked.connect(self.close)
        self.title_bar_layout.addWidget(self.close_button)

        self.title_bar_widget = QWidget()
        self.title_bar_widget.setLayout(self.title_bar_layout)
        main_layout.addWidget(self.title_bar_widget)

        # Основной центральный виджет, который будет содержать title bar и центральную часть
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setMenuWidget(central_widget)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def setup_download_tab(self):
        """Создает вкладку загрузок и добавляет иконку."""
        downloads_tab = QWidget()
        layout = QVBoxLayout()

        # Создаем таблицу для отображения загрузок
        self.download_table = QTableWidget()
        self.download_table.setColumnCount(4)
        self.download_table.setHorizontalHeaderLabels(["Имя файла", "Размер", "Дата", "Статус"])
        self.download_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.download_table.setStyleSheet("""
            QTableWidget {
                background-color: #101010;
                color: #fff;
                border: none;
                font-size: 13px;
                font-family: Manrope;
            }
            QHeaderView::section {
                background-color: #202020;
                color: #fff;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #373737;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #373737;
            }
        """)

        layout.addWidget(self.download_table)
        downloads_tab.setLayout(layout)

        self.tabs.add_tab(downloads_tab, "Загрузки")

    def setup_history_tab(self):
        """Создает вкладку с историей посещений."""
        history_tab = QWidget()
        layout = QVBoxLayout()

        # Создаем таблицу для отображения истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Название сайта", "Ссылка", "Дата посещения"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #101010;
                color: #fff;
                border: none;
                font-size: 13px;
                font-family: Manrope;
            }
            QHeaderView::section {
                background-color: #202020;
                color: #fff;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #373737;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #373737;
            }
        """)

        layout.addWidget(self.history_table)
        history_tab.setLayout(layout)

        # Заполнение таблицы данными истории
        self.update_history_table()

        index = self.tabs.addTab(history_tab, "История")
        self.tabs.setCurrentIndex(index)

    def add_download_entry(self, filename, size, status="В процессе"):
        """Добавляет запись в таблицу загрузок."""
        row = self.download_table.rowCount()
        self.download_table.insertRow(row)
        size_mb = f"{size / (1024 * 1024):.2f} MB" if size else "—"
        self.download_table.setItem(row, 0, QTableWidgetItem(filename))
        self.download_table.setItem(row, 1, QTableWidgetItem(size_mb))
        self.download_table.setItem(row, 2, QTableWidgetItem(QDateTime.currentDateTime().toString()))
        self.download_table.setItem(row, 3, QTableWidgetItem(status))

    def update_download_status(self, row, status):
        """Обновляет статус загрузки в таблице."""
        self.download_table.setItem(row, 3, QTableWidgetItem(status))

    def update_history_table(self):
        """Обновляет таблицу с историей на вкладке."""
        try:
            for i in range(self.history_table.rowCount()):
                self.history_table.removeRow(i)

            for entry in self.history_data:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                self.history_table.setItem(row, 0, QTableWidgetItem(entry["title"]))
                self.history_table.setItem(row, 1, QTableWidgetItem(entry["url"]))
                self.history_table.setItem(row, 2, QTableWidgetItem(entry["date"]))
        except Exception as e:
            print(f"Ошибка при обновлении таблицы истории: {e}")

    def add_history_entry(self, title, url, date):
        """Добавляет запись в историю."""
        self.history_data.append({"title": title, "url": url, "date": date})

    def add_history_entry_to_table(self, title, url, date):
        """Добавляет запись в таблицу истории без очистки существующих данных."""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(title))
        self.history_table.setItem(row, 1, QTableWidgetItem(url))
        self.history_table.setItem(row, 2, QTableWidgetItem(date))

    def open_history(self):
        """Открывает вкладку с историей посещений."""
        # Проверяем, существует ли уже вкладка "История"
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "История":
                self.tabs.setCurrentIndex(i)
                return

        # Создаем новую вкладку "История"
        history_tab = QWidget()
        layout = QVBoxLayout()

        # Создаем таблицу для отображения истории
        history_table = QTableWidget()
        history_table.setColumnCount(3)
        history_table.setHorizontalHeaderLabels(["Название сайта", "Ссылка", "Дата посещения"])
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_table.setStyleSheet("""
            QTableWidget {
                background-color: #101010;
                color: #fff;
                border: none;
                font-size: 13px;
                font-family: Manrope;
            }
            QHeaderView::section {
                background-color: #202020;
                color: #fff;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #373737;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #373737;
            }
        """)

        # Заполняем таблицу данными из истории
        for entry in self.history_data:
            row = history_table.rowCount()
            history_table.insertRow(row)
            history_table.setItem(row, 0, QTableWidgetItem(entry["title"]))
            history_table.setItem(row, 1, QTableWidgetItem(entry["url"]))
            history_table.setItem(row, 2, QTableWidgetItem(entry["date"]))

        layout.addWidget(history_table)
        history_tab.setLayout(layout)

        index = self.tabs.addTab(history_tab, "История")
        self.tabs.setCurrentIndex(index)

    def apply_dark_theme(self):
        dark_theme = """
            QWidget {
                background-color: #0e0e0e;
                color: #fff;
                font-family: Manrope;
                font-size: 13px;
                border-width: 0px;
                padding: 0px;
                border-style: none;
            }
            QTabWidget::pane {
                background-color: #0e0e0e;
                border: none;
                border-width: 0px;
                padding: 2px 0px 0px 0px;
                border-style: none;
            }
            QTabBar {
                background-color: #0e0e0e;
                border: none;
                border-width: 0px;
                padding: 2px;
                margin: 4px;
                border-style: none;
            }
            QTabBar::tab {
                background-color: #0e0e0e;
                color: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0.5 #fff, stop:1 #0e0e0e);
                font-size: 13px;
                border: none;
                padding: 5px;
                border-radius: 8px;
                border: none;
                margin: 4px;
            }
            QTabBar::tab:selected {
                color: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0.5 #fff, stop:1 #2c2c2c);
                background-color: #2c2c2c;
                border-radius: 8px;
                border: none;
            }
            QTabBar::tab:hover {
                color: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0.5 #fff, stop:1 #1e1e1e);
                background-color: #1e1e1e;
                border-radius: 8px;
                border: 0px solid #373737;
            }
            QLineEdit {
                background-color: #000000;
                color: #a5a5a5;
                font-size: 13px;
                border-radius: 8px;
                border: none;
                padding: 5px;
                font-family: Manrope;
            }
            QToolBar {
                background-color: #0e0e0e;
                border: none;
            }
            QToolButton {
                background-color: #0e0e0e;
                color: #fff;
                border: none;
                margin: 0px 5px 0px 5px;
                border-radius: 8px;
            }
            QToolButton:hover {
                background-color: #2c2c2c;
                border-radius: 8px;
                border: none;
            }
            QToolTip {
                background-color: #212121;
                color: #fff;
                font-size: 13px;
                border: none;
                border-radius: 8px;
                padding: 2px;
                font-family: Manrope;
            }
        """
        self.setStyleSheet(dark_theme)

    def add_tab(self, url="http://www.google.com"):
        new_tab = BrowserTab(self)
        new_tab.browser.setUrl(QUrl(url))
        index = self.tabs.add_tab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)

    def add_special_tab(self, title, tab_type):
        """Добавляет специальную вкладку и кнопку закрытия."""
        # Проверяем, существует ли уже вкладка с указанным названием
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

        # Найдем индекс добавленной вкладки
        new_index = self.tabs.count() - 1
        self.tabs.tabBar().add_custom_close_button(new_index)

    def open_settings(self):
        self.add_special_tab("Настройки", "settings")

    def open_downloads(self):
        self.setup_download_tab()
        self.add_special_tab("Загрузки", "downloads")

    def open_history(self):
        self.add_special_tab("История", "history")

    def add_history_entry(self, title, url, date):
        """Добавляет запись в историю."""
        self.history_data.append({"title": title, "url": url, "date": date})

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_position)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def setup_settings_tab(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec())
