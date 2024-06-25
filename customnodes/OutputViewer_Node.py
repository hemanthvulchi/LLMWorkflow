from PySide6 import QtWidgets, QtGui
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from core.node import Node

class OutputViewer_Node(Node):
    def __init__(self, node_config = {}):
        super().__init__()

        self.title_text = "Output Viewere"
        self.type_text = "View ouput"
        self.set_color(title_color=(3, 87, 254))

        #self.add_pin(name="Ex In", is_output=False, execution=True)

        self.pin_A = self.add_pin(name="input", is_output=False)
        self.build(node_config)

    def init_widget(self, node_config):
        super().init_widget()        
        self.config = node_config        
        if node_config == {}:
            self.config = {
                "user_prompt": "write your prompt here",
                "system_prompt": "You are a security risk professional",
                "output":"",
                "max_tokens": 1024,
                "id": "",
                "object": "",
                "temperature": ""
            }    
        else: 
            self.config = node_config

        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        btn_ouput = QtWidgets.QPushButton("Show Output")
        btn_ouput.clicked.connect(self.btn_refresh)

        layout.addWidget(btn_ouput)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)


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



        # Add a save button to the dialog
        save_button = QtWidgets.QPushButton("Save to File")
        save_button.clicked.connect(lambda: self._save_to_file(text_area.toPlainText()))
        layout.addWidget(save_button)

        # Add a copy button to the dialog
        copy_button = QtWidgets.QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(text_area.toPlainText()))
        layout.addWidget(copy_button)

        # Add a print button to the dialog
        print_button = QtWidgets.QPushButton("Print Output")
        print_button.clicked.connect(lambda: self._print_output(text_area.toPlainText()))
        layout.addWidget(print_button)

        dialog.setLayout(layout)

        # Show the dialog and bring it to the front
        dialog.show()
        dialog.activateWindow()
        dialog.raise_()

    def _copy_to_clipboard(self, text):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

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

    def _save_to_file(self, text):
        # Open a file dialog to specify the file location
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save Output to File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    file.write(text)
                print(f"Output saved to {file_name}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Save Error", f"Could not save file: {e}")
