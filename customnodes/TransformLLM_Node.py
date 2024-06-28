from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout, QCheckBox, QSlider, QPushButton
from PySide6.QtCore import Qt
from core.node import Node
from customnodes.common_widgets.configdialog import ConfigDialog
from core.common import Node_Status
from utils.llmconnection import LLMConnection
import json
import utils.themecolors as colors


class TransformLLM_Node(Node):
    def __init__(self,node_config = {}):
        super().__init__()

        self.title_text = "GenAI Transform"
        self.type_text = "Data to be entered and transformed"
        self.set_color(title_color=(44, 110, 96))
        self.pin_A = self.add_pin(name="input A", is_output=False)
        self.pin_output = self.add_pin(name="output", is_output=True)
        self.build(node_config)


    def init_widget(self, node_config):
        self.config = node_config        
        if node_config == {}:
            self.config = {
                "user_prompt": "please enter your prompt here",
                "system_prompt": "You are a security risk professional",
                "output":"",
                "max_tokens": 1024,
                "id": "",
                "properties": "",
                "temperature": "",
                "input1":""
                }    
        else: 
            self.config = node_config        
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(200)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.input1text = QTextEdit()
        if self.pin_A:
            self.input1text.setPlainText(self.config["input1"])
        self.input1text.setFixedHeight(50)
        self.input1text.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.input1text.setReadOnly(True)

        self.textbox = QTextEdit()
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

        self.btnR = QtWidgets.QPushButton("Refresh")
        self.btnR.clicked.connect(self.btn_refresh)


        self.btn = QtWidgets.QPushButton("Run")
        self.btn.clicked.connect(self.btn_chat)

        self.config_btn = QtWidgets.QPushButton("Configure")
        self.config_btn.clicked.connect(self.show_configuration)

        layout.addWidget(self.input1text)
        layout.addWidget(self.btnR)
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
        self.btn_refresh()
        self.config["user_prompt"] = self.textbox.toPlainText()
        strtemp = str(self.pin_A.connected_pin.get_data())
        self.config["additional_input"] = strtemp
        config_json = json.dumps(self.config)
        self.dialog = ExtendedConfigDialog(config_json, QtWidgets.QMainWindow())
        if self.dialog.exec():
            self.config = json.loads(self.dialog.get_configuration())
            self.responsetext.setText(self.config["output"])
            self.textbox.setText(self.config["user_prompt"])
            self.pin_output.set_data(self.responsetext.toPlainText())
            self.status = Node_Status.CLEAN
        print("Pin output data:", self.pin_output.get_data())        

    def btn_refresh(self):
        print("Refreshing data")
        if self.pin_A:
            self.pin_A.set_data(self.pin_A.connected_pin.get_data())
            print("pin A set:",self.pin_A.connected_pin.get_data())
            self.input1text.setText(str(self.pin_A.connected_pin.get_data()))
            str_temp1 = str(self.pin_A.connected_pin.get_data())
        self.config["additional_input"] = str_temp1
 
    def btn_chat(self):
        text1 = self.input1text.toPlainText()
        text3 = self.textbox.toPlainText()

        # Join the text with newline characters
        joined_text = f"{text3}\n{text1}"        
        connection = LLMConnection()
        response = connection.call_prompt(joined_text,self.config["system_prompt"])
        self.responsetext.setText(str(response))
        self.pin_output.set_data(str(response))

class ExtendedConfigDialog(ConfigDialog):
    def __init__(self, config_json, openAIclient, parent=None):
        super(ExtendedConfigDialog, self).__init__(config_json, parent)
        self.setmainlayout()
        self.setLayout(self.main_layout)
        self.post_prompt.setVisible(False)
        #self.additional_input = 

    def updatecompleteprompt(self):
        tempString = self.user_prompt.toPlainText() + "\n" + self.additional_input
        self.complete_prompt.setText(tempString)   
