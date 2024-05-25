from dotenv import load_dotenv
from openai import OpenAI
import time
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
        #self._connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-NmNJZ8iMHOfzeHYTYEyuT3BlbkFJJP8yWQEXoPrgCEh3hFBy"))
        self._connection= OpenAI()
        print("OpenAI connection created")
        
    def get_connection(self):
        return self._connection
    
class LLMConnection():
    def __init__(self):
        self.connection = OpenAI()
        #self.connection= OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-NmNJZ8iMHOfzeHYTYEyuT3BlbkFJJP8yWQEXoPrgCEh3hFBy"))
        self.thread = None
        self.assistant = None
        self.delay = 0.1
        self.max_delay = 10

    def get_connection(self):
        return self.connection

    def call_prompt(self,p_user_prompt,p_system_prompt="",p_model="gpt-3.5-turbo-0125", p_maximum_tokens=256, p_temparature=1,p_top_p=1,p_assistant_prompt=""):
        response = self.connection.chat.completions.create(
            model=p_model,
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
        return response
    
    def initiate_assistant(self,p_name, p_instructions, p_model="gpt-3.5-turbo-0125"):
        if ((self.assistant is not None) or (self.thread is not None)):
            raise RuntimeError("Either assistant or thread is already instantiated. For using multiple assistants or threads," 
                                "direct retrieve connection to create an assistant directly")
        self.assistant = self.connection.beta.assistants.create(
            name=p_name,
            instructions=p_instructions,
            model=p_model
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


if __name__ == "__main__":
    con = LLMConnection()
    response = con.call_prompt("what is a tiger")
    print(response.choices[0].message.content)