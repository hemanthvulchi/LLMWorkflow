import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QColor
from node_editor.node import Node
from node_editor.openaiconnection import OpenAIConnection
import openai
import json

# Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

class MultiInput_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Multi-Input"
        self.type_text = "Data to be entered"
        self.set_color(title_color=(255, 165, 0))
        self.pin_output = self.add_pin(name="value", is_output=True)
        self.build()
        self.con = OpenAIConnection()
        self.openAIclient = self.con.get_connection()
        
        self.config = {
            "user_prompts": [""],
            "system_prompt": "You will be provided with a message, and your task is to write a detailed report.",
            "max_tokens": 64,
            "model": "gpt-3.5-turbo",
            "id": "",
            "object": "",
            "usage_tokens": ""
        }

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
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

        self.btn = QtWidgets.QPushButton("Run")
        self.btn.clicked.connect(self.btn_chat)
        
        self.config_btn = QtWidgets.QPushButton("Configure")
        self.config_btn.clicked.connect(self.show_configuration)

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
    
    def btn_chat(self):
        messages = [{"role": "system", "content": self.config["system_prompt"]}]
        messages.extend([{"role": "user", "content": prompt} for prompt in self.config["user_prompts"]])
        
        response = self.openAIclient.chat.completions.create(
            model=self.config["model"],
            messages=messages,
            temperature=0.8,
            max_tokens=self.config["max_tokens"],
            top_p=1
        )
        self.config["id"] = response["id"]
        self.config["object"] = response["object"]
        self.config["usage_tokens"] = str(response["usage"]["total_tokens"])
        self.responsetext.setText(response.choices[0].message.content)
        print(response.choices[0].message.content)


class ConfigDialog(QDialog):
    def __init__(self, config_json, parent=None):
        super(ConfigDialog, self).__init__(parent)
        
        self.setWindowTitle("OpenAI Configuration")
        
        config = json.loads(config_json)
        
        self.user_prompts = []
        self.system_prompt = QTextEdit(config.get("system_prompt", ""))
        self.system_prompt.setFixedHeight(50)
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 4096)
        self.max_tokens.setValue(config.get("max_tokens", 150))
        self.model = QLineEdit(config.get("model", "gpt-3.5-turbo"))
        
        self.id_field = QLineEdit(config.get("id", ""))
        self.object_field = QLineEdit(config.get("object", ""))
        self.usage_tokens_field = QLineEdit(config.get("usage_tokens", ""))
        
        self.user_prompts_layout = QVBoxLayout()
        initial_user_prompt = QTextEdit(config.get("user_prompt", ""))
        initial_user_prompt.setFixedHeight(50)
        self.user_prompts.append(initial_user_prompt)
        self.user_prompts_layout.addWidget(initial_user_prompt)
        
        self.add_user_prompt_button = QPushButton("New User Prompt")
        self.add_user_prompt_button.clicked.connect(self.add_user_prompt)
        self.user_prompts_layout.addWidget(self.add_user_prompt_button)
        
        layout = QFormLayout()
        layout.addRow("User Prompts:", self.user_prompts_layout)
        layout.addRow("Assistant Prompt:", self.system_prompt)
        layout.addRow("Max Tokens:", self.max_tokens)
        layout.addRow("Model:", self.model)
        layout.addRow("ID:", self.id_field)
        layout.addRow("Object:", self.object_field)
        layout.addRow("Usage Tokens:", self.usage_tokens_field)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
    def add_user_prompt(self):
        new_user_prompt = QTextEdit()
        new_user_prompt.setFixedHeight(50)
        self.user_prompts.append(new_user_prompt)
        self.user_prompts_layout.insertWidget(self.user_prompts_layout.count() - 1, new_user_prompt)

    def get_configuration(self):
        user_prompts_text = [prompt.toPlainText() for prompt in self.user_prompts]
        config = {
            "user_prompts": user_prompts_text,
            "system_prompt": self.system_prompt.toPlainText(),
            "max_tokens": self.max_tokens.value(),
            "model": self.model.text(),
            "id": self.id_field.text(),
            "object": self.object_field.text(),
            "usage_tokens": self.usage_tokens_field.text()
        }
        return json.dumps(config)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    node = Input_Node()
    node.show()
    sys.exit(app.exec())
