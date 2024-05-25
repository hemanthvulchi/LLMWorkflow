import sys
import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
from node_editor.node import Node
from openpyxl.utils import range_boundaries

class ExcelFileReader(Node):
    def __init__(self):
        super().__init__()
        #self.initUI()
        self.title_text = "Load File"
        self.type_text = "Data to be entered"
        self.data = None
        self.selected_file = None
        self.sheet_name = None

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.setWindowTitle('Excel File Reader')

        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()

        self.file_label = QLabel('Selected file:')
        self.sheet_label = QLabel('Sheet name:')

        self.range_input = QLineEdit(self)
        self.range_input.setPlaceholderText('Enter Excel range (e.g., A1:B10)')

        self.sheet_combobox = QComboBox(self)
        self.sheet_combobox.setEnabled(False)

        self.load_button = QPushButton('Load Excel File', self)
        self.load_button.clicked.connect(self.load_file)

        self.get_data_button = QPushButton('Get Data', self)
        self.get_data_button.clicked.connect(self.get_range)
        self.get_data_button.setEnabled(False)

        self.save_data_button = QPushButton('Save Data', self)
        self.save_data_button.clicked.connect(self.save_data)
        self.save_data_button.setEnabled(False)
        
        layout.addWidget(self.load_button)
        layout.addWidget(self.file_label)
        layout.addWidget(self.sheet_label)
        layout.addWidget(self.range_input)
        layout.addWidget(self.sheet_combobox)
        layout.addWidget(self.get_data_button)
        layout.addWidget(self.save_data_button)

        self.widget.setLayout(layout)
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        super().init_widget()

    def load_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")

        if file_dialog.exec():
            self.selected_file = file_dialog.selectedFiles()[0]
            self.file_label.setText(f'Selected file: {self.selected_file}')

            xls = pd.ExcelFile(self.selected_file)
            self.sheet_combobox.clear()
            self.sheet_combobox.addItems(xls.sheet_names)
            if xls.sheet_names:
                self.sheet_combobox.setCurrentIndex(0)
                self.sheet_combobox.setEnabled(True)
                self.get_data_button.setEnabled(True)
                self.save_data_button.setEnabled(True)

    def get_range(self):
        if not self.selected_file:
            QMessageBox.warning(self, 'Error', 'No file selected.')
            return

        range_str = self.range_input.text()
        self.sheet_name = self.sheet_combobox.currentText()

        try:
            df = pd.read_excel(self.selected_file, sheet_name=self.sheet_name, engine='openpyxl')
            if range_str:
                df = self.get_data_in_range(df, range_str)
            self.data = df
            QMessageBox.information(self, 'Success', f'Selected range:\n{df}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def get_data_in_range(self, df, range_str):
        min_col, min_row, max_col, max_row = range_boundaries(range_str)
        min_col -= 1  # Convert to 0-indexed
        max_col -= 1  # Convert to 0-indexed
        return df.iloc[min_row-1:max_row, min_col:max_col]

    def save_data(self):
        if self.data is None:
            QMessageBox.warning(self, 'Error', 'No data to save.')
            return

        try:
            with pd.ExcelWriter(self.selected_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.data.to_excel(writer, sheet_name=self.sheet_name, index=False)
            QMessageBox.information(self, 'Success', 'Data saved successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_data_by_row(self, row_idx):
        if self.data is not None and 0 <= row_idx < len(self.data):
            return self.data.iloc[row_idx]
        else:
            return None

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    reader = ExcelFileReader()
    reader.show()
    sys.exit(app.exec())
