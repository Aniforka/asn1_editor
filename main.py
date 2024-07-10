from PyQt5 import QtCore, QtWidgets, uic
import sys
import os

from Asn1Tree import Asn1Tree

class Ui(QtWidgets.QMainWindow, QtWidgets.QWidget): #класс основого интерфейса программы
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/MainWindow.ui', self)

        self.tree = Asn1Tree()
        self.__init_vars()

        self.show()

        self.file_open_action.triggered.connect(self.load_file)
        self.clear_all_action.triggered.connect(self.clear_all)

    def __init_vars(self):
        self.treeWidget.clear()
        del self.tree
        self.tree = Asn1Tree()
        self.cur_file = None

    def load_file(self):
        self.__init_vars()

        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл', os.getcwd(), "Сертификаты (*.cer);;Все файлы (*)")
        if file:
            self.cur_file = file[0]
            self.tree.import_from_file(file[0])
            self.draw_tree()

    def draw_tree(self):
        self.treeWidget.clear()
        self.treeWidget.setHeaderLabels([os.path.basename(self.cur_file)])

        nodes_to_visit = [(self.tree.root, None)]

        while nodes_to_visit:
            current_node, parent_item = nodes_to_visit.pop(0)

            item = QtWidgets.QTreeWidgetItem(parent_item)
            item_text = f"({current_node.get_offset()}, {current_node.get_length()}) {current_node.get_tag_type()}"
            value = current_node.get_decode_value()
            if value is not None:
                item_text += f": {value}"
            item.setText(0, item_text)

            if parent_item is None:
                self.treeWidget.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            for child in reversed(current_node.childs):
                nodes_to_visit.insert(0, (child, item))

        self.treeWidget.expandAll()

    def clear_all(self):
        self.__init_vars()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) #создание приложения
    window = Ui() #получение экземпляра основного интерфейса
    app.exec() #запуск основого интерфейса
