from PyQt5.QtWidgets import QTreeWidget, QMenu, QAction, QMessageBox
from PyQt5.QtCore import pyqtSignal


class MyTreeWidget(QTreeWidget):
    create_item_signal = pyqtSignal()  # Сигнал о создании
    action_save_node_as_signal = pyqtSignal() # Сигнал о сохранении узла
    edit_item_signal = pyqtSignal()  # Сигнал об изменении
    edit_hex_item_signal = pyqtSignal()  # Сигнал об изменении (hex)
    copy_item_signal = pyqtSignal()  # Сигнал об копировании (hex)
    delete_item_signal = pyqtSignal()  # Сигнал об удалении
    insert_item_before_signal = pyqtSignal() # Сигнал о вставке перед
    insert_item_after_signal = pyqtSignal() # Сигнал о вставке после

    def __init__(self):
        super().__init__()

        # Создаем действия для контекстного меню
        self.action_create = QAction("Создать", self)
        self.action_save_node_as = QAction("Сохранить узел как...", self)
        self.action_edit = QAction("Редактировать", self)
        self.action_edit_hex = QAction("Редактировать в HEX", self)
        self.action_copy = QAction("Копировать", self)
        self.action_delete = QAction("Удалить", self)
        self.action_insert_before = QAction("Вставить перед", self)
        self.action_insert_after = QAction("Вставить после", self)

        self.action_create.triggered.connect(self.create_item)
        self.action_save_node_as.triggered.connect(self.save_node_as)
        self.action_edit.triggered.connect(self.edit_item)
        self.action_edit_hex.triggered.connect(self.edit_hex_item)
        self.action_copy.triggered.connect(self.copy_item)
        self.action_delete.triggered.connect(self.delete_item)
        self.action_insert_before.triggered.connect(self.insert_before_item)
        self.action_insert_after.triggered.connect(self.inser_after_item)

        self.itemDoubleClicked.connect(self.on_item_double_clicked)


    def contextMenuEvent(self, event):
        # Создаем контекстное меню
        menu = QMenu(self)
        menu.addAction(self.action_create)
        menu.addAction(self.action_save_node_as)
        menu.addAction(self.action_edit)
        menu.addAction(self.action_edit_hex)
        menu.addAction(self.action_copy)
        menu.addAction(self.action_delete)
        menu.addAction(self.action_insert_before)
        menu.addAction(self.action_insert_after)

        item = self.currentItem()
        is_item_valid = not item.asn1_tree_element.is_primitive()

        # Управление состоянием действия "Создать"
        self.action_create.setEnabled(is_item_valid)

        # Отображаем меню на позиции курсора
        menu.exec_(event.globalPos())


    def create_item(self):
        self.create_item_signal.emit()

    def save_node_as(self):
        self.action_save_node_as_signal.emit()

    def edit_item(self):
        self.edit_item_signal.emit()

    def edit_hex_item(self):
        self.edit_hex_item_signal.emit()

    def copy_item(self):
        self.copy_item_signal.emit()


    def delete_item(self):
        result = QMessageBox.question(self, 'Подтверждение', "Вы действительно хотите удалить элемент?", QMessageBox.Yes | QMessageBox.No)

        if result == QMessageBox.Yes:
            self.delete_item_signal.emit()
        

    def on_item_double_clicked(self, item, column):
        self.edit_item_signal.emit()

    def insert_before_item(self):
        self.insert_item_before_signal.emit()

    def inser_after_item(self):
        self.insert_item_after_signal.emit()
