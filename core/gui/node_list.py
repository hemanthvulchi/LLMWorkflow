from PySide6 import QtCore, QtGui, QtWidgets

class ListWidgetButton(QtWidgets.QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("QPushButton { margin: 2px; }")


class NodeList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)  # enable dragging

    def update_project(self, imports):
        # make an item for each custom  class

        for name, data in imports.items():
            name = name.replace("_Node", "")

            item = QtWidgets.QListWidgetItem(name)
            item.module = data["module"]
            item.class_name = data["class"]
            self.addItem(item)


    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        print(item)
        print(item.text())
        if item and item.text():
            name = item.text()
            #name = self.itemWidget(item).text()

            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(name)
            mime_data.item = item
            drag.setMimeData(mime_data)

            # Drag needs a pixmap or else it'll error due to a null pixmap
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtGui.QColor("darkgray"))
            drag.setPixmap(pixmap)
            drag.exec_()

            super().mousePressEvent(event)
