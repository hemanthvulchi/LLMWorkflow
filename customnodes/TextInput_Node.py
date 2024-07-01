from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel
from core.common import Node_Status
from core.node import Node
from customnodes.common_widgets.PropertiesDialog import PropertiesDialog
import utils.themecolors as colors
import utils.directory as directory


class TextInput_Node(Node):
    def __init__(self, node_config = {}):
        super().__init__()

        self.title_text = "Text Input"
        self.type_text = "Text Input"
        self.icon_file_path = directory.get_icon_path("textinput") #make sure to place the icon in resources/node_icons
        self.description = "Enter Description"
        self.set_color(colors.get_color_rgb("input"))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build(node_config)

    def init_widget(self, node_config):  
        super().init_widget(node_config)        

                   
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

    def topbar_doubleclick(self):
        dialog = PropertiesDialog(self.title_text, self.description)        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.title_text, self.description = dialog.get_values()
        self.config["title_text"] = self.title_text
        self.config["description"] = self.description
        self.build(self.config)    

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