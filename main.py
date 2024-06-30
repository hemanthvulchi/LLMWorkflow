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
from customnodes.Input_Node import Input_Node
from customnodes.Chat_Node import Chat_Node
from customnodes.PowerPointAdvanced_Node import PowerPointAdvanced_Node
from customnodes.OutputViewer_Node import OutputViewer_Node
from customnodes.SimpleInput_Node import SimpleInput_Node
from customnodes.SimpleTransform_Node import SimpleTransform_Node
from customnodes.FileExtract_Node import FileExtract_Node
from customnodes.TransformLLM_Node import TransformLLM_Node
from customnodes.Test_Node import Test_Node
import utils.themecolors as colors

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
        load_action.triggered.connect(self.get_project_path)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        # Create a "Reference Files (RAG)" menu and add actions to it
        reference_menu = QtWidgets.QMenu("Reference Files (RAG)", self)
        self.menuBar().addMenu(reference_menu)
        
        updateDB_action = QtGui.QAction("Update Database", self)
        updateDB_action.triggered.connect(self.update_vectorDB)
        reference_menu.addAction(updateDB_action)

    def init_ui(self):
        # Layouts
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        self.init_connection_widgets()
        self.init_labels()
        self.init_node_lists()
        
        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)

        self.init_ui_nodeGroupBox()
        self.init_ui_modelGroupBox()
        self.init_ui_ragGroupBox()

        left_layout.addWidget(self.nodeGroupBox)
        left_layout.addWidget(self.modelGroupBox)
        left_layout.addWidget(self.ragGroupBox)
        #left_layout.addItem(self.bottom_spacer)  
        #               
        main_layout.addWidget(self.splitter)

    def init_ui_nodeGroupBox(self):
        self.nodeGroupBox = self.create_external_group_box("Nodes",colors.get_color_hex("brightborder"))
        left_node_layout = QtWidgets.QVBoxLayout()
        left_node_layout.addWidget(self.nodes_label)
        left_node_layout.addWidget(self.input_nodes_group)
        left_node_layout.addWidget(self.transform_nodes_group)
        left_node_layout.addWidget(self.output_nodes_group)
        self.nodeGroupBox.setLayout(left_node_layout)

    def init_ui_modelGroupBox(self):
        self.modelGroupBox = self.create_external_group_box("Selected Model",colors.get_color_hex("brightborder"))
        left_model_layout = QtWidgets.QVBoxLayout()        
        left_model_layout.addWidget(self.connectionText)
        left_model_layout.addWidget(self.modelText)
        self.modelGroupBox.setLayout(left_model_layout)
        self.modelGroupBox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def init_ui_ragGroupBox(self):
        self.ragGroupBox = self.create_external_group_box("RAG (Document Database)",colors.get_color_hex("brightborder"))
        rag_layout = QtWidgets.QVBoxLayout()
        rag_line_layout = QtWidgets.QHBoxLayout()
        no_of_files_label = QtWidgets.QLabel("No of files indexed in RAG:")
        rag_line_layout.addWidget(no_of_files_label)
        self.rag_no_files_lineedit = QtWidgets.QLineEdit()
        self.rag_no_files_lineedit.setReadOnly(True)
        rag_line_layout.addWidget(self.rag_no_files_lineedit)
        rag_layout.addLayout(rag_line_layout)        
        rag_button = QtWidgets.QPushButton("Show Files List")
        rag_button.setStyleSheet("QPushButton { font-weight: bold; }")
        rag_button.clicked.connect(self.get_filelist_vectorDB)
        rag_layout.addWidget(rag_button)
        self.ragGroupBox.setLayout(rag_layout)        

    def init_connection_widgets(self):
        # Initialize connection text widgets with styles
        self.connectionText = self.create_text_edit()
        self.modelText = self.create_text_edit()

    def init_labels(self):
        # Initialize labels with styles
        custom_font = QtGui.QFont()
        custom_font.setBold(True)
        self.connection_label = self.create_label("Selected LLM", custom_font)
        self.model_label = self.create_label("Selected Model", custom_font)
        custom_font = QtGui.QFont()
        custom_font.setBold(False)
        custom_font.setItalic(True)
        self.nodes_label = self.create_label("Drag and drop below nodes", custom_font)
        self.bottom_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)


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


    def create_label(self, text, font, color=None):
        label = QtWidgets.QLabel(text)
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
                color: {color};
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
        self.load_project(load_project_path)

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

    def load_project(self,project_path=None):
        # Preloaded classes
        self.imports = {}
        self.input_imports = {}
        self.transform_imports = {}
        self.output_imports = {}
        self.input_imports['SimpleInput_Node'] = {"class": SimpleInput_Node, "module": SimpleInput_Node.__module__}
        self.input_imports['Input_Node'] = {"class": Input_Node, "module": Input_Node.__module__}
        self.input_imports['FileExtract_Node'] = {"class": FileExtract_Node, "module": FileExtract_Node.__module__}
        self.transform_imports['SimpleTransform_Node'] = {"class": SimpleTransform_Node, "module": SimpleTransform_Node.__module__}        
        self.transform_imports['Combine_Node'] = {"class": Combine_Node, "module": Combine_Node.__module__}
        self.transform_imports['TransformLLM_Node'] = {"class": TransformLLM_Node, "module": TransformLLM_Node.__module__}
        self.transform_imports['Aggregate_Node'] = {"class": Aggregate_Node, "module": Aggregate_Node.__module__}
        self.transform_imports['Test_Node'] = {"class": Test_Node, "module": Test_Node.__module__}
        self.output_imports['ExcelAdvancedProcess_Node'] = {"class": ExcelAdvancedProcess_Node, "module": ExcelAdvancedProcess_Node.__module__}
        #self.output_imports['ExcelBasicProcess_Node'] = {"class": ExcelBasicProcess_Node, "module": ExcelBasicProcess_Node.__module__}
        #self.output_imports['PowerPoint_Node'] = {"class": PowerPoint_Node, "module": PowerPoint_Node.__module__}
        self.output_imports['PowerPointAdvanced_Node'] = {"class": PowerPointAdvanced_Node, "module": PowerPointAdvanced_Node.__module__}
        self.output_imports['OutputViewer_Node'] = {"class": OutputViewer_Node, "module": OutputViewer_Node.__module__}

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

    def get_project_path(self):
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


    def get_filelist_vectorDB(self):
        vDB = VectorDB()
        file_list = vDB.get_filelist_db()
        Display.show_message_box("Files in RAG","List of files currently indexed and that can be searched:\n " + str(file_list))

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
        print("Initiated NodeEditor")
        launcher.setLLM(sLLM.selected_company)
        launcher.setModel(sLLM.selected_model)
        launcher.show()
        app.exec()
    except Exception as e:
        print("Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
        Display.show_error_box( "Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
    sys.exit()