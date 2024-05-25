from PySide6 import QtWidgets

class Display:
    message_box = None  # Class-level attribute to keep track of the message box instance

    @staticmethod
    def show_message_box(title, message):
        if Display.message_box is not None:
            Display.message_box.close()
        Display.message_box = QtWidgets.QMessageBox()
        Display.message_box.setWindowTitle(title)
        Display.message_box.setText(message)
        Display.message_box.exec()
    
    @staticmethod
    def show_error_box(title, message):
        if Display.message_box is not None:
            Display.message_box.close()
        Display.message_box = QtWidgets.QMessageBox()
        Display.message_box.setWindowTitle(title)
        Display.message_box.setText(message)
        Display.message_box.exec()