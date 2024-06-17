from PySide6.QtWidgets import  QApplication
import google.generativeai as genai
from openai import OpenAI
from utils.datamodels import SelectedLLM, ModelSelection
from utils.vectordb import VectorDB
#from datamodels import SelectedLLM,ModelSelection
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
        
class OpenAIConnection:
    _shared_state = {'_connection': None}    
    def __init__(self,model):
        #self.connection = OpenAI()
        #self.connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-NmNJZ8iMHOfzeHYTYEyuT3BlbkFJJP8yWQEXoPrgCEh3hFBy"))
        self.__dict__ = self._shared_state
        if self._connection is None:
            self._connect()
        self.thread = None
        self.assistant = None
        self.delay = 0.1
        self.max_delay = 10
        self.selected_model = model

    def _connect(self):            
        load_dotenv()
        #self._connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-UxMLylZ1f72vq3JsxapDT3BlbkFJjx590JnDiLvEKvd4TTdi"))
        self._connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-NmNJZ8iMHOfzeHYTYEyuT3BlbkFJJP8yWQEXoPrgCEh3hFBy"))
        print("OpenAI connection created")

    def get_connection(self):
        return self._connection

    def call_prompt(self,p_user_prompt,p_system_prompt="", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt="",embeddings = False):
        if embeddings:
            db = VectorDB()
            context = db.query_db_StringContext(p_user_prompt)
        else: 
            context = ""
        print(context)
        response = self._connection.chat.completions.create(
            model=self.selected_model,
            messages=[
                {"role": "system", "content": p_system_prompt},
                {"role": "user", "content": context},
                {"role": "user", "content": p_user_prompt}
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
        self.assistant = self._connection.beta.assistants.create(
            name=p_name,
            instructions=p_instructions,
            model=self.selected_model
        )        
        self.thread = self._connection.beta.threads.create()


    def create_assistant2(self,p_name, p_instructions):
        # Define your target assistant
        target_assistant_name = p_name

        # Check for existing assistants
        assistants = self._connection.Assistant.list()

        matching_assistants = [a for a in assistants.data if a.name == target_assistant_name]

        if matching_assistants:
            assistant = matching_assistants[0]
            print(f"Found existing assistant: {assistant.name} (ID: {assistant.id})")
        else:
            try:
                assistant = self._connection.beta.assistants.create(
                    name=target_assistant_name,
                    instructions=p_instructions,
                    tools=[],
                    model=self.selected_model
                )
                print(f"Created new assistant: {assistant.name} (ID: {assistant.id})")
            except self._connection.error.OpenAIError as e:
                print(f"Error creating assistant: {e.http_status} - {e.error}")
                # Exit or handle the error appropriately in your application
        self.assistant = assistant
        # Create a thread with the assistant (same as before)
        thread = self._connection.beta.threads.create(
            messages=[
                {"role": "user", "content": "Hello, assistant!"}
            ]
        )

    def create_thread(self,p_name, p_instructions,p_user_prompt, p_maximum_tokens=4096, p_temparature=1,p_top_p=1):
        delay = self.delay
        customthread = self._connection.beta.threads.create()
        print(f"Thread '{p_name}' created successfully (ID: {customthread.id})")   
        if(self.assistant is None):
            self.assistant = self._connection.beta.assistants.create(
                name="Default Assistant",
                instructions=p_instructions,
                model=self.selected_model
            )        
        run = self._connection.beta.threads.runs.create(
            thread_id = customthread.id,
            assistant_id = self.assistant.id,
            max_prompt_tokens = p_maximum_tokens,
            temperature = p_temparature,
            top_p = p_top_p
        )

        while True:
            run_status = self._connection.beta.threads.runs.retrieve(
                thread_id=customthread.id,
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

        messages = self._connection.beta.threads.messages.list(
            thread_id=customthread.id
        )

        answer = messages.data[0].content[0].text.value
        print(f"Question: {p_user_prompt}")
        print(f"Answer: {answer}")
        print("-" * 20)

        return answer

    def call_assistant(self,p_user_prompt, p_maximum_tokens=256, p_temparature=1,p_top_p=1,embeddings = False):
        if ((self.assistant is None) or (self.thread is None)):
            raise NameError("Either assistant or thread not set. Please call initiate_assistant to initate parameters before calling call_assistant")        
        delay = self.delay
        message = self._connection.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=p_user_prompt
        )

        run = self._connection.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.assistant.id,
            max_prompt_tokens = p_maximum_tokens,
            temperature = p_temparature,
            top_p = p_top_p
        )

        while True:
            run_status = self._connection.beta.threads.runs.retrieve(
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

        messages = self._connection.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        answer = messages.data[0].content[0].text.value
        print(f"Question: {p_user_prompt}")
        print(f"Answer: {answer}")
        print("-" * 20)

        return answer

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model_selection = ModelSelection()
    model_selection.select_models()
    # The selected model will now be available in model_selection.selectedmodel
    con = LLMConnection()
    #response = con.call_prompt("what is a tiger")
    response = con.create_thread("HelpAst","What is a tiger","how about india")
    print(response)