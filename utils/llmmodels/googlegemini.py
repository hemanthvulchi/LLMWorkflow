import google.generativeai as genai
from utils.vectordb import VectorDB
import os


class GoogleGeminiConnection:
    def __init__(self, model):
        #GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "AIzaSyCRQ-q8rvENUrHvgXxmWA2lwJO6zJ-dVKI"))
        # self.chatOn="ON"
        self.gemini_model = genai.GenerativeModel(model)
        # if self.chatOn == "ON":
        #     self.chat = self.gemini_model.start_chat(history=[])

    def get_connection(self):
        return self.connection

    def call_prompt(self,p_user_prompt,p_system_prompt="", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt="",embeddings = False):
        safety_settings = [{"category":"HARM_CATEGORY_DEROGATORY","threshold":4},{"category":"HARM_CATEGORY_TOXICITY","threshold":4},{"category":"HARM_CATEGORY_VIOLENCE","threshold":4},{"category":"HARM_CATEGORY_SEXUAL","threshold":4},{"category":"HARM_CATEGORY_MEDICAL","threshold":4},{"category":"HARM_CATEGORY_DANGEROUS","threshold":4}]
        request = ""
        input_str = str(p_system_prompt) + "\n" + str(p_user_prompt)
        # Query the ChromaDB vector database for relevant context
        if embeddings:
            db = VectorDB()
            context = db.query_db_StringContext(p_user_prompt)
        else:
            context = ""
        response = self.gemini_model.generate_content(input_str + "\n" + context) 
        if response.text:
            return response.text
        else:
            return "Error In Response"

    def initiate_assistant(self,p_name, p_instructions):
        self.chatOn="ON"
        self.chat = self.gemini_model.start_chat(history=[])
        self.chat.send_message(p_instructions)

    def call_assistant(self,p_user_prompt, p_maximum_tokens=256, p_temparature=1,p_top_p=1,embeddings = False):
        if embeddings:
            db = VectorDB()
            context = db.query_db_StringContext(p_user_prompt)
        else:
            context = ""
        response = self.chat.send_message(p_user_prompt + "\n" + context)
        if response.text:
            return response.text
        else:
            return "Error In Response"


