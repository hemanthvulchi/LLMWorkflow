from PySide6 import QtWidgets, QtGui
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from node_editor.node import Node



class Print_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Print"
        self.type_text = "Debug Nodes"
        self.set_color(title_color=(3, 87, 254))

        self.add_pin(name="Ex In", is_output=False, execution=True)

        self.pin_A = self.add_pin(name="input", is_output=False)
        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        btn_ouput = QtWidgets.QPushButton("Show Output")
        btn_ouput.clicked.connect(self.btn_refresh)

        btn_copy = QtWidgets.QPushButton("Copy to Clipboard")
        btn_copy.clicked.connect(self.btn_copy)


        layout.addWidget(btn_ouput)
        layout.addWidget(btn_copy)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()        

    def btn_copy(self):
        temptext = ""
        if self.pin_A and self.pin_A.connected_pin:
            temptext = self.pin_A.connected_pin.get_data()
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(temptext)                

    def btn_refresh(self):
        print("Refreshing data")
        temptext = ""
        if self.pin_A and self.pin_A.connected_pin:
            temptext = self.pin_A.connected_pin.get_data()

        # Create and configure the dialog box
        dialog = QtWidgets.QDialog(self.scene().views()[0])  # Parent to the main window
        dialog.setWindowTitle("Output Viewer")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(200)
        dialog.setModal(True)  # Make it modal to grab focus

        layout = QtWidgets.QVBoxLayout()
        text_area = QtWidgets.QTextEdit()
        text_area.setReadOnly(True)  # Make the text area read-only
        text_area.setText(temptext)
        layout.addWidget(text_area)

        # Add a print button to the dialog
        print_button = QtWidgets.QPushButton("Print Output")
        print_button.clicked.connect(lambda: self._print_output(text_area.toPlainText()))
        layout.addWidget(print_button)

        dialog.setLayout(layout)

        # Show the dialog and bring it to the front
        dialog.show()
        dialog.activateWindow()
        dialog.raise_()

    def _print_output(self, text):
        # You'll need to implement the actual printing logic here
        print("Printing output:", text)

        # Example using QPrinter (you'll need to customize this)
        printer = QPrinter()
        # ... configure printer settings ...
        print_dialog = QPrintDialog(printer)
        if print_dialog.exec() == QtWidgets.QDialog.Accepted:
            text_document = QtGui.QTextDocument()
            text_document.setPlainText(text)
            text_document.print_(printer)  

