from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame

class CleanView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        # 1. Заголовок и выбор основной колонки (Col A)
        self.info = QLabel("🧪 Лаборатория: выберите столбец для обработки")
        self.cols = QComboBox()
        layout.addWidget(self.info)
        layout.addWidget(self.cols)

        # 2. Блок базовой очистки
        layout.addWidget(QLabel("<b>🧹 Очистка данных:</b>"))
        btn_smart_num = QPushButton("🔢 Извлечь числа (RegEx)")
        btn_smart_num.clicked.connect(self.run_extract)
        
        btn_dropna = QPushButton("🗑 Удалить пустые строки")
        btn_dropna.clicked.connect(self.run_clean)
        
        layout.addWidget(btn_smart_num)
        layout.addWidget(btn_dropna)

        # Разделительная линия для красоты
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 3. Блок Математики (все в одну строку)
        layout.addWidget(QLabel("<b>🧮 Математические операции:</b>"))
        math_lay = QHBoxLayout()
        
        self.cols_b = QComboBox() # Второй список для колонки B
        btn_math = QPushButton("✖ Умножить Col A на Col B")
        btn_math.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_math.clicked.connect(self.run_math)
        
        math_lay.addWidget(self.cols_b)
        math_lay.addWidget(btn_math)
        layout.addLayout(math_lay)

        layout.addStretch() # Прижимает всё вверх, чтобы кнопки навигации были внизу

        # 4. Навигация
        nav = QHBoxLayout()
        btn_back = QPushButton("⬅ Склад")
        btn_back.clicked.connect(lambda: controller.switch_page(1))
        
        btn_modeling = QPushButton("🔍 SQL Моделирование")
        btn_modeling.setStyleSheet("background-color: #3498db; color: white;")
        btn_modeling.clicked.connect(lambda: controller.switch_page(4))
        
        btn_next = QPushButton("💾 Экспорт ➡")
        btn_next.clicked.connect(lambda: controller.switch_page(3))
        
        nav.addWidget(btn_back)
        nav.addWidget(btn_modeling)
        nav.addWidget(btn_next)
        layout.addLayout(nav)

    def refresh(self):
        df = self.controller.model.get_active_df()
        if df is not None:
            self.info.setText(f"Активный файл: {self.controller.model.active_file_name}")
            columns = list(df.columns)
            # Обновляем оба списка
            self.cols.clear()
            self.cols.addItems(columns)
            self.cols_b.clear()
            self.cols_b.addItems(columns)

    def run_extract(self):
        col = self.cols.currentText()
        if self.controller.model.extract_numbers(col):
            self.info.setText(f"✅ Числа извлечены из '{col}'")
            self.controller.update_appbar()

    def run_clean(self):
        removed = self.controller.model.clean_dropna()
        self.info.setText(f"✅ Удалено пустых строк: {removed}")
        self.controller.update_appbar()

    def run_math(self):
        col_a = self.cols.currentText()
        col_b = self.cols_b.currentText()
        # Вызываем метод из нашей обновленной Model
        if self.controller.model.apply_column_math(col_a, col_b, '*'):
            self.info.setText(f"✅ Создана колонка: {col_a}_*_{col_b}")
            self.controller.update_appbar()
            self.refresh() # Чтобы новая колонка появилась в списках
