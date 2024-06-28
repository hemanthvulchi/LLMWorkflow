
from PySide6 import QtWidgets
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from core.node import Node
from customnodes.common_widgets.configdialog import ConfigDialog
from core.common import Node_Status
from utils.llmconnection import LLMConnection
import utils.themecolors as colors
import json

# Set your OpenAI API key here
class Test_Node(Node):
    def __init__(self, node_config = {}):
        super().__init__()
        self.title_text = "Test"
        self.type_text = "Test"
        self.node_config = node_config
        self.set_color(colors.get_color_rgb("input"))
        self.pin_output = self.add_pin(name="value", is_output=True)
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
                "properties": "",
                "temperature": ""
            }    
        else: 
            self.config = node_config
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(200)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.textbox = QTextEdit()
        self.textbox.setPlainText(self.config["user_prompt"])
        self.textbox.setFixedHeight(50)
        self.responsetext = QTextEdit()
        self.responsetext.setPlainText(self.config["output"])
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
        print("Build in init again")
        layout.addWidget(self.textbox)
        layout.addWidget(self.responsetext)
        layout.addWidget(self.btn)
        layout.addWidget(self.config_btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        self.setOuput()

    def setOuput(self):
        self.pin_output.set_data(self.config["output"])

    def show_configuration(self):
        self.config["user_prompt"] = self.textbox.toPlainText()
        config_json = json.dumps(self.config)
        main_window = QtWidgets.QMainWindow()
        self.dialog = ExtendedConfigDialog(config_json, main_window)
        #self.dialog.setWindowFlags(self.dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        if self.dialog.exec():
            self.config = json.loads(self.dialog.get_configuration())
            self.responsetext.setText(self.config["output"])
            self.textbox.setText(self.config["user_prompt"])
            self.pin_output.set_data(self.responsetext.toPlainText())
            if self.pin_output.get_data() != "":
                self.status = Node_Status.CLEAN            
        print("Pin output data:", self.pin_output.get_data())


    def btn_chat(self):
        self.title_text = self.textbox.toPlainText()
        self.build(self.node_config)
        # connection = LLMConnection()
        # response = connection.call_prompt(self.textbox.toPlainText(),self.config["system_prompt"])
        # self.status = Node_Status.CLEAN  
        # self.responsetext.setText(str(response))
        # self.pin_output.set_data(self.responsetext.toPlainText())

class ExtendedConfigDialog(ConfigDialog):
    def __init__(self, config_json, parent=None):
        super(ExtendedConfigDialog, self).__init__(config_json, parent)
        self.setmainlayout()
        self.setLayout(self.main_layout)
        self.post_prompt.setVisible(False)
        self.complete_prompt.setVisible(False)
