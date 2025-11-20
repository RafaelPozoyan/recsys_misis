from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QGridLayout,
    QMessageBox,
)

from summarization_client import RapidApiArticleSummarizerClient


class ArticleSummarizerWindow(QWidget):
    """
    1) Что я делаю?
       Описываю главное окно приложения: ввод URL статьи,
       выбор языка суммаризации, вызов API и показ результата.

    2) Что я принимаю на вход?
       - В конструктор передаётся клиент RapidApiArticleSummarizerClient.

    3) Что я возвращаю?
       - Класс ничего не возвращает, управляет GUI.
    """

    def __init__(self, summarizer_client: RapidApiArticleSummarizerClient) -> None:
        super().__init__()

        self._summarizer_client: RapidApiArticleSummarizerClient = summarizer_client

        self._url_input: Optional[QLineEdit] = None
        self._language_selector: Optional[QComboBox] = None
        self._summary_output: Optional[TTextEdit] = None  # type: ignore[name-defined]
        self._summarize_button: Optional[QPushButton] = None

        self._initialize_ui()

    def _initialize_ui(self) -> None:
        """
        1) Что я делаю?
           Создаю и настраиваю все элементы интерфейса (поля, кнопки, подписи, layout).

        2) Что я принимаю на вход?
           - Ничего не принимаю.

        3) Что я возвращаю?
           - Ничего не возвращаю.
        """
        self.setWindowTitle("Article Extractor and Summarizer (RapidAPI)")
        self.setMinimumSize(800, 400)

        layout: QGridLayout = QGridLayout()
        self.setLayout(layout)

        url_label: QLabel = QLabel("URL статьи:")
        url_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("Вставьте ссылку на новость или статью...")

        language_label: QLabel = QLabel("Язык суммаризации:")

        self._language_selector = QComboBox()
        # Этот API умеет переводить summary — оставим базовый набор
        self._language_selector.addItem("Английский (en)", "en")
        self._language_selector.addItem("Испанский (es)", "es")
        self._language_selector.addItem("Французский (fr)", "fr")
        self._language_selector.addItem("Немецкий (de)", "de")

        self._summarize_button = QPushButton("Извлечь и суммаризировать")
        self._summarize_button.clicked.connect(self._on_summarize_clicked)

        summary_label: QLabel = QLabel("Результат суммаризации:")
        summary_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._summary_output = QTextEdit()
        self._summary_output.setReadOnly(True)
        self._summary_output.setPlaceholderText("Здесь появится краткое содержание статьи.")

        layout.addWidget(url_label, 0, 0)
        layout.addWidget(self._url_input, 0, 1, 1, 2)

        layout.addWidget(language_label, 1, 0)
        layout.addWidget(self._language_selector, 1, 1)

        layout.addWidget(self._summarize_button, 1, 2)

        layout.addWidget(summary_label, 2, 0, 1, 3)
        layout.addWidget(self._summary_output, 3, 0, 1, 3)

    def _show_error_message(self, message: str) -> None:
        """
        1) Что я делаю?
           Показываю окно с ошибкой.

        2) Что я принимаю на вход?
           - message: текст ошибки.

        3) Что я возвращаю?
           - Ничего не возвращаю.
        """
        box: QMessageBox = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Ошибка")
        box.setText(message)
        box.exec()

    def _on_summarize_clicked(self) -> None:
        """
        1) Что я делаю?
           Обрабатываю нажатие кнопки: беру URL и язык, вызываю API, вывожу summary.

        2) Что я принимаю на вход?
           - Ничего не принимаю (использую виджеты окна).

        3) Что я возвращаю?
           - Ничего не возвращаю; обновляю интерфейс.
        """
        if (
            self._url_input is None
            or self._summary_output is None
            or self._language_selector is None
            or self._summarize_button is None
        ):
            self._show_error_message("Элементы интерфейса не инициализированы.")
            return

        article_url: str = self._url_input.text().strip()
        if not article_url:
            self._show_error_message("Пожалуйста, введите URL статьи.")
            return

        current_language_index: int = self._language_selector.currentIndex()
        summary_language: str = str(
            self._language_selector.itemData(current_language_index)
        )

        self._summarize_button.setEnabled(False)
        self._summarize_button.setText("Обработка...")

        try:
            summary: str = self._summarizer_client.summarize_article(
                article_url=article_url,
                summary_language=summary_language,
            )
            self._summary_output.setPlainText(summary)
        except Exception as error:
            self._show_error_message(f"Ошибка при обращении к API: {error}")
        finally:
            self._summarize_button.setEnabled(True)
            self._summarize_button.setText("Извлечь и суммаризировать")


def run_gui_application() -> None:
    """
    1) Что я делаю?
       Создаю приложение PyQt6, инициализирую клиент RapidAPI и открываю окно суммаризации.

    2) Что я принимаю на вход?
       - Ничего не принимаю.

    3) Что я возвращаю?
       - Ничего не возвращаю; функция блокируется до закрытия окна.
    """
    import sys

    app: QApplication = QApplication(sys.argv)

    client: RapidApiArticleSummarizerClient = RapidApiArticleSummarizerClient()
    window: ArticleSummarizerWindow = ArticleSummarizerWindow(summarizer_client=client)
    window.show()

    sys.exit(app.exec())
