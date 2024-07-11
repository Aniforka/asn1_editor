from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QApplication
from Asn1TreeElement import Asn1TreeElement

class MyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, asn1_tree_element, *args):
        super().__init__(*args)
        self.asn1_tree_element = asn1_tree_element