from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class ExportView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        self.label = QLabel("💾 Готов к сохранению")
        btn_save = QPushButton("Экспортировать активный файл")
        btn_save.clicked.connect(self.export)
        
        btn_home = QPushButton("🏠 В начало")
        btn_home.clicked.connect(lambda: controller.switch_page(0))

        layout.addWidget(self.label)
        layout.addWidget(btn_save)
        layout.addWidget(btn_home)

    def export(self):
        df = self.controller.model.get_active_df()
        if df is not None:
            path, _ = QFileDialog.getSaveFileName(self, "Save", "result.csv", "*.csv")
            if path:
                df.to_csv(path, index=False)
                self.label.setText("✅ Успешно сохранено!")
