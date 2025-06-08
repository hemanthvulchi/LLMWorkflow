# Python GenAI Automated Workflow Editor

This tool provides a node based interface which allows for processing data using python and LLMs APIs. The intent of this project is to automate business processes, by funnenling data through nodes and allow them to be processed through LLM APIs.

This is my first dive into a major software project in a long time. I acknowledge its flaws and understand the need for improvement.

![image](https://github.com/user-attachments/assets/6cb58e99-7196-4ca9-8eae-bd86eb7de96a)


The engine is composed of three components, the node editor interface, LLM API connection classes and the nodes themselves which each perform specialized tasks.

1) The node editor presents an drag and drop interface to drop various elements and connect them. It has been modified to present a flexibile way of processing and transmitting data between different steps. 
2) The connection classes abstract away all the nuances of connecting to LLM APIs and allow the nodes to send the bare minimum to process the data (as of now it is limited to calling OpenAI chats and assistant APIs)
3) The nodes themselves do specialized tasks
   a) Simple Input: allows for directly adding/paste text, which can be transmitted to other nodes
   b) Combine Data: allows to combine incoming data and also send it to different nodes
   c) GenAI Input: allows you to enter data and have it processed by an LLM
   d) GenAI Aggregate: allows you to combine data and also have it processed at the same time
   e) Excel Assistant: allows you to take data from previous nodes for context and then extract questions from the Excel and to answer them directly in the Excel
   f) PowerPoint Assistant: allows you to take data from previous nodes for context and then extract questions from the PowerPoint and to answer them directly in the PowerPoint
4) There is also an integrated RAG in the tool using an ChromaDB.
5) The whole thing can be deployed as an exe file.
Need to add better error handling functions, dynamic workflow and a whole list of features

**References:**
The node editor interface is a heavily modified version of [project](https://github.com/bhowiebkr/python-node-editor) by bhowiebkr

Tool is mainly to demonstrate the art of the possible

"# GenAI" 
