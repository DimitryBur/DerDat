from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox

class CleanView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        self.info = QLabel("Выберите столбец для обработки")
        self.cols = QComboBox()
        
        btn_smart_num = QPushButton("🔢 Извлечь числа (RegEx)")
        btn_smart_num.clicked.connect(self.run_extract)
        
        btn_dropna = QPushButton("🗑 Удалить пустые строки")
        btn_dropna.clicked.connect(self.run_clean)

        layout.addWidget(self.info)
        layout.addWidget(self.cols)
        layout.addWidget(btn_smart_num)
        layout.addWidget(btn_dropna)

        nav = QHBoxLayout()
        btn_back = QPushButton("⬅ В магазин")
        btn_back.clicked.connect(lambda: controller.switch_page(1))
        btn_next = QPushButton("💾 К сохранению ➡")
        btn_next.clicked.connect(lambda: controller.switch_page(3))
        nav.addWidget(btn_back)
        nav.addWidget(btn_next)
        layout.addLayout(nav)

    def refresh(self):
        df = self.controller.model.get_active_df()
        if df is not None:
            self.info.setText(f"Лаборатория: {self.controller.model.active_file_name}")
            self.cols.clear()
            self.cols.addItems(df.columns)

    def run_extract(self):
        col = self.cols.currentText()
        if self.controller.model.extract_numbers(col):
            self.info.setText(f"✅ Числа извлечены из '{col}'")

    def run_clean(self):
        removed = self.controller.model.clean_dropna()
        self.info.setText(f"✅ Удалено пустых строк: {removed}")
