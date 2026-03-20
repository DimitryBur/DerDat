from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class ModelingView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>🚀 SQL Modeling (DuckDB)</b>"))
        
        # Редактор запросов
        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText('-- Пример:\nSELECT * FROM "file.csv" WHERE "Цена" > 500\n-- Имена таблиц = имена файлов в кавычках!')
        self.sql_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.sql_input)

        # Кнопки управления
        btn_lay = QHBoxLayout()
        btn_run = QPushButton("⚡ Выполнить SQL")
        btn_run.setMinimumHeight(40)
        btn_run.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_run.clicked.connect(self.run_query)
        
        btn_clear = QPushButton("🧹 Очистить")
        btn_clear.clicked.connect(lambda: self.sql_input.clear())
        
        btn_lay.addWidget(btn_run, 3)
        btn_lay.addWidget(btn_clear, 1)
        layout.addLayout(btn_lay)

        # Таблица результата
        layout.addWidget(QLabel("📊 Результат (первые 100 строк):"))
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Навигация назад
        nav = QHBoxLayout()
        btn_back = QPushButton("⬅ Назад в Лабораторию")
        btn_back.clicked.connect(lambda: controller.switch_page(2))
        nav.addWidget(btn_back)
        layout.addLayout(nav)

    def refresh(self):
        """Вызывается при переходе на страницу"""
        pass # Можно добавить логику подсказок имен таблиц

    def run_query(self):
        query = self.sql_input.toPlainText().strip()
        if not query: return

        # Вызываем метод из нашей обновленной Model
        new_name, error = self.controller.model.execute_sql(query)

        if error:
            QMessageBox.critical(self, "Ошибка SQL", f"Кривой запрос:\n{error}")
        else:
            self.controller.update_appbar()
            self.refresh_table()
            QMessageBox.information(self, "Успех", f"Запрос выполнен! Создан актив: {new_name}")

    def refresh_table(self):
        df = self.controller.model.get_active_df()
        if df is not None:
            self.table.clear()
            self.table.setColumnCount(len(df.columns))
            self.table.setRowCount(min(100, len(df)))
            self.table.setHorizontalHeaderLabels(df.columns)
            for i in range(self.table.rowCount()):
                for j in range(self.table.columnCount()):
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
