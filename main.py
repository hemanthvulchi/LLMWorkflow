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
from utils.datamodels import ModelSelection
from core.configdialog import ConfigDialog
from utils.llmconnection import LLMConnection
from utils.vectordb import VectorDB
from WFPrompt_project.Aggregate_Node import Aggregate_Node
from WFPrompt_project.Combine_Node import Combine_Node
from WFPrompt_project.ExcelAdvancedProcess_Node import ExcelAdvancedProcess_Node
from WFPrompt_project.ExcelBasicProcess_Node import ExcelBasicProcess_Node
from WFPrompt_project.Input_Node import Input_Node
from WFPrompt_project.Chat_Node import Chat_Node
from WFPrompt_project.PowerPoint_Node import PowerPoint_Node
from WFPrompt_project.PowerPointAdvanced_Node import PowerPointAdvanced_Node
from WFPrompt_project.Print_Node import Print_Node
from WFPrompt_project.SimpleInput_Node import SimpleInput_Node
from WFPrompt_project.SimpleTransform_Node import SimpleTransform_Node

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

        reference_menu = QtWidgets.QMenu("Reference Files", self)
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
        self.node_list = NodeList(self)
        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
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

    def save_project(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("JSON files (*.json)")
        file_path, _ = file_dialog.getSaveFileName()
        self.node_widget.save_project(file_path)

    def load_project(self,project_path=None):
        # Preloaded classes
        self.imports = {}
        self.imports['Aggregate_Node'] = {"class": Aggregate_Node, "module": Aggregate_Node.__module__}
        self.imports['Combine_Node'] = {"class": Combine_Node, "module": Combine_Node.__module__}
        self.imports['ExcelAdvancedProcess_Node'] = {"class": ExcelAdvancedProcess_Node, "module": ExcelAdvancedProcess_Node.__module__}
        self.imports['ExcelBasicProcess_Node'] = {"class": ExcelBasicProcess_Node, "module": ExcelBasicProcess_Node.__module__}
        self.imports['Input_Node'] = {"class": Input_Node, "module": Input_Node.__module__}
        self.imports['Chat_Node'] = {"class": Chat_Node, "module": Chat_Node.__module__}
        self.imports['PowerPoint_Node'] = {"class": PowerPoint_Node, "module": PowerPoint_Node.__module__}
        self.imports['PowerPointAdvanced_Node'] = {"class": PowerPointAdvanced_Node, "module": PowerPointAdvanced_Node.__module__}
        self.imports['Print_Node'] = {"class": Print_Node, "module": Print_Node.__module__}
        self.imports['SimpleInput_Node'] = {"class": SimpleInput_Node, "module": SimpleInput_Node.__module__}
        self.imports['SimpleTransform_Node'] = {"class": SimpleTransform_Node, "module": SimpleTransform_Node.__module__}        

        # Update project with the preloaded classes
        self.node_list.update_project(self.imports)

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
        # client = chromadb.Client(
        #     settings=Settings(anonymized_telemetry=False),
        #     tenant=DEFAULT_TENANT,
        #     database=DEFAULT_DATABASE,
        # )
        print("Set ChromaDB client")
        vDB = VectorDB()
        print("Initialized ChromaDB")
        launcher = NodeEditor()
        print("Initiated NodeEditor")
        launcher.show()
        app.exec()
    except Exception as e:
        print("Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
        Display.show_error_box( "Error", f"Fatal failure!\nError: {str(e)}\n Detailed Description: {str(traceback.format_exc())}")
    sys.exit()
