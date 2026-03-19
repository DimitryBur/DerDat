from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
                             QPushButton, QFileDialog, QLineEdit, QLabel, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt

class StoreView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("📦 Список загруженных CSV:"))
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        layout.addWidget(QLabel("👀 Предпросмотр (10 строк):"))
        self.table = QTableWidget()
        layout.addWidget(self.table)

        rename_lay = QHBoxLayout()
        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("Новое имя для активного файла...")
        btn_ren = QPushButton("Переименовать")
        btn_ren.clicked.connect(self.rename)
        rename_lay.addWidget(self.name_in)
        rename_lay.addWidget(btn_ren)
        layout.addLayout(rename_lay)

        btn_add = QPushButton("📥 Добавить файл")
        btn_add.clicked.connect(self.add_file)
        btn_merge = QPushButton("🔗 Объединить отмеченные")
        btn_merge.clicked.connect(self.merge_files)
        
        layout.addWidget(btn_add)
        layout.addWidget(btn_merge)

        nav = QHBoxLayout()
        btn_next = QPushButton("🧹 Перейти к Очистке >>")
        btn_next.clicked.connect(lambda: controller.switch_page(2))
        nav.addWidget(btn_next)
        layout.addLayout(nav)

    def add_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSV", "", "*.csv")
        if path:
            name, rows = self.controller.model.add_file(path)
            item = QListWidgetItem(f"{name} ({rows} стр.)")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)
            self.controller.update_appbar()

    def on_item_clicked(self, item):
        name = item.data(Qt.ItemDataRole.UserRole)
        self.controller.model.active_file_name = name
        self.controller.update_appbar()

    def refresh(self):
        df = self.controller.model.get_active_df()
        if df is not None:
            self.table.clear()
            self.table.setColumnCount(len(df.columns))
            self.table.setRowCount(min(10, len(df)))
            self.table.setHorizontalHeaderLabels(df.columns)
            for i in range(self.table.rowCount()):
                for j in range(self.table.columnCount()):
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

    def rename(self):
        old = self.controller.model.active_file_name
        new = self.name_in.text()
        if old and new and self.controller.model.rename_file(old, new):
            self.controller.update_appbar()
            self.name_in.clear()

    def merge_files(self):
        selected = [self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.list_widget.count()) 
                    if self.list_widget.item(i).checkState() == Qt.CheckState.Checked]
        if self.controller.model.merge_selected(selected):
            self.controller.update_appbar()
