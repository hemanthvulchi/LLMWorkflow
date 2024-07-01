from PySide6 import QtWidgets
from PySide6.QtWidgets import QTextEdit
from core.common import Node_Status
from core.node import Node
import utils.documents.fileextract as fex
from customnodes.common_widgets.PropertiesDialog import PropertiesDialog
import utils.themecolors as colors
import utils.directory as directory
import os

class FileExtract_Node(Node):
    def __init__(self, node_config = {}):
        super().__init__()

        self.title_text = "Extract File"
        self.type_text = "Extract File"
        self.icon_file_path = directory.get_icon_path("fileextract") #make sure to place the icon in resources/node_icons
        self.description = "Enter Description"
        self.set_color(colors.get_color_rgb("input"))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build(node_config)

    def init_widget(self, node_config):  
        super().init_widget(node_config)        

                    
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.filetextbox = QTextEdit()
        self.filetextbox.setPlainText(self.config["output"])
        self.filetextbox.setMinimumHeight(200)
        self.filetextbox.setMinimumWidth(100)
        self.filetextbox.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.filetextbox.setReadOnly(True)


        self.extract_btn = QtWidgets.QPushButton("Extract from file")
        self.extract_btn.clicked.connect(self.btn_extract)


        layout.addWidget(self.filetextbox)
        layout.addWidget(self.extract_btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        self.setOutput()

    def setOutput(self):
        self.pin_output.set_data(self.config["output"])

    def topbar_doubleclick(self):
        dialog = PropertiesDialog(self.title_text, self.description)        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.title_text, self.description = dialog.get_values()
        self.config["title_text"] = self.title_text
        self.config["description"] = self.description
        self.build(self.config)
    
    def btn_extract(self):
        print("btn command:")
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select File", "", "Text, PDF, Word, and PowerPoint Files (*.txt *.pdf *.docx *.pptx))"
        )
        if file_path:
            text_extract = self.extract_document(file_path)
        self.filetextbox.setText(text_extract)
        self.pin_output.set_data(text_extract)
        self.config["output"] = text_extract
        if self.pin_output.get_data() != "":
            self.status = Node_Status.CLEAN
        #self.compute()

    def extract_document(self, file_path):
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.txt':
                with open(file_path, "r", encoding="utf-8") as file:
                    document_text = file.read()
            elif file_extension == '.pdf':
                document_text = fex.extract_text_from_pdf(file_path)
            elif file_extension == '.pptx':
                document_text = fex.extract_text_from_pptx(file_path)
            elif file_extension == '.docx':
                document_text = fex.extract_text_from_docx(file_path)
            else:
                print(f"Unsupported file type: {file_extension}")
                return
            return document_text
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error extracting from document {file_path}, error: {e}")



    def inputupdated(self):
            self.status = Node_Status.DIRTY