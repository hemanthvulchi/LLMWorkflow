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
        original_pos = Display.message_box.pos()
        offset_x = 1200  # Move 20 pixels to the right
        offset_y = 500  # Move 15 pixels up
        new_x = original_pos.x() + offset_x
        new_y = original_pos.y() + offset_y        
        Display.message_box.move(new_x, new_y)
        Display.message_box.exec()
    
    @staticmethod
    def show_error_box(title, message):
        if Display.message_box is not None:
            Display.message_box.close()
        Display.message_box = QtWidgets.QMessageBox()
        Display.message_box.setWindowTitle(title)
        Display.message_box.setText(message)
        original_pos = Display.message_box.pos()
        offset_x = 1200  # Move 20 pixels to the right
        offset_y = 500  # Move 15 pixels up
        new_x = original_pos.x() + offset_x
        new_y = original_pos.y() + offset_y        
        Display.message_box.move(new_x, new_y)
        Display.message_box.exec()