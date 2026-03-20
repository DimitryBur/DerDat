from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
                             QPushButton, QFileDialog, QLineEdit, QLabel, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt

class StoreView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("📦 Список загруженных CSV:"))
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        # Подключаем сигнал изменения галочки для обновления списка колонок
        self.list_widget.itemChanged.connect(self.update_column_list)
        layout.addWidget(self.list_widget)

        layout.addWidget(QLabel("👀 Предпросмотр (10 строк):"))
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Блок переименования
        rename_lay = QHBoxLayout()
        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("Новое имя для активного файла...")
        btn_ren = QPushButton("📝 Переименовать")
        btn_ren.clicked.connect(self.rename)
        rename_lay.addWidget(self.name_in)
        rename_lay.addWidget(btn_ren)
        layout.addLayout(rename_lay)

        # Блок управления активами
        btn_lay = QHBoxLayout()
        btn_add = QPushButton("📥 Добавить файл")
        btn_add.clicked.connect(self.add_file)
        
        self.btn_del = QPushButton("🗑 Удалить отмеченные")
        self.btn_del.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_del.clicked.connect(self.delete_selected)
        
        btn_lay.addWidget(btn_add)
        btn_lay.addWidget(self.btn_del)
        layout.addLayout(btn_lay)

        # Блок объединения (Улучшенный)
        merge_lay = QHBoxLayout()
        merge_lay.addWidget(QLabel("Ключ (Join):"))
        
        self.combo_key = QComboBox()
        self.combo_key.setMinimumWidth(200)
        
        btn_merge = QPushButton("🔗 Объединить")
        btn_merge.clicked.connect(self.merge_files)
        
        merge_lay.addWidget(self.combo_key)
        merge_lay.addWidget(btn_merge)
        layout.addLayout(merge_lay)

        # Навигация
        nav = QHBoxLayout()
        btn_next = QPushButton("🧹 Перейти к Очистке >>")
        btn_next.clicked.connect(lambda: controller.switch_page(2))
        nav.addWidget(btn_next)
        layout.addLayout(nav)

    def update_column_list(self):
        """Обновляет выпадающий список колонками ПЕРВОГО отмеченного файла"""
        self.combo_key.clear()
        self.combo_key.addItem("--- Простой Merge (Vertical) ---")
        
        selected = [self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) 
                    for i in range(self.list_widget.count()) 
                    if self.list_widget.item(i).checkState() == Qt.CheckState.Checked]
        
        if selected:
            first_file = selected[0]
            df = self.controller.model.all_files.get(first_file)
            if df is not None:
                self.combo_key.addItems(list(df.columns))

    def add_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSV", "", "*.csv")
        if path:
            name, rows = self.controller.model.add_file(path)
            item = QListWidgetItem(f"{name} ({rows} стр.)")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)
            self.update_column_list()
            self.controller.update_appbar()

    def on_item_clicked(self, item):
        name = item.data(Qt.ItemDataRole.UserRole)
        self.controller.model.active_file_name = name
        self.refresh()
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
        new = self.name_in.text().strip()
        if old and new and self.controller.model.rename_file(old, new):
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == old:
                    item.setData(Qt.ItemDataRole.UserRole, new)
                    item.setText(f"{new} ({len(self.controller.model.all_files[new])} стр.)")
            self.controller.update_appbar()
            self.name_in.clear()

    def delete_selected(self):
        selected = [self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.list_widget.count()) 
                    if self.list_widget.item(i).checkState() == Qt.CheckState.Checked]
        if not selected: return
        confirm = QMessageBox.question(self, "Удаление", f"Удалить выбранные файлы ({len(selected)} шт.)?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.controller.model.delete_multiple_assets(selected)
            for i in range(self.list_widget.count() - 1, -1, -1):
                if self.list_widget.item(i).checkState() == Qt.CheckState.Checked:
                    self.list_widget.takeItem(i)
            self.update_column_list()
            self.controller.update_appbar()

    def update_column_list(self):
        """Обновляет выпадающий список колонками ПЕРВОГО отмеченного файла"""
        # Блокируем сигналы, чтобы не зациклить обновление
        self.combo_key.blockSignals(True)
        self.combo_key.clear()
        self.combo_key.addItem("--- Простой Merge (Vertical) ---")
        
        selected = [self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) 
                    for i in range(self.list_widget.count()) 
                    if self.list_widget.item(i).checkState() == Qt.CheckState.Checked]
        
        if selected:
            first_name = selected[0] # Берем именно первый файл
            df = self.controller.model.all_files.get(first_name)
            if df is not None:
                # df.columns.tolist() гарантирует, что мы передаем список строк, а не объект индекса
                cols = [str(c) for c in df.columns]
                self.combo_key.addItems(cols)
            
        self.combo_key.blockSignals(False)

    def merge_files(self):
        """Логика Smart Merge с выбором конкретной колонки"""
        # 1. Собираем отмеченные файлы
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        
        if len(selected) < 2:
            QMessageBox.warning(self, "Внимание", "Нужно отметить галочками хотя бы 2 файла!")
            return

        # 2. Определяем, что выбрал пользователь в выпадающем списке
        current_idx = self.combo_key.currentIndex()
        
        if current_idx <= 0:
            # Выбрана первая строка (Простой Merge)
            method = 'vertical'
            key_param = None
        else:
            # Выбрана конкретная колонка
            method = 'join'
            key_param = self.combo_key.currentText()
        
        # 3. Запускаем объединение в модели
        result_msg = self.controller.model.smart_merge(selected, method=method, key_column=key_param)
        
        if "Успешно" in result_msg:
            # Добавляем результат в список (UI)
            new_name = self.controller.model.active_file_name
            df = self.controller.model.get_active_df()
            
            item = QListWidgetItem(f"{new_name} ({len(df)} стр.)")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, new_name)
            self.list_widget.addItem(item)
            
            self.controller.update_appbar()
            self.refresh()
            QMessageBox.information(self, "Результат", result_msg)
        else:
            QMessageBox.critical(self, "Ошибка", result_msg)

