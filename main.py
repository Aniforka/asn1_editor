from PyQt5 import QtWidgets, uic
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
        self.layout_Tree.addWidget(self.tree_widget)

        self.tree = Asn1Tree()
        self.__init_vars()

        self.show()

        self.file_open_action.triggered.connect(self.load_file)
        self.file_save_action.triggered.connect(self.save_file)
        self.file_save_as_action.triggered.connect(self.save_file_as)
        self.clear_all_action.triggered.connect(self.clear_all)

        self.tree_widget.create_item_signal.connect(self.create_tree_item)
        self.tree_widget.action_save_node_as_signal.connect(self.save_node_as)
        self.tree_widget.edit_item_signal.connect(self.edit_tree_item)
        self.tree_widget.edit_hex_item_signal.connect(self.edit_hex_tree_item)
        self.tree_widget.copy_item_signal.connect(self.copy_item_to_clipboard)
        self.tree_widget.delete_item_signal.connect(self.delete_tree_item)


    def __init_vars(self):
        self.tree_widget.clear()
        self.tree_widget.setHeaderLabels([])
        self.tree_widget.setColumnCount(0)
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


    def save_file(self):
        if self.tree.get_root() is not None:
            if self.cur_file:
                try:
                    self.tree.export_to_file(self.cur_file)
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
        cur_item = self.tree_widget.currentItem()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tag = dialog.tag_input.text()

            try:
                self.tree.add_node(cur_item.asn1_tree_element, tag)
            except Exception as exp:
                QtWidgets.QMessageBox.critical(self, 'Ошибка создания', 'Не получилось создать элемент', QtWidgets.QMessageBox.Ok)
                print(exp)
                return

        self.draw_tree()


    def save_node_as(self):
        cur_item = self.tree_widget.currentItem()

        if self.tree.get_root() is not None:
            file = QtWidgets.QFileDialog.getSaveFileName(self,'Сохранение', self.cur_file, self.file_filter)
            if file:
                try:
                    self.tree.export_node_to_file(file[0], cur_item.asn1_tree_element)
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


    def edit_tree_item(self):
        dialog = EditDialog(self)
        dialog.tag_input.setDisabled(True)

        cur_item = self.tree_widget.currentItem()

        tree_item = cur_item.asn1_tree_element
        is_parrent = bool(tree_item.get_childs())

        dialog.tag_field.setText(
            f"{str(tree_item.get_encode_tag())} ({str(hex(tree_item.get_encode_tag()))}):"\
            f" {tree_item.get_tag_type()}"
        )
        dialog.tag_input.setText(str(tree_item.get_encode_tag()))
        dialog.offset_field.setText(str(tree_item.get_offset()))
        dialog.length_field.setText(str(tree_item.get_length()))

        if not is_parrent:
            dialog.data_input.setPlainText(tree_item.get_decode_value())

        cursor = dialog.data_input.textCursor()
        cursor.movePosition(cursor.End)
        dialog.data_input.setTextCursor(cursor)

        if is_parrent:
            dialog.data_input.setDisabled(True)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if not is_parrent:
                new_value = dialog.data_input.toPlainText()

                try:
                    self.tree.edit_node(tree_item, new_value)
                except Exception as exp:
                    QtWidgets.QMessageBox.critical(self, 'Ошибка изменения', 'Не получилось изменить элемент', QtWidgets.QMessageBox.Ok)
                    print(exp)
                    return

        self.draw_tree()


    def edit_hex_tree_item(self):
        dialog = EditDialog(self)
        dialog.tag_input.setDisabled(True)

        cur_item = self.tree_widget.currentItem()

        tree_item = cur_item.asn1_tree_element
        is_parrent = bool(tree_item.get_childs())

        dialog.tag_field.setText(
            f"{str(tree_item.get_encode_tag())} ({str(hex(tree_item.get_encode_tag()))}):"\
            f" {tree_item.get_tag_type()}"
        )
        dialog.tag_input.setText(str(tree_item.get_encode_tag()))
        dialog.offset_field.setText(str(tree_item.get_offset()))
        dialog.length_field.setText(str(tree_item.get_length()))

        if not is_parrent:
            dialog.data_input.setPlainText(tree_item.get_encode_value().hex().upper())

        cursor = dialog.data_input.textCursor()
        cursor.movePosition(cursor.End)
        dialog.data_input.setTextCursor(cursor)

        if is_parrent:
            dialog.data_input.setDisabled(True)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if not is_parrent:
                new_value = dialog.data_input.toPlainText().replace(' ', '')

                if len(new_value) % 2 != 0:
                    QtWidgets.QMessageBox.critical(self, 'Ошибка редактирования', 'Не HEX вид. Не чётная длина', QtWidgets.QMessageBox.Ok)
                    return

                try:
                    self.tree.edit_node(tree_item, new_value, True)
                except Exception as exp:
                    QtWidgets.QMessageBox.critical(self, 'Ошибка изменения', 'Не получилось изменить элемент', QtWidgets.QMessageBox.Ok)
                    print(exp)
                    return


        self.draw_tree()


    def copy_item_to_clipboard(self):
        cur_item = self.tree_widget.currentItem()
    
        try:
            value = self.tree.get_full_encoded_item(cur_item.asn1_tree_element)
        except Exception as exp:
            QtWidgets.QMessageBox.critical(self, 'Ошибка сохранения', 'Не получилось закодировать элемент', QtWidgets.QMessageBox.Ok)
            print(exp)
            return

        clipboard = app.clipboard()
        clipboard.setText(value.hex().upper())


    def delete_tree_item(self):
        cur_item = self.tree_widget.currentItem()

        try:
            self.tree.remove_node(cur_item.asn1_tree_element)
        except Exception as exp:
            QtWidgets.QMessageBox.critical(self, 'Ошибка удаления', 'Не удалить элемент', QtWidgets.QMessageBox.Ok)
            print(exp)
            return

        self.draw_tree()


    def clear_all(self):
        result = QtWidgets.QMessageBox.question(
            self,
            'Подтверждение',
            "Вы действительно хотите очистить всё?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.Yes:
            self.__init_vars()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) #создание приложения
    window = Ui() #получение экземпляра основного интерфейса
    app.exec() #запуск основого интерфейса
