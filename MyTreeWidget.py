from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QApplication

from Asn1Tree import Asn1Tree

class MyTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        # Создаем действия для контекстного меню
        self.action_create = QAction("Создать", self)
        self.action_edit = QAction("Редактировать", self)
        self.action_delete = QAction("Удалить", self)

        self.action_create.triggered.connect(self.create_item)
        self.action_edit.triggered.connect(self.edit_item)
        self.action_delete.triggered.connect(self.delete_item)

    def contextMenuEvent(self, event):
        # Создаем контекстное меню
        menu = QMenu(self)
        menu.addAction(self.action_create)
        menu.addAction(self.action_edit)
        menu.addAction(self.action_delete)

        item = self.currentItem()
        is_item_valid = len(item.asn1_tree_element.get_childs())  # Замените на вашу логику проверки

        # Управление состоянием действия "Создать"
        self.action_create.setEnabled(is_item_valid)

        # Отображаем меню на позиции курсора
        menu.exec_(event.globalPos())

    def create_item(self):
        item = self.currentItem()

    def edit_item(self):
        item = self.currentItem()
        print(f"Редактируем элемент: {item.text(0)}")

    def delete_item(self):
        item = self.currentItem()
        print(f"Удаляем элемент: {item.text(0)}")

