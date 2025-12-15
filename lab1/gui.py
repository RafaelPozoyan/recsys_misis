import requests
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QTabWidget,
    QApplication,
)
from summarization_client import get_article_summary, get_text_summary


class SummarizerApp(QMainWindow):
    # Константы
    WINDOW_TITLE = "Суммаризатор | Позоян Р.О. | БПМ-22-ПО-3"
    WINDOW_SIZE = (1000, 600)
    DEFAULT_SUMMARY_LENGTH = 1

    def __init__(self) -> None:
        """Конструктор"""
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """Инициализация и настройка интерфейса"""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(*self.WINDOW_SIZE)

        # Основной контейнер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Вкладки
        self.tabs_widget = QTabWidget()
        main_layout.addWidget(self.tabs_widget)

        # Инициализация страниц
        self.url_tab = QWidget()
        self.text_tab = QWidget()

        self.tabs_widget.addTab(self.url_tab, "По ссылке")
        self.tabs_widget.addTab(self.text_tab, "По тексту")

        self.setup_url_tab()
        self.setup_text_tab()

        main_layout.addWidget(QLabel("Результат:"))
        self.summary_output = QTextEdit()
        main_layout.addWidget(self.summary_output)

    def setup_url_tab(self) -> None:
        """Настройка вкладки суммаризации по ссылке"""
        layout = QVBoxLayout(self.url_tab)

        self.url_input = QLineEdit()
        self.btn_process_url = QPushButton("Обработать данные по ссылке")
        self.btn_process_url.setMinimumHeight(40)
        self.btn_process_url.clicked.connect(self.on_url_click)

        layout.addWidget(QLabel("Вставьте URL статьи:"))
        layout.addWidget(self.url_input)
        layout.addWidget(self.btn_process_url)
        layout.addStretch()

    def setup_text_tab(self) -> None:
        """Настройка вкладки суммаризации по тексту"""
        layout = QVBoxLayout(self.text_tab)

        self.text_input = QTextEdit()
        self.btn_process_text = QPushButton("Обработать текст")
        self.btn_process_text.setMinimumHeight(40)
        self.btn_process_text.clicked.connect(self.on_text_click)

        layout.addWidget(QLabel("Вставьте текст статьи:"))
        layout.addWidget(self.text_input)
        layout.addWidget(self.btn_process_text)

    def on_url_click(self) -> None:
        """Обработка нажатия по кнопке обработки по ссылке"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите ссылку")
            return

        QApplication.processEvents()
        try:
            result = get_article_summary(url, self.DEFAULT_SUMMARY_LENGTH)
            self.summary_output.setText(result)
        except Exception as e:
            self.handle_error(e)

    def on_text_click(self) -> None:
        """Обработка нажатия по кнопке обработки по тексту"""
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст")
            return

        QApplication.processEvents()
        try:
            result = get_text_summary(text, self.DEFAULT_SUMMARY_LENGTH)
            self.summary_output.setText(result)
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, error: Exception) -> None:
        """Обработка ошибок"""
        self.summary_output.clear()
        if isinstance(error, requests.exceptions.HTTPError):
            msg = f"Ошибка API: {error}"
        elif isinstance(error, ValueError):
            msg = f"Ошибка конфигурации: {error}"
        else:
            msg = f"Произошла ошибка: {error}"

        QMessageBox.critical(self, "Ошибка", msg)
