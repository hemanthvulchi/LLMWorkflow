from PySide6 import QtWidgets
from core.node import Node


class Summarize_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Summarize"
        self.type_text = "Summarize Results"
        self.set_color(title_color=(0, 128, 0))
        self.add_pin(name="input A", is_output=False)
        self.add_pin(name="input B", is_output=False)
        self.add_pin(name="output", is_output=True)
        self.build()
        
    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        btn = QtWidgets.QPushButton("Button test")
        btn.clicked.connect(self.btn_cmd)
        layout.addWidget(btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def compute(self):
            # Retrieve values from input pins
            input_a = self.get_pin("input A").get_value()
            input_b = self.get_pin("input B").get_value()

            # Perform addition
            result = input_a + input_b

            # Set the result on the output pin
            self.get_pin("output").set_value(result)
            print(result)
            # Optionally, handle execution flow
            self.execute_output()

    def execute_output(self):
        # This method would execute the next node connected to the "Ex Out" pin
        ex_out_pin = self.get_pin("Ex Out")
        if ex_out_pin.is_connected():
            next_node = ex_out_pin.connected_node()
            next_node.execute()

    def btn_cmd(self):
        print("btn command")
        self.compute()