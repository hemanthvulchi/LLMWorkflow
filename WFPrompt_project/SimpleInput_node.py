from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel

from node_editor.node import Node
from WFPrompt_project.common_widgets import FloatLineEdit


class SimpleInput_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Simple Input"
        self.type_text = "Just Add Simple Input"
        self.set_color(title_color=(15, 129, 126))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        #self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.textbox = QtWidgets.QTextEdit()
        self.textbox.setMinimumHeight(200)
        self.textbox.setMinimumWidth(100)
        self.btn = QtWidgets.QPushButton("Save")
        self.btn.clicked.connect(self.btn_cmd)


        layout.addWidget(self.textbox)
        layout.addWidget(self.btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()
    
    def btn_cmd(self):
        print("btn command:")
        self.pin_output.set_data(self.textbox.toPlainText())
        print("btn command:",self.pin_output.get_data())
        #self.compute()