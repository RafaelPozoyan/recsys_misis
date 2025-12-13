import requests
from PyQt6.QtWidgets import (
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout,
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QTextEdit, 
    QMessageBox,
    QTabWidget,
    QSpinBox,
    QApplication
)
from summarization_client import get_article_summary, get_text_summary

class SummarizerApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Лабораторная: Суммаризатор")
        self.setGeometry(100, 100, 700, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной вертикальный макет
        main_layout = QVBoxLayout()

        # Вкладки
        self.tabs = QTabWidget()
        
        self.tab_url = QWidget()
        self.tab_text = QWidget()
        
        self.tabs.addTab(self.tab_url, "По ссылке (URL)")
        self.tabs.addTab(self.tab_text, "По тексту")
        
        self.setup_url_tab()
        self.setup_text_tab()
        
        main_layout.addWidget(self.tabs)

        # Результат
        self.result_label = QLabel("Результат (Summary):")
        main_layout.addWidget(self.result_label)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;") # Темная тема совместимость
        main_layout.addWidget(self.result_area)

        central_widget.setLayout(main_layout)

    def _create_length_selector(self) -> tuple[QWidget, QSpinBox]:
        """
        Создает панель с выбором количества предложений.
        """
        container = QWidget()
        layout = QHBoxLayout()
        # Убираем отступы внутри контейнера, чтобы он не занимал лишнее место
        layout.setContentsMargins(0, 5, 0, 5) 
        
        label = QLabel("Кол-во предложений:")
        spin_box = QSpinBox()
        spin_box.setRange(1, 10) 
        spin_box.setValue(3) 
        
        layout.addWidget(label)
        layout.addWidget(spin_box)
        layout.addStretch() # Прижимаем спинбокс влево
        
        container.setLayout(layout)
        return container, spin_box

    def setup_url_tab(self) -> None:
        layout = QVBoxLayout()
        
        self.url_label = QLabel("Введите URL статьи:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/article")
        
        length_widget, self.url_len_spin = self._create_length_selector()
        
        self.btn_url = QPushButton("Суммаризировать URL")
        self.btn_url.clicked.connect(self.on_url_click)
        # Сделаем кнопку немного выше (по желанию)
        self.btn_url.setMinimumHeight(40)

        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(length_widget)
        layout.addWidget(self.btn_url)
        
        # Этот стрейч заполнит пустое место ВНИЗУ вкладки, поджимая элементы вверх
        layout.addStretch() 
        
        self.tab_url.setLayout(layout)

    def setup_text_tab(self) -> None:
        layout = QVBoxLayout()
        
        self.text_label = QLabel("Вставьте текст статьи:")
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Скопируйте сюда текст...")
        
        length_widget, self.text_len_spin = self._create_length_selector()
        
        self.btn_text = QPushButton("Суммаризировать Текст")
        self.btn_text.clicked.connect(self.on_text_click)
        self.btn_text.setMinimumHeight(40)

        layout.addWidget(self.text_label)
        layout.addWidget(self.text_input)
        layout.addWidget(length_widget)
        layout.addWidget(self.btn_text)
        
        # Здесь addStretch не нужен, так как QTextEdit сам растягивается
        
        self.tab_text.setLayout(layout)

    def _lock_ui(self, is_locked: bool) -> None:
        self.btn_url.setEnabled(not is_locked)
        self.btn_text.setEnabled(not is_locked)
        
        if is_locked:
            self.result_area.setText("Загрузка... Пожалуйста, подождите.")
            self.btn_url.setText("Обработка...")
            self.btn_text.setText("Обработка...")
        else:
            self.btn_url.setText("Суммаризировать URL")
            self.btn_text.setText("Суммаризировать Текст")

    def on_url_click(self) -> None:
        url: str = self.url_input.text().strip()
        length: int = self.url_len_spin.value()

        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL!")
            return
        
        self._lock_ui(True)
        # Принудительно обновляем интерфейс перед тяжелой задачей
        QApplication.processEvents()
        
        try:
            summary = get_article_summary(url, length)
            self.result_area.setText(summary)
        except Exception as e:
            self.handle_error(e)
        finally:
            self._lock_ui(False)

    def on_text_click(self) -> None:
        text: str = self.text_input.toPlainText().strip()
        length: int = self.text_len_spin.value() 

        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст!")
            return

        self._lock_ui(True)
        QApplication.processEvents()
        
        try:
            summary = get_text_summary(text, length)
            self.result_area.setText(summary)
        except Exception as e:
            self.handle_error(e)
        finally:
            self._lock_ui(False)

    def handle_error(self, error: Exception) -> None:
        self.result_area.clear()
        if isinstance(error, requests.exceptions.HTTPError):
            QMessageBox.critical(self, "Ошибка API", f"HTTP Error: {error}")
        elif isinstance(error, ValueError):
            QMessageBox.critical(self, "Ошибка .env", str(error))
        else:
            QMessageBox.critical(self, "Ошибка", f"Произошло что-то странное: {error}")
