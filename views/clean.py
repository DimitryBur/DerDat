from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import QTimer, Qt

class CleanView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        # --- ВЕРХНЯЯ ПАНЕЛЬ С ИНДИКАТОРОМ ---
        header_lay = QHBoxLayout()
        self.info = QLabel("🧪 Лаборатория")
        
        # Наша "Лампочка"
        self.indicator = QLabel()
        self.indicator.setFixedSize(16, 16)
        # Начальный стиль (серая/выключена)
        self.indicator.setStyleSheet("background-color: #555; border-radius: 8px;")
        
        header_lay.addWidget(self.info)
        header_lay.addStretch()
        header_lay.addWidget(self.indicator)
        layout.addLayout(header_lay)

        # Таймер для выключения лампочки
        self.blink_timer = QTimer()
        self.blink_timer.setSingleShot(True)
        self.blink_timer.timeout.connect(self.indicator_off)

        # --- Остальной UI (выбор колонок и кнопки) ---
        self.cols = QComboBox()
        layout.addWidget(self.cols)
        
        btn_smart_num = QPushButton("🔢 Извлечь числа (RegEx)")
        btn_smart_num.clicked.connect(self.run_extract)
        
        btn_dropna = QPushButton("🗑 Удалить пустые строки")
        btn_dropna.clicked.connect(self.run_clean)

        layout.addWidget(btn_smart_num)
        layout.addWidget(btn_dropna)

        # Блок Математики
        layout.addWidget(QLabel("<b>🧮 Математика:</b>"))
        math_lay = QHBoxLayout()
        self.cols_b = QComboBox()
        btn_math = QPushButton("✖ Умножить на Col A")
        btn_math.clicked.connect(self.run_math)
        math_lay.addWidget(self.cols_b)
        math_lay.addWidget(btn_math)
        layout.addLayout(math_lay)

        # Навигация
        nav = QHBoxLayout()
        btn_back = QPushButton("⬅ В магазин")
        btn_back.clicked.connect(lambda: controller.switch_page(1))
        btn_modeling = QPushButton("🔍 SQL Моделирование")
        btn_modeling.clicked.connect(lambda: controller.switch_page(4))
        btn_next = QPushButton("💾 К сохранению ➡")
        btn_next.clicked.connect(lambda: controller.switch_page(3))
        nav.addWidget(btn_back)
        nav.addWidget(btn_modeling)
        nav.addWidget(btn_next)
        layout.addLayout(nav)

    # --- ЛОГИКА ЛАМПОЧКИ ---
    def blink(self, success=True):
        color = "#2ecc71" if success else "#e74c3c" # Зеленый или Красный
        self.indicator.setStyleSheet(f"background-color: {color}; border-radius: 8px; border: 1px solid white;")
        self.blink_timer.start(800) # Потухнет через 0.8 сек

    def indicator_off(self):
        self.indicator.setStyleSheet("background-color: #555; border-radius: 8px;")

    # --- ОБНОВЛЕННЫЕ МЕТОДЫ С БЛИНКОМ ---
    def refresh(self):
        df = self.controller.model.get_active_df()
        if df is not None:
            self.info.setText(f"Активный файл: {self.controller.model.active_file_name}")
            cols = list(df.columns)
            self.cols.clear()
            self.cols.addItems(cols)
            self.cols_b.clear()
            self.cols_b.addItems(cols)

    def run_extract(self):
        col = self.cols.currentText()
        if self.controller.model.extract_numbers(col):
            self.blink(True)
        else:
            self.blink(False)

    def run_clean(self):
        removed = self.controller.model.clean_dropna()
        self.blink(True) if removed >= 0 else self.blink(False)

    def run_math(self):
        col_a = self.cols.currentText()
        col_b = self.cols_b.currentText()
        if self.controller.model.apply_column_math(col_a, col_b, '*'):
            self.blink(True)
            self.refresh()
        else:
            self.blink(False)
