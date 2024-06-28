from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel
from core.common import Node_Status
from core.node import Node
import utils.themecolors as colors


class SimpleInput_Node(Node):
    def __init__(self, node_config = {}):
        super().__init__()

        self.title_text = "Simple Input"
        self.type_text = "Just Add Simple Input"
        self.set_color(colors.get_color_rgb("input"))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build(node_config)

    def init_widget(self, node_config):  
        super().init_widget()        
        self.config = node_config        
        if node_config == {}:
            self.config = {
                "input_prompt": "enter your input here",
                }    
        else: 
            self.config = node_config              
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.textbox = QtWidgets.QTextEdit()
        self.textbox.setPlainText(self.config["input_prompt"])
        #self.textbox.setMinimumWidth(50)
        #self.textbox.setFixedHeight(50)
        self.textbox.textChanged.connect(self.inputupdated)
        self.btn = QtWidgets.QPushButton("Save")
        self.btn.clicked.connect(self.btn_cmd)


        layout.addWidget(self.textbox)
        layout.addWidget(self.btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        self.setOuput()

    def setOuput(self):
        self.pin_output.set_data(self.config["input_prompt"])

    
    def btn_cmd(self):
        print("btn command:")
        self.pin_output.set_data(self.textbox.toPlainText())
        print("btn command:",self.pin_output.get_data())
        self.config["input_prompt"] = self.textbox.toPlainText()
        if self.pin_output.get_data() != "":
            self.status = Node_Status.CLEAN
        #self.compute()

    def inputupdated(self):
            self.status = Node_Status.DIRTY