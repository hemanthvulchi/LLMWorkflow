import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout, QCheckBox, QSlider, QPushButton, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem,QStandardItemModel
from core.node import Node
from utils.display import Display
from utils.llmconnection import LLMConnection
from utils.datamodels import SelectedLLM
import json
import traceback

class ConfigDialog(QDialog):
    def __init__(self, config_json, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setWindowTitle("OpenAI Configuration")
        config = json.loads(config_json)
        self.additional_input = config.get("additional_input","")
        self.system_prompt = QTextEdit(config.get("system_prompt", ""))
        self.user_prompt = QTextEdit(config.get("user_prompt", ""))
        #self.user_prompt.setMinimumHeight(30)
        self.user_prompt.setMinimumWidth(200)
        self.post_prompt = QTextEdit()
        #self.post_prompt.setMinimumHeight(30)
        self.post_prompt.setMinimumWidth(200)        
        self.complete_prompt = QTextEdit()
        self.complete_prompt.setMinimumHeight(100)
        self.complete_prompt.setMinimumWidth(300)
        self.complete_prompt.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.complete_prompt.setReadOnly(True)    
        self.user_prompt.textChanged.connect(self.updatecompleteprompt)
        self.post_prompt.textChanged.connect(self.updatecompleteprompt)

        self.responseAPItext = QTextEdit()
        self.responseAPItext.setMinimumHeight(150)
        self.responseAPItext.setMinimumWidth(300)
        self.responseAPItext.setStyleSheet("""
        QTextEdit{
        background: rgb(50, 50, 50); /*background color */
        }
        """)
        self.responseAPItext.setReadOnly(True)
        self.max_tokens_slider = QSlider(Qt.Horizontal)
        self.max_tokens_slider.setRange(256, 32000)
        self.max_tokens_slider.setValue(config.get("max_tokens", 150))
        self.max_tokens_slider.setTickPosition(QSlider.TicksBelow)
        self.max_tokens_slider.setTickInterval(256)
        #self.max_tokens_slider.setValue(1024)
        self.max_tokens_value_label = QLabel(str(self.max_tokens_slider.value()))
        
        self.max_tokens_slider.valueChanged.connect(self.update_max_tokens_label)
        self.model_dropdown = QComboBox()
        self.populate_model_dropdown()
        self.model_dropdown.currentIndexChanged.connect(self.on_modeldropdown_changed)
        self.on_modeldropdown_changed()

        self.id_field = QLineEdit(config.get("id", ""))
        self.object_field = QLineEdit(config.get("object", ""))
        self.temparature_field = QLineEdit(config.get("temperature", ""))

        self.use_reference_data_checkbox = QCheckBox("Search Documents for context (stored in Documents folder)")


        self.advanced_options_checkbox = QCheckBox("Show Advanced Options")
        self.advanced_options_checkbox.stateChanged.connect(self.toggle_advanced_options)

        self.layout = QFormLayout()
        self.layout.addRow("System Prompt:", self.system_prompt)
        self.layout.addRow("User Prompt:", self.user_prompt)
        self.layout.addRow("Post User Prompt:", self.post_prompt)
        self.layout.addRow("Complete Prompt:", self.complete_prompt)
        self.layout.addRow("Response Text:", self.responseAPItext)
        self.layout.addRow("Max Tokens:", self.max_tokens_slider)
        self.layout.addRow("Max Tokens Value:", self.max_tokens_value_label)
        self.layout.addRow(self.use_reference_data_checkbox)
        self.layout.addRow(self.advanced_options_checkbox)

        self.advanced_options_layout = QFormLayout()
        self.advanced_options_layout.addRow("Model: Input-Output Price/1M tokens:", self.model_dropdown)
        self.advanced_options_layout.addRow("ID:", self.id_field)
        self.advanced_options_layout.addRow("Object:", self.object_field)
        self.advanced_options_layout.addRow("Temperature:", self.temparature_field)

        self.advanced_options_widget = QtWidgets.QWidget()
        self.advanced_options_widget.setLayout(self.advanced_options_layout)
        self.advanced_options_widget.setVisible(False)

        self.test_api_button = QPushButton("Submit Prompt")
        self.test_api_button.setStyleSheet("background-color: blue; color: white;")
        self.test_api_button.clicked.connect(self.test_api_connection)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        selfok_button = self.button_box.button(QDialogButtonBox.Ok)
        selfok_button.setStyleSheet("background-color: green; color: white;")
        
        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        self.cancel_button.setStyleSheet("background-color: red; color: white;")
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout = QVBoxLayout()

    def setmainlayout(self):
        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.advanced_options_widget)
        self.main_layout.addWidget(self.test_api_button)
        self.main_layout.addWidget(self.button_box)
        #self.setLayout(self.main_layout)

    def updatecompleteprompt(self):
        tempString = self.user_prompt.toPlainText()+ self.post_prompt.toPlainText() + "\n" + self.additional_input
        self.complete_prompt.setText(tempString)
    
    def update_max_tokens_label(self, value):
        self.max_tokens_value_label.setText(str(value))

    def toggle_advanced_options(self):
        self.advanced_options_widget.setVisible(self.advanced_options_checkbox.isChecked())

    def populate_model_dropdown(self):
        self.model_dropdown.clear()
        llm_models = QStandardItemModel()
        # for text, value in LLM_MODELS:
        #     self.model_dropdown.addItem(text, value)
        sLLM = SelectedLLM()
        for display_text, primary_value, secondary_value in sLLM.available_llms:
            item = QStandardItem(display_text)
            item.setData(primary_value, Qt.UserRole)
            item.setData(secondary_value, Qt.UserRole + 1)
            llm_models.appendRow(item)
        self.model_dropdown.setModel(llm_models)
        self.set_model_value(sLLM.selected_model)

    def set_model_value(self, value):
        model = self.model_dropdown.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            item_value = item.data(Qt.UserRole)  
            if item_value == value:
                self.model_dropdown.setCurrentIndex(index)
                break
 
    def get_model_selected_value(self):
        current_index = self.model_dropdown.currentIndex()
        if current_index >= 0:
            model = self.model_dropdown.model()
            item = model.item(current_index)
            return item.data(Qt.UserRole)
        return None

    def get_model_selected_secondary_value(self):
        current_index = self.model_dropdown.currentIndex()
        if current_index >= 0:
            model = self.model_dropdown.model()
            item = model.item(current_index)
            return item.data(Qt.UserRole + 1)
        return 4096


    def on_modeldropdown_changed(self):
        max = self.get_model_selected_secondary_value()
        self.max_tokens_slider.setRange(256, int(max))

    def test_api_connection(self):
        try:
            connection = LLMConnection()
            complete_prompt = self.user_prompt.toPlainText() + "\n" + self.additional_input
            response = connection.call_prompt(complete_prompt,self.system_prompt.toPlainText(),self.max_tokens_slider.value(),embeddings=self.use_reference_data_checkbox.isChecked())
            Display.show_message_box( "Success", "API connection successful!\nResponse: " + str(response))
            self.responseAPItext.setText(str(response))
        except Exception as e:
            print("Error", f"API connection failed!\nError: {str(e)}")
            Display.show_error_box( "Error", f"API connection failed!\nError: {str(e)}\nDetailed Error:{print(traceback.format_exc())}")

    def get_configuration(self):
        config = {
            "user_prompt": self.user_prompt.toPlainText(),
            "system_prompt": self.system_prompt.toPlainText(),
            "output": self.responseAPItext.toPlainText(),
            "max_tokens": self.max_tokens_slider.value(),
            "additional_input": self.complete_prompt.toPlainText(),
            "model": self.get_model_selected_value(),
            "id": self.id_field.text(),
            "object": self.object_field.text(),
            "temperature": self.temparature_field.text()
        }
        return json.dumps(config)
    
    def update_additional_input(self,str_data):
        self.additional_input = str_data