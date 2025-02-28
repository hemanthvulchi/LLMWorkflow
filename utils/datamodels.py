from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QMessageBox, QApplication, QPushButton, QLabel, QGridLayout
from PySide6 import QtGui, QtCore, QtWidgets
import sys

LLM_MODELS = []
DEFAULT_MODEL = ""

class SelectedLLM:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SelectedLLM, cls).__new__(cls)
            cls._instance.selected_company = ""
            cls._instance.selected_model = ""
            cls._instance.available_llms = []
        return cls._instance

class ModelSelection:
    def __init__(self):
        self.llm_companies = ["OpenAI GPTs", "Google Gemini","Meta","DeepSeek"]  

        self.llm_models = {
            "OpenAI GPTs": [
                ("GPT-4o(128K): $5.00 & $15.00", "gpt-4o", "4096"),
                ("GPT-4-turbo(128K): $10.00 & $30.00", "gpt-4-turbo", "4096"),
                ("GPT-4(8K): $30.00 & $60.00", "gpt-4", "4096"),
                ("GPT-3.5-turbo(16K): $0.50 & $1.50", "gpt-3.5-turbo", "4096")
            ],
            "Google Gemini": [
                ("Gemini 1.5 Pro(1M): $3.50-7.00 & $10.50-21.10", "gemini-1.5-pro", "1048576"),
                ("Gemini 1.5 Flash(1M): $0.35-0.70 & $1.05-2.10", "gemini-1.5-flash", "1048576"),
                ("Gemini 1.0 Pro(32K): $0.50 & $1.50", "gemini-1.0-pro", "32000")
            ],
            "Meta": [
                ("Llama 3.2 2.0 GB: Local", "llama3.2", "8096"),
                ("Llama 3.2 43.0 GB: Local", "llama3.3", "8096")

            ],
            "DeepSeek": [
                ("DeepSeek-R1 4.7 GB: Local", "deepseek-r1", "64000")
            ]            
        }
        self.settings = ""
        self.settings = QtCore.QSettings("node-editorDisplay", "NodeEditorDisplay")
        self.restore_last_state()

    def select_models(self):
        selLLM = SelectedLLM()
        dialog = QDialog()
        dialog.setWindowTitle("Select Model")
        dialog.setWindowIcon(QtGui.QIcon("resources\\ai.jpg"))
        
        layout = QGridLayout()
        company_label = QLabel("LLM Family")
        model_label = QLabel("LLM Model")
        model_label_details = QLabel("Model(Context Window): Input Price & Output Price (Per 1M tokens)")
        company_combo = QComboBox()
        company_combo.addItems(self.llm_companies)
        model_combo = QComboBox()
        label_disclaimer = QLabel("CONCEPTUAL PROOF OF CONCEPT")
        label_warning = QLabel("This is a proof of concept and has not been approved for official use")

        layout.addWidget(company_label, 0, 0)
        layout.addWidget(company_combo, 0, 1)
        layout.addWidget(model_label_details, 1, 1)        
        layout.addWidget(model_label, 2, 0)
        layout.addWidget(model_combo, 2, 1)
        layout.addWidget(label_disclaimer, 4, 0, 1, 2)
        layout.addWidget(label_warning, 5, 0, 1, 2)


        def on_company_change(index):
            model_combo.clear()
            model_combo.addItems([item[0] for item in self.llm_models[self.llm_companies[index]]])
            model_combo.setCurrentIndex(0)  # Set to the first model by default

        company_combo.currentIndexChanged.connect(on_company_change)
        on_company_change(0)  # Trigger initial model population

        def on_select():
            selLLM.selected_company = company_combo.currentText()
            selLLM.selected_model = model_combo.currentText()
            # Find the selected model's information and store it
            for model_info in self.llm_models[selLLM.selected_company]:
                if model_info[0] == selLLM.selected_model:  # Compare full model names
                    selLLM.available_llms = [model_info]  # Store it as a single-item list
                    selLLM.selected_model = str(model_info[1])
                    break
            dialog.accept()

        select_button = QPushButton("Select")
        select_button.setStyleSheet("background-color: green; color: white;")
        select_button.clicked.connect(on_select)
        layout.addWidget(select_button, 3, 1)  # Span across 2 columns
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.Rejected:
            print("No model selected, exiting.")
            QMessageBox()            
            sys.exit()

    def restore_last_state(self):
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
            s = self.settings.value("splitterSize")
            self.splitter.restoreState(s)

    def closeEvent(self, event):
        """
        Handles the close event by saving the GUI state and closing the application.
        Args:
            event: Close event.
        Returns:
            None.
        """
        # debugging lets save the scene:
        # self.node_widget.save_project("C:/Users/Howard/simple-node-editor/Example_Project/test.json")        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)

# Example usage
if __name__ == "__main__":
    import qdarktheme    
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    model_selection = ModelSelection()
    model_selection.select_models()
    sLLM = SelectedLLM()
    print(f"selected_company(global):", sLLM.selected_company)
    print(f"selected_model(global):", sLLM.selected_model)
    print(f"available_llms(global):", sLLM.available_llms)
