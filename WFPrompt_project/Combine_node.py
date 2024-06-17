import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout, QCheckBox, QSlider, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from core.node import Node
from core.common import Node_Status
import openai
import json

# Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

class Combine_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Combine Data"
        self.type_text = "Data would be combined"
        self.set_color(title_color=(44, 110, 96))
        #self.ex_in_pin=self.add_pin(name="Ex In", is_output=False, execution=True)
        #self.pin_output = self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.pin_A = self.add_pin(name="input A", is_output=False)
        #self.pin_A_end = Pin(None,None)
        self.pin_B = self.add_pin(name="input B", is_output=False)
        self.pin_C = self.add_pin(name="input C", is_output=False)        
        self.pin_D = self.add_pin(name="input D", is_output=False)        
        self.pin_E = self.add_pin(name="input E", is_output=False)        
        #self.pin_B_end = Pin(None,None)
        self.outpin = self.add_pin(name="output A", is_output=True)
        self.outpin2 = self.add_pin(name="output B", is_output=True)
        self.build()

        self.config = {
            "user_prompt": "",
            "system_prompt": "You will be provided with a message, and your task is to write a detailed report.",
            "output":"",
            "max_tokens": 1024,
            "model": "",
            "id": "",
            "object": "",
            "temperature": "",
            "input1":"",
            "input2":""
        }

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(200)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.input1text = QTextEdit()
        self.input1text.setFixedHeight(50)
        self.input1text.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.input1text.setReadOnly(True)

        self.input2text = QTextEdit()
        self.input2text.setFixedHeight(50)
        self.input2text.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.input2text.setReadOnly(True)

        self.input3text = QTextEdit()
        self.input3text.setFixedHeight(50)
        self.input3text.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.input3text.setReadOnly(True)

        self.input4text = QTextEdit()
        self.input4text.setFixedHeight(50)
        self.input4text.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.input4text.setReadOnly(True)

        self.input5text = QTextEdit()
        self.input5text.setFixedHeight(50)
        self.input5text.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.input5text.setReadOnly(True)

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

        self.btnR = QtWidgets.QPushButton("Refresh")
        self.btnR.clicked.connect(self.btn_refresh)

        layout.addWidget(self.input1text)
        layout.addWidget(self.input2text)
        layout.addWidget(self.input3text)
        layout.addWidget(self.input4text)
        layout.addWidget(self.input5text)
        layout.addWidget(self.btnR)
        layout.addWidget(self.responsetext)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()


    def btn_refresh(self):
        print("Refreshing data")
        temptext = ""

        if self.pin_A and self.pin_A.connected_pin:
            self.pin_A.set_data(self.pin_A.connected_pin.get_data())
            print("pin A set:",self.pin_A.connected_pin.get_data())
            self.input1text.setText(str(self.pin_A.connected_pin.get_data()))
            temptext = str(self.pin_A.connected_pin.get_data())
        if self.pin_B and self.pin_B.connected_pin:
            self.pin_B.set_data(self.pin_B.connected_pin.get_data())
            print("pin B set:",self.pin_B.connected_pin.get_data())
            self.input2text.setText(str(self.pin_B.connected_pin.get_data()))
            temptext = temptext + "\n" + str(self.pin_B.connected_pin.get_data())
        if self.pin_C and self.pin_C.connected_pin:
            self.pin_C.set_data(self.pin_C.connected_pin.get_data())
            print("pin B set:",self.pin_C.connected_pin.get_data())
            self.input3text.setText(str(self.pin_C.connected_pin.get_data()))
            temptext = temptext + "\n" + str(self.pin_C.connected_pin.get_data())            
        if self.pin_D and self.pin_D.connected_pin:
            self.pin_D.set_data(self.pin_D.connected_pin.get_data())
            print("pin B set:",self.pin_D.connected_pin.get_data())
            self.input4text.setText(str(self.pin_D.connected_pin.get_data()))
            temptext = temptext + "\n" + str(self.pin_D.connected_pin.get_data())
        if self.pin_E and self.pin_E.connected_pin: 
            self.pin_E.set_data(self.pin_E.connected_pin.get_data())
            print("pin B set:",self.pin_E.connected_pin.get_data())
            self.input5text.setText(str(self.pin_E.connected_pin.get_data()))
            temptext = temptext + "\n" + str(self.pin_E.connected_pin.get_data())            



        self.responsetext.setText(temptext)
        self.outpin.set_data(temptext)
        self.outpin2.set_data(temptext)
        if temptext != "":
            self.status = Node_Status.CLEAN          
 

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    node = Combine_Node()
    node.show()
    sys.exit(app.exec())
