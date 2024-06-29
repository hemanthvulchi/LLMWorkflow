from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QCursor

class PropertiesDialog(QtWidgets.QDialog):
    def __init__(self, title, type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Node Properties")
        self.move(QCursor.pos())        
        self.title_input = QtWidgets.QLineEdit(title)
        self.title_input.setMaxLength(20)
        self.description = QtWidgets.QTextEdit(type)
    
        layout = QtWidgets.QFormLayout(self)
        layout.addRow("Title:", self.title_input)
        layout.addRow("Type Text:", self.description)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self
        )
        layout.addRow(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_values(self):
        return self.title_input.text(), self.description.toPlainText()