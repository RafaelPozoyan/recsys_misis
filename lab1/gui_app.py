"""
GUI приложение для суммаризации текста с использованием PyQt6.

Предоставляет удобный интерфейс для суммаризации текстов с поддержкой
настройки параметров суммаризации и сохранения результатов.
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QSpinBox,
    QGroupBox,
    QMessageBox,
    QScrollArea,
    QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QColor

from text_summarizer import summarize_text, summarize_text_advanced, load_api_token


class TextSummarizerApp(QMainWindow):
    """
    Что я делаю?
        Создаю главное окно приложения для суммаризации текста с графическим интерфейсом.
    Что я принимаю на вход?
        Ничего - это класс PyQt6 виджета.
    Что я возвращаю?
        Ничего - класс создает интерфейс при инициализации.
    """
    
    def __init__(self) -> None:
        """
        Что я делаю?
            Инициализирую главное окно и все компоненты интерфейса.
        Что я принимаю на вход?
            Ничего.
        Что я возвращаю?
            Ничего - конструктор класса.
        """
        super().__init__()
        self.setWindowTitle("🤖 Суммаризатор текста - Hugging Face API")
        self.setGeometry(100, 100, 1200, 800)
        
        # Проверяем наличие API токена
        try:
            load_api_token()
            api_status: str = "✅ API токен загружен"
        except ValueError as err:
            api_status: str = str(err)
        
        # Главный виджет
        central_widget: QWidget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный макет
        main_layout: QVBoxLayout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        title_label: QLabel = QLabel("📝 Суммаризация текста с использованием AI")
        title_font: QFont = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Статус API
        status_label: QLabel = QLabel(api_status)
        status_label.setStyleSheet(
            "color: green; font-weight: bold;" if "✅" in api_status 
            else "color: red; font-weight: bold;"
        )
        main_layout.addWidget(status_label)
        
        # Горизонтальный макет для основного контента
        content_layout: QHBoxLayout = QHBoxLayout()
        
        # Левая часть - Исходный текст
        left_layout: QVBoxLayout = QVBoxLayout()
        input_label: QLabel = QLabel("📌 Исходный текст:")
        left_layout.addWidget(input_label)
        
        self.input_text: QTextEdit = QTextEdit()
        self.input_text.setPlaceholderText(
            "Вставьте здесь текст для суммаризации (минимум 50 символов)..."
        )
        self.input_text.setMinimumHeight(300)
        left_layout.addWidget(self.input_text)
        
        content_layout.addLayout(left_layout, 1)
        
        # Правая часть - Результат
        right_layout: QVBoxLayout = QVBoxLayout()
        output_label: QLabel = QLabel("✨ Суммаризированный текст:")
        right_layout.addWidget(output_label)
        
        self.output_text: QTextEdit = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText(
            "Результат суммаризации будет отображен здесь..."
        )
        self.output_text.setMinimumHeight(300)
        right_layout.addWidget(self.output_text)
        
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # Параметры суммаризации
        params_group: QGroupBox = QGroupBox("⚙️ Параметры суммаризации")
        params_layout: QHBoxLayout = QHBoxLayout()
        
        # Максимальная длина
        max_len_label: QLabel = QLabel("Макс. длина (токены):")
        params_layout.addWidget(max_len_label)
        
        self.max_length_spinbox: QSpinBox = QSpinBox()
        self.max_length_spinbox.setMinimum(30)
        self.max_length_spinbox.setMaximum(500)
        self.max_length_spinbox.setValue(150)
        params_layout.addWidget(self.max_length_spinbox)
        
        # Минимальная длина
        min_len_label: QLabel = QLabel("Мин. длина (токены):")
        params_layout.addWidget(min_len_label)
        
        self.min_length_spinbox: QSpinBox = QSpinBox()
        self.min_length_spinbox.setMinimum(10)
        self.min_length_spinbox.setMaximum(200)
        self.min_length_spinbox.setValue(50)
        params_layout.addWidget(self.min_length_spinbox)
        
        params_layout.addStretch()
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # Кнопки управления
        button_layout: QHBoxLayout = QHBoxLayout()
        
        self.summarize_button: QPushButton = QPushButton("🚀 Суммаризировать")
        self.summarize_button.setMinimumHeight(40)
        self.summarize_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        self.summarize_button.clicked.connect(self.on_summarize_clicked)
        button_layout.addWidget(self.summarize_button)
        
        self.clear_button: QPushButton = QPushButton("🧹 Очистить")
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            """
        )
        self.clear_button.clicked.connect(self.on_clear_clicked)
        button_layout.addWidget(self.clear_button)
        
        self.copy_button: QPushButton = QPushButton("📋 Копировать результат")
        self.copy_button.setMinimumHeight(40)
        self.copy_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            """
        )
        self.copy_button.clicked.connect(self.on_copy_clicked)
        button_layout.addWidget(self.copy_button)
        
        self.exit_button: QPushButton = QPushButton("❌ Выход")
        self.exit_button.setMinimumHeight(40)
        self.exit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #757575;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            """
        )
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(button_layout)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")
    
    @pyqtSlot()
    def on_summarize_clicked(self) -> None:
        """
        Что я делаю?
            Обрабатываю нажатие кнопки суммаризации и вызываю функцию суммаризации.
        Что я принимаю на вход?
            Ничего.
        Что я возвращаю?
            Ничего.
        """
        input_text: str = self.input_text.toPlainText()
        
        if not input_text.strip():
            QMessageBox.warning(
                self,
                "⚠️ Ошибка",
                "Пожалуйста, введите текст для суммаризации!"
            )
            return
        
        self.statusBar().showMessage("⏳ Суммаризация в процессе...")
        QApplication.processEvents()
        
        max_len: int = self.max_length_spinbox.value()
        min_len: int = self.min_length_spinbox.value()
        
        if min_len > max_len:
            QMessageBox.warning(
                self,
                "⚠️ Ошибка параметров",
                "Минимальная длина не может быть больше максимальной!"
            )
            self.statusBar().showMessage("Готов к работе")
            return
        
        summary: Optional[str] = summarize_text_advanced(
            input_text,
            max_length=max_len,
            min_length=min_len,
            num_beams=4
        )
        
        if summary:
            self.output_text.setPlainText(summary)
            self.statusBar().showMessage("✅ Суммаризация завершена успешно!")
        else:
            QMessageBox.critical(
                self,
                "❌ Ошибка",
                "Не удалось выполнить суммаризацию. Попробуйте позже."
            )
            self.statusBar().showMessage("Готов к работе")
    
    @pyqtSlot()
    def on_clear_clicked(self) -> None:
        """
        Что я делаю?
            Очищаю оба текстовых поля (исходный и результат).
        Что я принимаю на вход?
            Ничего.
        Что я возвращаю?
            Ничего.
        """
        self.input_text.clear()
        self.output_text.clear()
        self.statusBar().showMessage("Готов к работе")
    
    @pyqtSlot()
    def on_copy_clicked(self) -> None:
        """
        Что я делаю?
            Копирую результат суммаризации в буфер обмена.
        Что я принимаю на вход?
            Ничего.
        Что я возвращаю?
            Ничего.
        """
        output_text: str = self.output_text.toPlainText()
        
        if not output_text.strip():
            QMessageBox.warning(
                self,
                "⚠️ Нечего копировать",
                "Сначала выполните суммаризацию текста!"
            )
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(output_text)
        self.statusBar().showMessage("📋 Результат скопирован в буфер обмена!")


def main() -> None:
    """
    Что я делаю?
        Запускаю приложение PyQt6.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Ничего.
    """
    app: QApplication = QApplication(sys.argv)
    window: TextSummarizerApp = TextSummarizerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
