from PyQt5.QtWidgets import QTreeWidgetItem
from Asn1TreeElement import Asn1TreeElement

class MyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, asn1_tree_element: Asn1TreeElement, *args):
        super().__init__(*args)
        self.asn1_tree_element = asn1_tree_element
