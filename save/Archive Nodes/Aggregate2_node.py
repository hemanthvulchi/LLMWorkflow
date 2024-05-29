import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout, QCheckBox, QSlider, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from node_editor.node import Node
from node_editor.openaiconnection import OpenAIConnection
import openai
import json

# Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

class Aggregate2_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "GenAI Aggregate"
        self.type_text = "Data to be entered"
        self.set_color(title_color=(255, 165, 0))
        #self.ex_in_pin=self.add_pin(name="Ex In", is_output=False, execution=True)
        #self.pin_output = self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.pin_A = self.add_pin(name="input A", is_output=False)
        #self.pin_A_end = Pin(None,None)
        self.pin_B = self.add_pin(name="input B", is_output=False)
        #self.pin_B_end = Pin(None,None)
        self.pin_output = self.add_pin(name="output", is_output=True)
        self.build()
        self.con = OpenAIConnection()
        self.openAIclient = self.con.get_connection()

        self.config = {
            "user_prompt": "",
            "system_prompt": "You will be provided with a message, and your task is to write a detailed report.",
            "output":"",
            "max_tokens": 64,
            "model": "gpt-3.5-turbo",
            "id": "",
            "object": "",
            "temperature": "",
            "input1":"",
            "input2":""
        }

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
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


        self.btn = QtWidgets.QPushButton("Run")
        self.btn.clicked.connect(self.btn_chat)

        self.config_btn = QtWidgets.QPushButton("Configure")
        self.config_btn.clicked.connect(self.show_configuration)

        layout.addWidget(self.input1text)
        layout.addWidget(self.input2text)
        layout.addWidget(self.btnR)
        layout.addWidget(self.textbox)
        layout.addWidget(self.responsetext)
        layout.addWidget(self.btn)
        layout.addWidget(self.config_btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def show_configuration(self):
        config_json = json.dumps(self.config)
        dialog = ConfigDialog(config_json, self.widget)
        if dialog.exec():
            self.config = json.loads(dialog.get_configuration())
            self.responsetext.setText(self.config["output"])
            self.textbox.setText(self.config["user_prompt"])
            self.pin_output.set_data(self.responsetext.toPlainText())
        print("Pin output data:", self.pin_output.get_data())

    def btn_refresh(self):
        print("Refreshing data")
        if self.pin_A:
            self.pin_A.set_data(self.pin_A.connected_pin.get_data())
            print("pin A set:",self.pin_A.connected_pin.get_data())
            self.input1text.setText(str(self.pin_A.connected_pin.get_data()))
            self.config["input1"] = str(self.pin_A.connected_pin.get_data())
        if self.pin_B:
            self.pin_B.set_data(self.pin_B.connected_pin.get_data())
            print("pin B set:",self.pin_B.connected_pin.get_data())
            self.input2text.setText(str(self.pin_B.connected_pin.get_data()))
            self.config["input2"] = str(self.pin_B.connected_pin.get_data())
 
    def btn_chat(self):
        text1 = self.input1text.toPlainText()
        text2 = self.input2text.toPlainText()
        text3 = self.textbox.toPlainText()

        # Join the text with newline characters
        joined_text = f"{text1}\n{text2}\n{text3}"        
        response = self.openAIclient.chat.completions.create(
            model=self.config["model"],
            messages=[
                {
                    "role": "system",
                    "content": self.config["system_prompt"]
                },
                {
                    "role": "user",
                    "content": joined_text
                }
            ],
            temperature=0.8,
            max_tokens=self.config["max_tokens"],
            top_p=1
        )
        #self.config["id"] = response["id"]
        #self.config["object"] = response["object"]
        #self.config["usage_tokens"] = str(response["usage"]["total_tokens"])
        self.responsetext.setText(response.choices[0].message.content)
        self.pin_output.set_data(self.responsetext.toPlainText())
        print("Pin output data:", self.pin_output.get_data())
        #print(response.choices[0].message.content)
        #print(self.config)

class ConfigDialog(QDialog):
    def __init__(self, config_json,openAIclient, parent=None):
        super(ConfigDialog, self).__init__(parent)

        self.setWindowTitle("OpenAI Configuration")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.openAIclient = openAIclient
        config = json.loads(config_json)
        self.system_prompt = QTextEdit(config.get("system_prompt", ""))
        self.user_prompt = QTextEdit(config.get("user_input", ""))
        self.user_prompt.setMinimumHeight(60)
        self.user_prompt.setMinimumWidth(500)
        self.responseAPItext = QTextEdit()
        self.responseAPItext.setMinimumHeight(400)
        self.responseAPItext.setMinimumWidth(300)
        self.responseAPItext.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.responseAPItext.setReadOnly(True)        
        self.max_tokens_slider = QSlider(Qt.Horizontal)
        self.max_tokens_slider.setRange(1, 4096)
        self.max_tokens_slider.setValue(config.get("max_tokens", 150))
        self.max_tokens_slider.setTickPosition(QSlider.TicksBelow)
        self.max_tokens_slider.setTickInterval(50)
        self.max_tokens_value_label = QLabel(str(self.max_tokens_slider.value()))
        
        self.max_tokens_slider.valueChanged.connect(self.update_max_tokens_label)

        self.model = QLineEdit(config.get("model", "gpt-3.5-turbo"))
        self.id_field = QLineEdit(config.get("id", ""))
        self.object_field = QLineEdit(config.get("object", ""))
        self.usage_tokens_field = QLineEdit(config.get("usage_tokens", ""))

        self.advanced_options_checkbox = QCheckBox("Show Advanced Options")
        self.advanced_options_checkbox.stateChanged.connect(self.toggle_advanced_options)

        layout = QFormLayout()
        layout.addRow("Assistant Prompt:", self.system_prompt)
        layout.addRow("User Prompt:", self.user_prompt)
        layout.addRow("Response Text:", self.responseAPItext)
        layout.addRow("Max Tokens:", self.max_tokens_slider)
        layout.addRow("Max Tokens Value:", self.max_tokens_value_label)
        layout.addRow(self.advanced_options_checkbox)

        self.advanced_options_layout = QFormLayout()
        self.advanced_options_layout.addRow("Model:", self.model)
        self.advanced_options_layout.addRow("ID:", self.id_field)
        self.advanced_options_layout.addRow("Object:", self.object_field)
        self.advanced_options_layout.addRow("Usage Tokens:", self.usage_tokens_field)

        self.advanced_options_widget = QtWidgets.QWidget()
        self.advanced_options_widget.setLayout(self.advanced_options_layout)
        self.advanced_options_widget.setVisible(False)

        self.test_api_button = QPushButton("Test API Connection")
        self.test_api_button.setStyleSheet("background-color: blue; color: white;")
        self.test_api_button.clicked.connect(self.test_api_connection)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setStyleSheet("background-color: green; color: white;")
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet("background-color: red; color: white;")
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.advanced_options_widget)
        main_layout.addWidget(self.test_api_button)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def update_max_tokens_label(self, value):
        self.max_tokens_value_label.setText(str(value))

    def toggle_advanced_options(self):
        self.advanced_options_widget.setVisible(self.advanced_options_checkbox.isChecked())

    def test_api_connection(self):
        try:
            print("in config dialog")
            self.con = OpenAIConnection()
            self.openAIclient2 = self.con.get_connection()            
            response = self.openAIclient2.chat.completions.create(
                model=self.model.text(),
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt.toPlainText()
                    },
                    {
                        "role": "user",
                        "content": self.user_prompt.toPlainText()
                    }
                ],
                max_tokens=self.max_tokens_slider.value(),
                top_p=1
            )
            QtWidgets.QMessageBox.information(self, "Success", "API connection successful!\nResponse: " + response.choices[0].message.content)
            self.responseAPItext.setText(response.choices[0].message.content)
        except Exception as e:
            print("Error", f"API connection failed!\nError: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"API connection failed!\nError: {str(e)}")

    def get_configuration(self):
        config = {
            "user_prompt": self.user_prompt.toPlainText(),
            "system_prompt": self.system_prompt.toPlainText(),
            "output": self.responseAPItext.toPlainText(),
            "max_tokens": self.max_tokens_slider.value(),
            "model": self.model.text(),
            "id": self.id_field.text(),
            "object": self.object_field.text(),
            "usage_tokens": self.usage_tokens_field.text()
        }
        return json.dumps(config)

