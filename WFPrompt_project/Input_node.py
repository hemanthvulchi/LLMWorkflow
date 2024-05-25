
from PySide6 import QtWidgets
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from node_editor.node import Node
from node_editor.openaiconnection import OpenAIConnection
from node_editor.configdialog import ConfigDialog
from utils.llmconnection import LLMConnection
import json

# Set your OpenAI API key here
class Input_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "GenAI Input"
        self.type_text = "Data to be entered"
        self.set_color(title_color=(15, 129, 126))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build()
        self.con = OpenAIConnection()
        #self.openAIclient = self.con.get_connection()

        self.config = {
            "user_prompt": "please write a detailed report on the below material",
            "system_prompt": "You are a security risk professional",
            "output":"",
            "max_tokens": 64,
            "model": "gpt-3.5-turbo",
            "id": "",
            "object": "",
            "usage_tokens": ""
        }

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(200)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.textbox = QTextEdit()
        self.textbox.setFixedHeight(50)
        self.responsetext = QTextEdit()
        self.responsetext.setFixedHeight(50)
        self.responsetext.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.responsetext.setReadOnly(True)

        self.btn = QtWidgets.QPushButton("Run")
        self.btn.clicked.connect(self.btn_chat)

        self.config_btn = QtWidgets.QPushButton("Configure")
        self.config_btn.clicked.connect(self.show_configuration)

        layout.addWidget(self.textbox)
        layout.addWidget(self.responsetext)
        layout.addWidget(self.btn)
        layout.addWidget(self.config_btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def show_configuration(self):
        self.config["user_prompt"] = self.textbox.toPlainText()
        config_json = json.dumps(self.config)
        main_window = QtWidgets.QMainWindow()
        self.dialog = ExtendedConfigDialog(config_json, main_window)
        self.dialog.setWindowFlags(self.dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        if self.dialog.exec():
            self.config = json.loads(self.dialog.get_configuration())
            self.responsetext.setText(self.config["output"])
            self.textbox.setText(self.config["user_prompt"])
            self.pin_output.set_data(self.responsetext.toPlainText())
        print("Pin output data:", self.pin_output.get_data())


    def btn_chat(self):

        connection = LLMConnection()

        response = connection.call_prompt(self.textbox.toPlainText(),self.config["system_prompt"],self.config["model"])
        self.responsetext.setText(response.choices[0].message.content)
        self.pin_output.set_data(self.responsetext.toPlainText())

class ExtendedConfigDialog(ConfigDialog):
    def __init__(self, config_json, parent=None):
        super(ExtendedConfigDialog, self).__init__(config_json, parent)
        self.setmainlayout()
        self.setLayout(self.main_layout)
        self.post_prompt.setVisible(False)
        self.complete_prompt.setVisible(False)
