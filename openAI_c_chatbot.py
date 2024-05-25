import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from utils.llmconnection import LLMConnection
import logging
#logging.basicConfig(level=logging.DEBUG)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = LLMConnection()
        self.connection.initiate_assistant("Simple Chat Bot","You are a helpful assistant","gpt-3.5-turbo")
        self.setWindowTitle("Chat App")

        # Create UI elements
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)  # Make the chat history non-editable
        self.input_box = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send_button_clicked)

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.chat_history)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_send_button_clicked(self):
        user_input = self.input_box.text()
        ai_response = self.send_message_to_openai(user_input)
        self.chat_history.append(f"User: {user_input}\nAI: {ai_response}\n")
        self.input_box.clear()

    def send_message_to_openai(self,message):
        response = self.connection.call_assistant(message,4096)
        return response

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())