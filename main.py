"""
A simple Node Editor application that allows the user to create, modify and connect nodes of various types.

The application consists of a main window that contains a splitter with a Node List and a Node Widget. The Node List
shows a list of available node types, while the Node Widget is where the user can create, edit and connect nodes.

This application uses PySide6 as a GUI toolkit.

Author: Bryan Howard
Repo: https://github.com/bhowiebkr/simple-node-editor
"""

import logging
from pathlib import Path
import importlib
import inspect
import chromadb
import os
import shutil
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from PySide6 import QtCore, QtGui, QtWidgets
import qdarktheme

from core.gui.node_list import NodeList
from core.gui.node_widget import NodeWidget
from utils.display import Display
from utils.datamodels import ModelSelection, SelectedLLM
from customnodes.common_widgets.ConfigDialog import ConfigDialog
from utils.llmconnection import LLMConnection
from utils.vectordb import VectorDB
from customnodes.Aggregate_Node import Aggregate_Node
from customnodes.Combine_Node import Combine_Node
from customnodes.ExcelAdvancedProcess_Node import ExcelAdvancedProcess_Node
from customnodes.AI_Prompt import AIPrompt_Node
from customnodes.Chat_Node import Chat_Node
from customnodes.PowerPointAdvanced_Node import PowerPointAdvanced_Node
from customnodes.OutputViewer_Node import OutputViewer_Node
from customnodes.TextInput_Node import TextInput_Node
from customnodes.TextEdit_Node import TextEdit_Node
from customnodes.FileExtract_Node import FileExtract_Node
from customnodes.AIPromptInput_Node import AI_Prompt_Input_Node
from customnodes.Test_Node import Test_Node
from customnodes.AI_Prompt_v2 import AIPrompt_Node2
import utils.themecolors as colors
import utils.directory as directory

#logging.basicConfig(level=logging.DEBUG)


