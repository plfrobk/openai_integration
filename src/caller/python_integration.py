from os import makedirs, path, listdir
from datetime import datetime
from json import dump, dumps, load
from tiktoken import get_encoding
from requests import post
from base64 import b64encode
import pypdfium2 as pdfium
from openai import OpenAI

class OpenAIPythonIntegration(OpenAI):
    """Custom class to create client with API key, get a response, and format it to save to JSON"""
    def __init__(self):
        self.apiKey = self.get_api_key()
        self.organizationId = self.get_organization_key()
    
        super().__init__(organization=self.organizationId, api_key=self.apiKey)

    def get_api_key(self, fileName='./local/API_KEY.txt'): #Put API key in virtual environment folder, e.g. local
        """Function to get the API key to use for authorization when opening client object"""
        try:
            with open(fileName, 'r', encoding='utf-8') as data:
                key = data.read().strip()
            return key
        except FileNotFoundError as e:
            print(f"Error: API key file not found! Full message: ${e}")
        
    def get_organization_key(self, fileName='./local/ORGANIZATION_KEY.txt'): #Put API key in virtual environment folder, e.g. local
        """Function to get the Organization key to use with the API key when opening client object"""
        try:
            with open(fileName, 'r', encoding='utf-8') as data:
                key = data.read().strip()
            return key
        except FileNotFoundError as e:
            print(f"Error: Organization key file not found! Full message: ${e}")

    def create_assistant(self, name, instructions, applicationName, assistantType='retrieval', apiURL = 'https://api.openai.com/v1/assistants', gptModel='gpt-4-1106-preview', mode='w', messageIndent=0):
        """Function to call the open AI API to create an assistant"""
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
            "OpenAI-Beta": "assistants=v1"
            }
        
        payload = {
            "model": gptModel,
            "name": name,
            "instructions": instructions,
            "tools": [
                {
                "type": assistantType
                }
            ]
        }

        response = post(apiURL, headers=header, json=payload)
        responseJSON = response.json()

        assistantId = responseJSON['id']
        assistantName = responseJSON['name']

        makedirs(path.dirname(f'./src/{applicationName}/data/assistant_config/'), exist_ok=True)
        
        with open(f'./src/{applicationName}/data/assistant_config/{assistantId}_{assistantName}.json', mode, encoding='utf-8') as outputFile:
            dump(responseJSON, outputFile, ensure_ascii=False, indent=messageIndent)

    def get_assistant_id(self, applicationName, assistantName):
        """Function to review the previously generated assistant json file configurations to return the ID associated"""
        configFiles = listdir(f'./src/{applicationName}/data/assistant_config/')
        assistantFiles = []

        for file in configFiles:
            if file.startswith('asst'):
                assistantFiles.append(file)
        
        for file in assistantFiles:
            with open(f'./src/{applicationName}/data/assistant_config/{file}', 'r') as data:
                config = load(data)
                name = config['name']
            
                if name == assistantName:
                    output = config['id']
        
        try:
            return output
        except UnboundLocalError:
            raise Exception('Error: Assistant does not exist by name entered.  Please check the application and assistant name or call the create assistant function.')
    
    def upload_file_to_assistant(self, fileName, applicationName, filePurpose='assistants', fileReadMode = 'rb'):
        """Function to directly upload a file to OpenAI"""

        with open(f'./src/{applicationName}/data/{fileName}', mode=fileReadMode) as fileToUpload:
            try:
                response = self.files.create(
                    file=fileToUpload,
                    purpose=filePurpose
                )
            
                print('Succcess! Response from OpenAI: ' + str(response))
            except Exception as e:
                print('Failure! Full error message: ' + str(e))
            
    def create_assistant_thread(self, assistantId, applicationName, apiURL = 'https://api.openai.com/v1/threads', mode='w', messageIndent=0):
        """Function to call the open AI API to create a thread"""
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
            "OpenAI-Beta": "assistants=v1"
            }
        
        payload = ''

        response = post(apiURL, headers=header, json=payload)
        responseJSON = response.json()

        threadId = responseJSON['id']
        createdDate = responseJSON['created_at']

        makedirs(path.dirname(f'./src/{applicationName}/data/assistant_config/'), exist_ok=True)
        
        with open(f'./src/{applicationName}/data/assistant_config/{threadId}_{createdDate}_{assistantId}.json', mode, encoding='utf-8') as outputFile:
            dump(responseJSON, outputFile, ensure_ascii=False, indent=messageIndent)

    def get_thread_id(self, assistantId, applicationName):
        """Function to review the previously generated thread json file configurations to return the ID associated"""
        configFiles = listdir(f'./src/{applicationName}/data/assistant_config/')
        threadFile = []

        for file in configFiles:
            if file.startswith('thread') and file.endswith(f'{assistantId}.json'):
                threadFile.append(file)
    
        with open(f'./src/{applicationName}/data/assistant_config/{threadFile[0]}', 'r') as data:
            config = load(data)
            output = config['id']
            
        try:
            return output
        except UnboundLocalError:
            raise Exception('Error: Thread does not exist for assistant.  Please check the assistant ID or application name or call the create thread function.')