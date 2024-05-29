from PySide6.QtWidgets import  QApplication
import google.generativeai as genai
from openai import OpenAI
from utils.datamodels import SelectedLLM, ModelSelection
from dotenv import load_dotenv
import os
import sys
import time

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
        else:
            raise ValueError(f"Unsupported model: {self.selected_company}")

    def get_connection(self):
        return self.connection.get_connection()

    def call_prompt(self, *args, **kwargs):
        return self.connection.call_prompt(*args, **kwargs)  
    
    def initiate_assistant(self, *args, **kwargs):
        if self.selected_company == "Google Gemini":
            raise NotImplementedError("This function is not available for google gemini")
        return self.connection.initiate_assistant(*args, **kwargs)
    
    def call_assistant(self, *args, **kwargs):
        if self.selected_company == "Google Gemini":
            raise NotImplementedError("This function is not available for google gemini")        
        return self.connection.call_assistant(*args, **kwargs)    
        
class OpenAIConnection:
    def __init__(self,model):
        self.connection = OpenAI()
        #self.connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-NmNJZ8iMHOfzeHYTYEyuT3BlbkFJJP8yWQEXoPrgCEh3hFBy"))
        self.thread = None
        self.assistant = None
        self.delay = 0.1
        self.max_delay = 10
        self.selected_model = model

    def get_connection(self):
        return self.connection

    def call_prompt(self,p_user_prompt,p_system_prompt="", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt=""):
        response = self.connection.chat.completions.create(
            model=self.selected_model,
            messages=[
                {
                    "role": "system",
                    "content": p_system_prompt
                },
                {
                    "role": "user",
                    "content": p_user_prompt
                }
            ],
            temperature=p_temparature,
            max_tokens=p_maximum_tokens,
            top_p=p_top_p
        )
        return response.choices[0].message.content
    
    def initiate_assistant(self,p_name, p_instructions):
        if ((self.assistant is not None) or (self.thread is not None)):
            raise RuntimeError("Either assistant or thread is already instantiated. For using multiple assistants or threads," 
                                "direct retrieve connection to create an assistant directly")
        self.assistant = self.connection.beta.assistants.create(
            name=p_name,
            instructions=p_instructions,
            model=self.selected_model
        )        
        self.thread = self.connection.beta.threads.create()


    def call_assistant(self,p_user_prompt, p_maximum_tokens=256, p_temparature=1,p_top_p=1):
        if ((self.assistant is None) or (self.thread is None)):
            raise NameError("Either assistant or thread not set. Please call initiate_assistant to initate parameters before calling call_assistant")        
        delay = self.delay
        message = self.connection.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=p_user_prompt
        )

        run = self.connection.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.assistant.id,
            max_prompt_tokens = p_maximum_tokens,
            temperature = p_temparature,
            top_p = p_top_p
        )

        while True:
            run_status = self.connection.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in  ["failed", "cancelled", "expired"]:  # Handle errors
                raise RuntimeError(f"Assistant run failed with status: {run_status.status}")
            else:
                print("Delaying by: ",delay,"seconds || Question:",p_user_prompt)
                time.sleep(delay)
                delay = delay * 1.5
                delay = min(delay, self.max_delay)

        messages = self.connection.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        answer = messages.data[0].content[0].text.value
        print(f"Question: {p_user_prompt}")
        print(f"Answer: {answer}")
        print("-" * 20)

        return answer

class GoogleGeminiConnection:
    def __init__(self, model):
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        self.chatOn="ON"
        self.gemini_model = genai.GenerativeModel(model)
        if self.chatOn == "ON":
            self.chat = self.gemini_model.start_chat(history=[])

    def get_connection(self):
        return self.connection

    def call_prompt(self,p_user_prompt,p_system_prompt="", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt=""):
        safety_settings = [{"category":"HARM_CATEGORY_DEROGATORY","threshold":4},{"category":"HARM_CATEGORY_TOXICITY","threshold":4},{"category":"HARM_CATEGORY_VIOLENCE","threshold":4},{"category":"HARM_CATEGORY_SEXUAL","threshold":4},{"category":"HARM_CATEGORY_MEDICAL","threshold":4},{"category":"HARM_CATEGORY_DANGEROUS","threshold":4}]
        request = ""
        input_str = str(p_system_prompt) + "\n" + str(p_user_prompt)
        if self.chatOn == "ON":
            response = self.chat.send_message(input_str)
        else:
            response = self.gemini_model.generate_content(input_str) 
        if response.text:
            return response.text
        else:
            return "Error In Response"
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model_selection = ModelSelection()
    model_selection.select_models()
    # The selected model will now be available in model_selection.selectedmodel
    con = LLMConnection()
    response = con.call_prompt("what is a tiger")
    print(response.choices[0].message.content)