class MainWindow(QtWidgets.QMainWindow):
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = None
        self.project_path = None
        self.imports = None  # we will store the project import node types here for now.

        self.setWindowTitle("Visual Prompt Engineering")
        self.settings = QtCore.QSettings("node-editor", "NodeEditor")

        self.init_menu()
        self.init_ui()
        self.load_initial_project()
        self.restore_last_state()

    def init_menu(self):
        # Create a "File" menu and add actions to it
        file_menu = QtWidgets.QMenu("File", self)
        self.menuBar().addMenu(file_menu)

        load_action = QtGui.QAction("Load Project", self)
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        # Create a "Reference Files (RAG)" menu and add actions to it
        reference_menu = QtWidgets.QMenu("Reference Files (RAG)", self)
        self.menuBar().addMenu(reference_menu)
        
        refreshDB_action = QtGui.QAction("Refresh Database", self)
        refreshDB_action.triggered.connect(self.update_vectorDB)
        reference_menu.addAction(refreshDB_action)

        listFilesDB_action = QtGui.QAction("List files", self)
        listFilesDB_action.triggered.connect(self.get_filelist_vectorDB)
        reference_menu.addAction(listFilesDB_action)

        addFilesDB_action = QtGui.QAction("Add files to database", self)
        addFilesDB_action.triggered.connect(self.add_files_vectorDb)
        reference_menu.addAction(addFilesDB_action)

        about_menu = QtWidgets.QMenu("About tool", self)
        self.menuBar().addMenu(about_menu)
        
        showAbout_action = QtGui.QAction("About", self)
        showAbout_action.triggered.connect(self.show_about_tool)
        about_menu.addAction(showAbout_action)

    def init_ui(self):
        # Create main layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)

        #Create left layout
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_layout)
        
        # Create splitter 
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        
        #Create parts of left layout
        self.init_ui_nodeGroupBox()
        self.init_ui_modelGroupBox()
        self.init_ui_ragGroupBox()

        left_layout.addWidget(self.nodeGroupBox)
        left_layout.addWidget(self.ragGroupBox)
        left_layout.addWidget(self.modelGroupBox)
        
        #self.bottom_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        #left_layout.addItem(self.bottom_spacer)  
               
        main_layout.addWidget(self.splitter)

    def init_ui_nodeGroupBox(self):
        self.nodeGroupBox = self.create_external_group_box("Nodes",colors.get_color_hex("brightborder"))
        self.init_node_lists()
        left_node_layout = QtWidgets.QVBoxLayout()
        custom_font = QtGui.QFont()
        custom_font.setItalic(True)
        self.nodes_label = self.create_label("To start, drag the nodes into the editor (to the right)",custom_font)                
        left_node_layout.addWidget(self.nodes_label,1)
        left_node_layout.addWidget(self.input_nodes_group,6)
        left_node_layout.addWidget(self.transform_nodes_group,10)
        left_node_layout.addWidget(self.output_nodes_group,6)
        self.nodeGroupBox.setLayout(left_node_layout)

    def init_ui_modelGroupBox(self):
        self.modelGroupBox = self.create_external_group_box("Selected Model",colors.get_color_hex("brightborder"))
        custom_font = QtGui.QFont()
        custom_font.setBold(True)
        #self.connection_label = self.create_label("Selected LLM", custom_font)
        #self.model_label = self.create_label("Selected Model", custom_font)
        self.connectionText = self.create_text_edit()
        self.modelText = self.create_text_edit()
        left_model_layout = QtWidgets.QVBoxLayout()        
        left_model_layout.addWidget(self.connectionText)
        left_model_layout.addWidget(self.modelText)
        self.modelGroupBox.setLayout(left_model_layout)
        self.modelGroupBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def init_ui_ragGroupBox(self):
        self.ragGroupBox = self.create_external_group_box("RAG (Document Database)",colors.get_color_hex("brightborder"))
        rag_layout = QtWidgets.QVBoxLayout()
        custom_font = QtGui.QFont()
        custom_font.setItalic(True)
        rag_info_label = self.create_label("Files added to the document database can be searched",custom_font)
        rag_layout.addWidget(rag_info_label)

      

        rag_add_button = QtWidgets.QPushButton()
        rag_add_button.setText("Add files and update document database")
        rag_add_button.setStyleSheet("QPushButton { font-weight: bold; }")
        rag_add_button.clicked.connect(self.add_files_vectorDb)
        rag_layout.addWidget(rag_add_button)

        # rag_button = QtWidgets.QPushButton("Show Files List")
        # rag_button.setStyleSheet("QPushButton { font-weight: bold; }")
        # rag_button.clicked.connect(self.get_filelist_vectorDB)
        # rag_layout.addWidget(rag_button)                

        rag_refresh_button = QtWidgets.QPushButton()
        rag_refresh_button.setText("Refresh document database")
        rag_refresh_button.setStyleSheet("QPushButton { font-weight: bold; }")
        rag_refresh_button.clicked.connect(self.update_vectorDB)
        rag_layout.addWidget(rag_refresh_button)

        #Adding no of files display
        rag_line_layout = QtWidgets.QHBoxLayout()
        no_of_files_label = QtWidgets.QLabel("No of files indexed in document database:")
        rag_line_layout.addWidget(no_of_files_label)
        self.rag_no_files_lineedit = QtWidgets.QLineEdit()
        self.rag_no_files_lineedit.setReadOnly(True)
        rag_line_layout.addWidget(self.rag_no_files_lineedit)
        rag_layout.addLayout(rag_line_layout)  


        self.ragGroupBox.setLayout(rag_layout)        


    def init_node_lists(self):
        # Initialize node lists with styles
        self.input_node_list = NodeList(self)
        self.transform_node_list = NodeList(self)
        self.output_node_list = NodeList(self)

        self.input_node_list.setStyleSheet(self.get_node_list_style(colors.get_color_hex("input")))
        self.transform_node_list.setStyleSheet(self.get_node_list_style(colors.get_color_hex("transform")))
        self.output_node_list.setStyleSheet(self.get_node_list_style(colors.get_color_hex("output")))

        # Create groups with headers
        self.input_nodes_group = self.create_group_box("Input Nodes", self.input_node_list, colors.get_color_hex("input"))
        self.transform_nodes_group = self.create_group_box("Transform Nodes",self.transform_node_list, colors.get_color_hex("transform"))
        self.output_nodes_group = self.create_group_box("Output Nodes", self.output_node_list, colors.get_color_hex("output"))


    def create_label(self, text, font = "", color=None):
        label = QtWidgets.QLabel(text)
        if not(font==""):
            label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        if color:
            label.setStyleSheet(f"""
                background-color: {color}; 
                color: white;               
                border: 2px solid {color};  
                border-radius: 10px;        
                padding: 10px;                             
            """)
        return label

    def create_text_edit(self):
        text_edit = QtWidgets.QTextEdit()
        text_edit.setPlainText("TBD")
        text_edit.setFixedHeight(30)
        text_edit.setStyleSheet("""
            QTextEdit{
            background: rgb(100, 100, 100); 
            }
        """)
        text_edit.setReadOnly(True)
        return text_edit

    def get_node_list_style(self, color):
        return f"""
                QListWidget {{
                    background: rgb(25, 25, 25);
                    color: white;               
                    border: 2px solid color;         
                    padding: 10px;             
                }}

                QListWidget::item {{
                    border: 1px solid {colors.get_color_hex('dark')};
                    background: {color};
                    margin: 2px;
                    padding: 2px;
                    border-radius: 5px;   
                    height: 20px;         
                }}
                """
    def create_external_group_box(self, title, color):
        group_box = QtWidgets.QGroupBox(title)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {color};
                border-radius: 5px;
                margin-top: 10px; /* Optional spacing adjustment */
            }}
            QGroupBox::title {{
                color: {color};
                subcontrol-origin: margin;
                subcontrol-position: top left; 
                padding: 0 3px;
                font-size: 30px; /* Adjust as needed */
            }}
        """)
        return group_box

    def create_group_box(self, title, widget, color):
        group_box = QtWidgets.QGroupBox(title)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {colors.get_color_hex('border')};
                border-radius: 5px;
                margin-top: 5px;
            }}
            QGroupBox::title {{
                color: white;
                subcontrol-origin: margin;
                subcontrol-position: top left; 
                padding: 0 3px;
                font-size: 16px;
                font-weight: bold;
                text-decoration: underline;
            }}
        """)

        layout = QtWidgets.QVBoxLayout()
        if widget:
            layout.addWidget(widget)
        group_box.setLayout(layout)
        return group_box


    def load_initial_project(self):
        load_project_path = (Path(__file__).parent.resolve())
        self.load_project_classes(load_project_path)

    def restore_last_state(self):
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
            s = self.settings.value("splitterSize")
            self.splitter.restoreState(s)


    def setLLM(self,textLLM):
        self.connectionText.setPlainText(textLLM)

    def setModel(self,textModel):
        self.modelText.setPlainText(textModel)

    def setRAGNo(self,numberOfFiles):
        self.rag_no_files_lineedit.text = numberOfFiles

    def save_project(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_path, _ = file_dialog.getSaveFileName(filter="JSON files (*.json)")
        if file_path:
            self.node_widget.save_project(file_path)

    def load_project_classes(self,project_path=None):
        # Preloaded classes
        self.imports = {}
        self.input_imports = {}
        self.transform_imports = {}
        self.output_imports = {}
        self.input_imports['TextInput_Node'] = {"label":"Text Input","class": TextInput_Node, "module": TextInput_Node.__module__,"image":'textinput'}
        self.input_imports['AIPrompt_Node'] = {"label":"AI Prompt","class": AIPrompt_Node, "module": AIPrompt_Node.__module__,"image":'assistant'}
        self.input_imports['AIPrompt_Node2'] = {"label":"AI Prompt2","class": AIPrompt_Node2, "module": AIPrompt_Node2.__module__,"image":'assistant'}
        self.input_imports['FileExtract_Node'] = {"label":"Extract File","class": FileExtract_Node, "module": FileExtract_Node.__module__,"image":'fileextract'}
        self.transform_imports['TextEdit_Node'] = {"label":"Edit Text","class": TextEdit_Node, "module": TextEdit_Node.__module__,"image":'simpletransform'}        
        self.transform_imports['Combine_Node'] = {"label":"Combine Text","class": Combine_Node, "module": Combine_Node.__module__,"image":'combine'}
        self.transform_imports['AI_Prompt_Input_Node'] = {"label":"AI Prompt (with input)","class": AI_Prompt_Input_Node, "module": AI_Prompt_Input_Node.__module__,"image":'assistant'}
        self.transform_imports['Aggregate_Node'] = {"label":"AI Prompt (mutiple inputs)","class": Aggregate_Node, "module": Aggregate_Node.__module__,"image":'merge'}
        self.output_imports['ExcelAdvancedProcess_Node'] = {"label":"Excel Interface","class": ExcelAdvancedProcess_Node, "module": ExcelAdvancedProcess_Node.__module__,"image":'excel'}
        self.output_imports['PowerPointAdvanced_Node'] = {"label":"PowerPoint Interface","class": PowerPointAdvanced_Node, "module": PowerPointAdvanced_Node.__module__,"image":'powerpoint'}
        self.output_imports['OutputViewer_Node'] = {"label":"View Output","class": OutputViewer_Node, "module": OutputViewer_Node.__module__,"image":'outputviewer'}
        self.output_imports['Test_Node'] = {"label":"Chat with AI","class": Test_Node, "module": Test_Node.__module__,"image":'assistant'}        

        # Update project with the preloaded classes
        self.input_node_list.update_project(self.input_imports)
        self.transform_node_list.update_project(self.transform_imports)
        self.output_node_list.update_project(self.output_imports)
        self.imports.update(self.input_imports)
        self.imports.update(self.transform_imports)
        self.imports.update(self.output_imports)
        #old code, where it would dynamically import the classes
            # for file in project_path.glob("*.py"):

            #     if not file.stem.endswith('_node'):
            #         print('file:', file.stem)
            #         continue
            #     spec = importlib.util.spec_from_file_location(file.stem, file)
            #     module = importlib.util.module_from_spec(spec)
            #     spec.loader.exec_module(module)

            #     for name, obj in inspect.getmembers(module):
            #         if not name.endswith('_Node'):
            #             continue
            #         if inspect.isclass(obj):
            #             self.imports[obj.__name__] = {"class": obj, "module": module}
            #             #break

        #self.node_list.update_project(self.imports)

        # work on just the first json file. add the ablitity to work on multiple json files later
        for json_path in project_path.glob("*.json"):
            self.node_widget.load_scene(json_path, self.imports)
            break

    def load_project(self):
        json_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select JSON File", "", "JSON Files (*.json)"
        )
        if json_path:
            self.node_widget.load_scene(json_path, self.imports)

    def update_vectorDB(self):
        vDB = VectorDB()
        response = vDB.update_db()
        noOfFiles = vDB.get_count_files_in_list_db()
        self.set_rag_no_files_lineedit(noOfFiles)
        Display.show_message_box( "Success", "Document database refreshed\n " + str(response))

    
    def add_files_vectorDb(self):
        # Open the dialog to select multiple files
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)  
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()

            # Get the destination folder (Documents)
            documents_folder = directory.check_documents_directory()

            # Copy the selected files to the Documents folder
            for file_path in selected_files:
                try:
                    shutil.copy2(file_path, documents_folder)  # copy2 preserves metadata
                except Exception as e:
                    # Handle potential errors (e.g., file already exists, permissions)
                    QtWidgets.QMessageBox.critical(None, "Error", f"Failed to copy {file_path}: {e}")
            self.update_vectorDB()
        
        
    def open_document_directory(self):
        directory.open_document_directory()

    def get_filelist_vectorDB(self):
        vDB = VectorDB()
        file_list = vDB.get_filelist_db()
        Display.show_message_box("Files in RAG","List of files currently indexed and that can be searched:\n " + str(file_list))

    def show_about_tool(self):
        Display.show_message_box(f"Visual Prompt Engineering","This is a conceptual prototype built to assist practitioners in "
                                 "automating business tasks by tactically structuring data for easy processing by AI. "
                                 "It provides an embedded interface with office documents like PowerPoint and Excel."
                                 "\n\nVersion: Ahhhhhhhhhhhhhhhhh :@")

    def set_rag_no_files_lineedit(self,noOfFiles):
        self.rag_no_files_lineedit.setText(str(noOfFiles))

    def closeEvent(self, event):
        """
        Handles the close event by saving the GUI state and closing the application.

        Args:
            event: Close event.

        Returns:
            None.
        """

        # debugging lets save the scene:
        # self.node_widget.save_project("C:/Users/Howard/simple-node-editor/Example_Project/test.json")

        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    import sys
    import qdarktheme
    import traceback
    try:
        app = QtWidgets.QApplication(sys.argv)
        model_selection = ModelSelection()
        model_selection.select_models()        
        app.setWindowIcon(QtGui.QIcon("resources\\ai.jpg"))
        qdarktheme.setup_theme()
        print("Setting up environment for database")
        print("Set ChromaDB client")
        vDB = VectorDB()
        noOfFiles = vDB.get_count_files_in_list_db()
        print("Initialized ChromaDB")
        launcher = MainWindow()
        sLLM = SelectedLLM()
        launcher.set_rag_no_files_lineedit(noOfFiles)
        print("Initiated Main Window")
        launcher.setLLM(sLLM.selected_company)
        launcher.setModel(sLLM.selected_model)
        launcher.show()
        app.exec()
    except Exception as e:
        print("Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
        Display.show_error_box( "Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
    sys.exit()