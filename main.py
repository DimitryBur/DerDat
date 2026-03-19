import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar, QComboBox, QLabel
from models.data_manager import DataManager
from views.home import HomeView
from views.store import StoreView
from views.clean import CleanView
from views.export import ExportView

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = DataManager()
        self.setWindowTitle("derDate Pro: Smart Data Cleaner")
        self.resize(1100, 800)

        # Глобальный AppBar
        self.toolbar = self.addToolBar("Files")
        self.toolbar.addWidget(QLabel(" 📂 Текущий объект: "))
        self.file_combo = QComboBox()
        self.file_combo.setMinimumWidth(300)
        self.file_combo.currentIndexChanged.connect(self.sync_file)
        self.toolbar.addWidget(self.file_combo)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.stack.addWidget(HomeView(self))   # 0
        self.stack.addWidget(StoreView(self))  # 1
        self.stack.addWidget(CleanView(self))  # 2
        self.stack.addWidget(ExportView(self)) # 3

    def sync_file(self):
        name = self.file_combo.currentText()
        if name:
            self.model.active_file_name = name
            current = self.stack.currentWidget()
            if hasattr(current, "refresh"): current.refresh()

    def update_appbar(self):
        self.file_combo.blockSignals(True)
        self.file_combo.clear()
        self.file_combo.addItems(self.model.all_files.keys())
        self.file_combo.setCurrentText(self.model.active_file_name)
        self.file_combo.blockSignals(False)
        self.sync_file()

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainController()
    window.show()
    sys.exit(app.exec())
