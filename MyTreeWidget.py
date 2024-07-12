from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal

from Asn1Tree import Asn1Tree

class MyTreeWidget(QTreeWidget):
    create_item_signal = pyqtSignal()  # Сигнал о создании
    action_save_node_as_signal = pyqtSignal() # Сигнал о сохранении узла
    edit_item_signal = pyqtSignal()  # Сигнал об изменении
    edit_hex_item_signal = pyqtSignal()  # Сигнал об изменении (hex)
    delete_item_signal = pyqtSignal()  # Сигнал об удалении

    def __init__(self):
        super().__init__()

        # Создаем действия для контекстного меню
        self.action_create = QAction("Создать", self)
        self.action_save_node_as = QAction("Сохранить узел как...", self)
        self.action_edit = QAction("Редактировать", self)
        self.action_edit_hex = QAction("Редактировать в HEX", self)
        self.action_delete = QAction("Удалить", self)

        self.action_create.triggered.connect(self.create_item)
        self.action_save_node_as.triggered.connect(self.save_node_as)
        self.action_edit.triggered.connect(self.edit_item)
        self.action_edit_hex.triggered.connect(self.edit_hex_item)
        self.action_delete.triggered.connect(self.delete_item)

        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def contextMenuEvent(self, event):
        # Создаем контекстное меню
        menu = QMenu(self)
        menu.addAction(self.action_create)
        menu.addAction(self.action_save_node_as)
        menu.addAction(self.action_edit)
        menu.addAction(self.action_edit_hex)
        menu.addAction(self.action_delete)

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

    def delete_item(self):
        result = QMessageBox.question(self, 'Подтверждение', "Вы действительно хотите удалить элемент?", QMessageBox.Yes | QMessageBox.No)

        if result == QMessageBox.Yes:
            self.delete_item_signal.emit()
        

    def on_item_double_clicked(self, item, column):
        self.edit_item_signal.emit()
