from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel
from core.common import Node_Status
from core.node import Node
from WFPrompt_project.common_widgets import FloatLineEdit


class SimpleTransform_Node(Node):
    def __init__(self, node_config = {}):
        super().__init__()

        self.title_text = "Simple Transform"
        self.type_text = "Transform Data"
        self.set_color(title_color=(32, 118, 146))
        self.pin_A = self.add_pin(name="input", is_output=False)
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
        self.textbox = QtWidgets.QTextEdit(self.config["input_prompt"])
        self.textbox.setMinimumHeight(200)
        self.textbox.setMinimumWidth(100)
        self.textbox.textChanged.connect(self.inputupdated)

        self.btnRefresh = QtWidgets.QPushButton("Clear and Refresh")
        self.btnRefresh.clicked.connect(self.btn_refresh)

        self.btnSave = QtWidgets.QPushButton("Save")
        self.btnSave.clicked.connect(self.btn_cmd)

        layout.addWidget(self.textbox)
        layout.addWidget(self.btnRefresh)
        layout.addWidget(self.btnSave)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        self.setOuput()

    def setOuput(self):
        self.pin_output.set_data(self.config["input_prompt"])

    def btn_refresh(self):
        print("Refreshing data")
        temptext = ""
        if self.pin_A and self.pin_A.connected_pin:
            self.pin_A.set_data(self.pin_A.connected_pin.get_data())
            print("pin A set:",self.pin_A.connected_pin.get_data())
            self.textbox.setText(str(self.pin_A.connected_pin.get_data()))
            temptext = str(self.pin_A.connected_pin.get_data())
        self.pin_output.set_data(temptext)
        if temptext != "":
            self.status = Node_Status.CLEAN          
     
    def btn_cmd(self):
        self.pin_output.set_data(self.textbox.toPlainText())
        print("btn command:",self.pin_output.get_data())
        self.config["input_prompt"] = self.textbox.toPlainText()
        if self.pin_output.get_data() != "":
            self.status = Node_Status.CLEAN
        #self.compute()

    def inputupdated(self):
            self.status = Node_Status.DIRTY