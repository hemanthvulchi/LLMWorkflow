from PySide6.QtWidgets import  QApplication
from utils.datamodels import SelectedLLM, ModelSelection
from utils.llmmodels.openai import OpenAIConnection
from utils.llmmodels.googlegemini import GoogleGeminiConnection
from utils.llmmodels.ollama import LLamaConnection
from utils.llmmodels.deepseek import DeepSeekConnection
#from datamodels import SelectedLLM,ModelSelection
from dotenv import load_dotenv
import sys



class LLMConnection:
    def __init__(self):
        sLLM = SelectedLLM()
        load_dotenv()
        self.selected_company = sLLM.selected_company
        print("Selected_model:",self.selected_company)
        if self.selected_company == "OpenAI GPTs":
            self.connection = OpenAIConnection(sLLM.selected_model)  
        elif self.selected_company == "Google Gemini":
            self.connection = GoogleGeminiConnection(sLLM.selected_model)
        elif self.selected_company == "Meta":
            self.connection = LLamaConnection(sLLM.selected_model)            
        elif self.selected_company == "DeepSeek":
            self.connection = DeepSeekConnection(sLLM.selected_model)                       
        else:
            raise ValueError(f"Unsupported model: {self.selected_company}")

    #what is this code|| remove?
    def get_connection(self):
        return self.connection.get_connection()

    def call_prompt(self,p_user_prompt,p_system_prompt="", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt="",embeddings = False):
        return self.connection.call_prompt(p_user_prompt,p_system_prompt, p_maximum_tokens, p_temparature,p_top_p,p_assistant_prompt,embeddings)  
    
    def initiate_assistant(self, *args, **kwargs):
        return self.connection.initiate_assistant(*args, **kwargs)
    
    def create_thread(self, *args, **kwargs):
        if self.selected_company == "Google Gemini":
            raise NotImplementedError("This function is not available for google gemini")
        return self.connection.create_thread(*args, **kwargs)

    def call_assistant(self,p_user_prompt, p_maximum_tokens=256, p_temparature=1,p_top_p=1,embeddings = False):
        return self.connection.call_assistant(p_user_prompt, p_maximum_tokens, p_temparature,p_top_p,embeddings)    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    model_selection = ModelSelection()
    model_selection.select_models()
    # The selected model will now be available in model_selection.selectedmodel
    con = LLMConnection()
    #response = con.call_prompt("what is a tiger")
    response = con.create_thread("HelpAst","What is a tiger","how about india")
    print(response)