from PySide6 import QtWidgets
from node_editor.node import Node
from node_editor.pin import Pin
from node_editor.connection import Connection
from node_editor.openaiconnection import OpenAIConnection

class Add_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Add"
        self.type_text = "Logic Nodes"
        self.set_color(title_color=(0, 128, 0))

        self.ex_in_pin=self.add_pin(name="Ex In", is_output=False, execution=True)
        self.pin_output = self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.pin_A = self.add_pin(name="input A", is_output=False)
        #self.pin_A_end = Pin(None,None)
        self.pin_B = self.add_pin(name="input B", is_output=False)
        #self.pin_B_end = Pin(None,None)
        self.add_pin(name="output", is_output=True)
        self.build()
        self.con = OpenAIConnection()
        self.openAIClient = self.con.get_connection()
        
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
        strTest = "no connection"

        if self.pin_A:
            self.pin_A.set_data(self.pin_A.connected_pin.get_data())
            print("pin A set:",self.pin_A.connected_pin.get_data())
        if self.pin_B:
            self.pin_B.set_data(self.pin_B.connected_pin.get_data())
            print("pin B set:",self.pin_B.connected_pin.get_data())
