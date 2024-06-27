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
from core.configdialog import ConfigDialog
from utils.llmconnection import LLMConnection
from utils.vectordb import VectorDB
from customnodes.Aggregate_Node import Aggregate_Node
from customnodes.Combine_Node import Combine_Node
from customnodes.ExcelAdvancedProcess_Node import ExcelAdvancedProcess_Node
from customnodes.ExcelBasicProcess_Node import ExcelBasicProcess_Node
from customnodes.Input_Node import Input_Node
from customnodes.Chat_Node import Chat_Node
from customnodes.PowerPoint_Node import PowerPoint_Node
from customnodes.PowerPointAdvanced_Node import PowerPointAdvanced_Node
from customnodes.OutputViewer_Node import OutputViewer_Node
from customnodes.SimpleInput_Node import SimpleInput_Node
from customnodes.SimpleTransform_Node import SimpleTransform_Node
from customnodes.FileExtract_Node import FileExtract_Node
from customnodes.TransformLLM_Node import TransformLLM_Node
import utils.themecolors as colors

#logging.basicConfig(level=logging.DEBUG)


class NodeEditor(QtWidgets.QMainWindow):
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = None
        self.project_path = None
        self.imports = None  # we will store the project import node types here for now.


        self.setWindowTitle("Visual Prompt Engineering")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # create a "File" menu and add an "Export CSV" action to it
        file_menu = QtWidgets.QMenu("File", self)
        self.menuBar().addMenu(file_menu)

        load_action = QtGui.QAction("Load Project", self)
        load_action.triggered.connect(self.get_project_path)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        reference_menu = QtWidgets.QMenu("Reference Files (RAG)", self)
        self.menuBar().addMenu(reference_menu)
        updateDB_action = QtGui.QAction("Update Database", self)
        updateDB_action.triggered.connect(self.update_vectorDB)
        reference_menu.addAction(updateDB_action)
        

        # Layouts
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        self.input_nodes_label = QtWidgets.QLabel("Input Nodes")
        self.input_node_list = NodeList(self)
        self.transform_nodes_label = QtWidgets.QLabel("Transform Nodes")
        self.transform_node_list = NodeList(self)
        self.output_nodes_label = QtWidgets.QLabel("Output Nodes")
        self.output_node_list = NodeList(self)
        self.connection_label = QtWidgets.QLabel("Selected LLM")
        self.connectionText = QtWidgets.QTextEdit()
        self.model_label = QtWidgets.QLabel("Selected Model")
        self.modelText = QtWidgets.QTextEdit()

        #SEt bold font
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.connection_label.setFont(bold_font)
        self.model_label.setFont(bold_font)
        self.input_nodes_label.setFont(bold_font)
        self.input_nodes_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.input_nodes_label.setStyleSheet(f"""
            background-color: {colors.get_color_hex('input')}; 
            color: white;               /* White text color */
            border: 2px solid {colors.get_color_hex('input')};  
            border-radius: 10px;        /* Rounded corners */
            padding: 10px;              /* Padding inside the label */
            """)        
        self.transform_nodes_label.setFont(bold_font)
        self.transform_nodes_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.transform_nodes_label.setStyleSheet(f"""
            background-color: {colors.get_color_hex('transform')}; 
            color: white;               /* White text color */
            border: 2px solid {colors.get_color_hex('transform')};  
            border-radius: 10px;        /* Rounded corners */
            padding: 10px;              /* Padding inside the label */
            """)        
        self.output_nodes_label.setFont(bold_font)
        self.output_nodes_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.output_nodes_label.setStyleSheet(f"""
            background-color: {colors.get_color_hex('output')};  
            color: white;               /* White text color */
            border: 2px solid {colors.get_color_hex('output')};  
            border-radius: 10px;        /* Rounded corners */
            padding: 10px;              /* Padding inside the label */
        """)        


        #Set background of node lists
        self.input_node_list.setStyleSheet(f"""
            background: rgb(50, 50, 50);
            color: white;               
            border: 2px solid {colors.get_color_hex("input")};         
            padding: 10px;             
            """)
        self.transform_node_list.setStyleSheet(f"""
            background: rgb(50, 50, 50);
            color: white;               
            border: 2px solid {colors.get_color_hex("transform")};  
            padding: 10px;             
            """)        
        self.output_node_list.setStyleSheet(f"""
            background: rgb(50, 50, 50);
            color: white;               
            border: 2px solid {colors.get_color_hex("output")};  
            padding: 10px;             
            """)        


        self.connectionText.setPlainText("TBD")
        self.connectionText.setFixedHeight(30)
        self.connectionText.setStyleSheet("""
        QTextEdit{
        background: rgb(100, 100, 100); /*background color */
        }
        """)
        self.connectionText.setReadOnly(True)

        self.modelText.setPlainText("TBD")
        self.modelText.setFixedHeight(30)
        self.modelText.setStyleSheet("""
        QTextEdit{
        background: rgb(100, 100, 100); /*background color */
        }
        """)
        self.modelText.setReadOnly(True)

        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.connection_label)
        left_layout.addWidget(self.connectionText)        
        left_layout.addWidget(self.model_label)
        left_layout.addWidget(self.modelText)           
        left_layout.addWidget(self.input_nodes_label)
        left_layout.addWidget(self.input_node_list)
        left_layout.addWidget(self.transform_nodes_label)
        left_layout.addWidget(self.transform_node_list)
        left_layout.addWidget(self.output_nodes_label)
        left_layout.addWidget(self.output_node_list)    
              
        main_layout.addWidget(self.splitter)

        # Load the example project | need to replace 
        #load_project_path = (Path(__file__).parent.resolve() / 'Example_project')
        load_project_path = (Path(__file__).parent.resolve())
        self.load_project(load_project_path)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def setLLM(self,textLLM):
        self.connectionText.setPlainText(textLLM)

    def setModel(self,textModel):
        self.modelText.setPlainText(textModel)

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
        self.transform_imports['Chat_Node'] = {"class": Chat_Node, "module": Chat_Node.__module__}
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
        vDB.update_db()

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
        print("Initialized ChromaDB")
        launcher = NodeEditor()
        sLLM = SelectedLLM()
        print("Initiated NodeEditor")
        launcher.setLLM(sLLM.selected_company)
        launcher.setModel(sLLM.selected_model)
        launcher.show()
        app.exec()
    except Exception as e:
        print("Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
        Display.show_error_box( "Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
    sys.exit()
