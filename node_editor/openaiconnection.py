from dotenv import load_dotenv
from openai import OpenAI
import os


#A singleton class to create the connection to OpenAI
class OpenAIConnection():
    _shared_state = {'_connection': None}
    def __init__(self):
        self.__dict__ = self._shared_state
        if self._connection is None:
            self._connect()

    def _connect(self):            
        load_dotenv()
        #self._connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-UxMLylZ1f72vq3JsxapDT3BlbkFJjx590JnDiLvEKvd4TTdi"))
        self._connection= OpenAI()
        print("OpenAI connection created")
        
    def get_connection(self):
        return self._connection
    
