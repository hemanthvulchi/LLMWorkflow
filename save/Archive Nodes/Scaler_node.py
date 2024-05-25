from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel

from node_editor.node import Node
from WFPrompt_project.common_widgets import FloatLineEdit


class Scaler_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Scaler"
        self.type_text = "Constants"
        self.set_color(title_color=(255, 165, 0))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.scaler_line = FloatLineEdit()
        self.label = QLabel()      

        self.scaler_line.textChanged.connect(self.label.setText)
        #self.scaler_line.textChanged.connect(self.pin_output.set_data)
        self.btn = QtWidgets.QPushButton("Save")
        self.btn.clicked.connect(self.btn_cmd)


        layout.addWidget(self.scaler_line)
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()
    
    def btn_cmd(self):
        print("btn command:")
        self.pin_output.set_data(self.scaler_line.text())
        print("btn command:",self.pin_output.get_data())
        #self.compute()