from PyQt5 import QtCore, QtWidgets, uic
import sys
import os

from Asn1Tree import Asn1Tree
from MyTreeWidget import MyTreeWidget
from MyTreeWidgetItem import MyTreeWidgetItem
from EditDialog import EditDialog

class Ui(QtWidgets.QMainWindow, QtWidgets.QWidget): #класс основого интерфейса программы
    file_filter = (
        "Сертификаты (*.cer *.crl);; "  # Сертификаты и списки отзыва сертификатов
        "Запросы на сертификаты (*.p10);; "  # Запросы на сертификаты
        "Файлы подписи (*.p7s);; "  # Файлы подписи
        "Все файлы (*)"  # На всякий случай, для отображения всех файлов 
    )

    # file_filter = (
    #     "Сертификаты (*.cer *.crt *.der);; "
    #     "Запросы на сертификаты (*.csr *.p10);; "
    #     "Закрытые ключи (*.key *.pem);; "
    #     "Списки отозванных сертификатов (*.crl);; "
    #     "Файлы PKCS#7 (*.p7b *.p7c *.p7m *.p7r *.p7s);; "
    #     "Файлы PKCS#12 (*.p12 *.pfx);; "
    #     "Все файлы (*)" 
    # )


    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/MainWindow.ui', self)

        self.tree_widget = MyTreeWidget()
        self.Layout_Tree.addWidget(self.tree_widget)

        self.tree = Asn1Tree()
        self.__init_vars()

        self.show()

        self.file_open_action.triggered.connect(self.load_file)
        self.file_save_as_action.triggered.connect(self.save_file_as)
        self.clear_all_action.triggered.connect(self.clear_all)

        self.tree_widget.create_item_signal.connect(self.create_tree_item)
        self.tree_widget.edit_item_signal.connect(self.edit_tree_item)
        self.tree_widget.delete_item_signal.connect(self.delete_tree_item)


    def __init_vars(self):
        self.tree_widget.clear()
        del self.tree
        self.tree = Asn1Tree()
        self.cur_file = None


    def load_file(self):
        self.__init_vars()

        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл', os.getcwd(), self.file_filter)
        
        if file:
            self.cur_file = file[0]
            try:
                self.tree.import_from_file(file[0])
                self.draw_tree()
            except Exception as exp:
                QtWidgets.QMessageBox.critical(self, 'Ошибка чтения', 'Не удалось считать файл', QtWidgets.QMessageBox.Ok)
                print(exp)
                return


    def save_file_as(self):
        if self.tree.get_root() is not None:
            file = QtWidgets.QFileDialog.getSaveFileName(self,'Сохранить файл', self.cur_file, self.file_filter)
            if file:
                try:
                    self.tree.export_to_file(file[0])
                except Exception as exp:
                    QtWidgets.QMessageBox.critical(self, 'Ошибка сохранения', 'Не удалось сохранить файл', QtWidgets.QMessageBox.Ok)
                    print(exp)
                    return
            else:
                QtWidgets.QMessageBox.critical(self, 'Ошибка сохранения', 'Файл для сохранения не указан', QtWidgets.QMessageBox.Ok)
                return
        else:
            QtWidgets.QMessageBox.critical(self, 'Ошибка сохранения', 'Нет данных для сохранения', QtWidgets.QMessageBox.Ok)
            return


    def draw_tree(self):
        self.tree_widget.clear()
        self.tree_widget.setHeaderLabels([os.path.basename(self.cur_file)])

        if self.tree.root is None:
            return

        nodes_to_visit = [(self.tree.root, None)]

        while nodes_to_visit:
            current_node, parent_item = nodes_to_visit.pop(0)

            item = MyTreeWidgetItem(current_node, parent_item)
            item_text = f"({current_node.get_offset()}, {current_node.get_length()}) {current_node.get_tag_type()}"
            value = current_node.get_decode_value()
            if value is not None:
                item_text += f": {value}"
            item.setText(0, item_text)

            if parent_item is None:
                self.tree_widget.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, (child, item))

        self.tree_widget.expandAll()


    def create_tree_item(self):
        dialog = EditDialog(self)
        dialog.data_input.setDisabled(True)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tag = dialog.tag_input.text()

            print(f"Tag: {tag}\n")


    def edit_tree_item(self):
        dialog = EditDialog(self)
        dialog.tag_input.setDisabled(True)

        cur_item = self.tree_widget.currentItem()

        tree_item = cur_item.asn1_tree_element
        dialog.tag_field.setText(
            f"{str(tree_item.get_encode_tag())} ({str(hex(tree_item.get_encode_tag()))}):"\
            f" {tree_item.get_tag_type()}"
        )
        dialog.tag_input.setText(str(tree_item.get_encode_tag()))
        dialog.offset_field.setText(str(tree_item.get_offset()))
        dialog.length_field.setText(str(tree_item.get_length()))

        is_parrent = bool(tree_item.get_childs())
        if is_parrent:
            dialog.data_input.setDisabled(True)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if not is_parrent:
                new_value = dialog.data_input.toPlainText()
                self.tree.edit_node(tree_item, new_value)

        self.draw_tree()


    def delete_tree_item(self):
        cur_item = self.tree_widget.currentItem()

        self.tree.remove_node(cur_item.asn1_tree_element)
        self.draw_tree()


    def clear_all(self):
        self.__init_vars()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) #создание приложения
    window = Ui() #получение экземпляра основного интерфейса
    app.exec() #запуск основого интерфейса
