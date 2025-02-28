#from utils.llmconnection import LLMConnection
from utils.vectordb import VectorDB
import requests
import json


class LLamaConnection:
    def __init__(self, model):
        self.selected_model = model
        self.OLLAMA_URL = "http://localhost:11434/api/generate"
        self.chat_history = []

    def get_connection(self):
        return self.connection

    def call_prompt(self,p_user_prompt,p_system_prompt="", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt="",embeddings = False):
        request = ""
        input_str = str(p_system_prompt) + "\n" + str(p_user_prompt)
        # Query the ChromaDB vector database for relevant context
        if embeddings:
            db = VectorDB()
            context = db.query_db_StringContext(p_user_prompt)
        else:
            context = ""

        chat_input = input_str + "\n" + context

        payload = {
            "model": self.selected_model,  # Ensure this matches your running model
            "prompt": chat_input,
            "stream": False
        }
        response = requests.post(self.OLLAMA_URL, data=json.dumps(payload))
        # Parse the response
        if response.status_code == 200:
            result = response.json()
            print("LLaMA 3 Response:", result.get("response", "No response"))
            return result.get("response", "No response")
        else:
            print("Error:", response.status_code, response.text)
            return "Error In Response"
        

    def initiate_assistant(self,p_name, p_instructions):
        self.chatOn="ON"
        self.chat_history = []
        self.chat_history.append({"role": "user", "content": p_instructions})


    def call_assistant(self,p_user_prompt, p_maximum_tokens=256, p_temparature=1,p_top_p=1,embeddings = False):
        request = ""
        # Query the ChromaDB vector database for relevant context
        if embeddings:
            db = VectorDB()
            context = db.query_db_StringContext(p_user_prompt)
        else:
            context = ""

        chat_input = p_user_prompt + "\n" + context

        self.chat_history.append({"role": "user", "content": chat_input})

        # Create a formatted prompt including chat history
        formatted_prompt = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.chat_history
        )

        payload = {
            "model": self.selected_model,  # Ensure this matches your running model
            "prompt": formatted_prompt,
            "stream": False
        }
        response = requests.post(self.OLLAMA_URL, data=json.dumps(payload))
        # Parse the response
        if response.status_code == 200:
            result = response.json()
            results_txt = result.get("response", "No response")
            print("LLaMA 3 Response:", results_txt)
            self.chat_history.append({"role": "assistant", "content": results_txt})
            return results_txt
        else:
            print("Error:", response.status_code, response.text)
            return "Error In Response"

