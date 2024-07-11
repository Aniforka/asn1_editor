from PyQt5 import QtCore, QtWidgets, uic


class EditDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/EditDialog.ui', self)
        # ... (дополнительная инициализация, подключение слотов) ...
