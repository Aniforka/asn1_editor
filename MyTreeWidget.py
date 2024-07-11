from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QApplication

class MyTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        # Создаем действия для контекстного меню
        self.action_edit = QAction("Редактировать", self)
        self.action_delete = QAction("Удалить", self)

        # Подключаем сигналы к слотам (опционально)
        self.action_edit.triggered.connect(self.edit_item)
        self.action_delete.triggered.connect(self.delete_item)

    def contextMenuEvent(self, event):
        # Создаем контекстное меню
        menu = QMenu(self)
        menu.addAction(self.action_edit)
        menu.addAction(self.action_delete)

        # Отображаем меню на позиции курсора
        menu.exec_(event.globalPos())

    def edit_item(self):
        # Обработчик действия "Редактировать"
        item = self.currentItem()
        print(f"Редактируем элемент: {item.text(0)}")

    def delete_item(self):
        # Обработчик действия "Удалить"
        item = self.currentItem()
        print(f"Удаляем элемент: {item.text(0)}")

