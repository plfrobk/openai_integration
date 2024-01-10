from os import makedirs, path, listdir
from datetime import datetime
from json import dump, dumps, load
from tiktoken import get_encoding
from requests import post
from base64 import b64encode
import pypdfium2 as pdfium
from openai import OpenAI

class OpenAIPythonIntegration(OpenAI):
    """Custom class to utilize Python to directly work with OpenAI to do various functions"""
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

    def create_assistant(self, name, instructions, applicationName, metadata = '', assistantType='retrieval', gptModel='gpt-4-1106-preview', mode='w', messageIndent=0):
        """Function to directly use OpenAI to create an assistant"""

        assistantDict = {}
        assistant = self.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=gptModel,
            tools=[{"type": assistantType}],
            metadata=metadata
        ) 

        assistantDict['id'] = assistant.id
        assistantDict['name'] = assistant.name
        assistantDict['created_at'] = assistant.created_at
        assistantDict['model'] = assistant.model
        assistantDict['instructions'] = assistant.instructions
        assistantDict['type'] = assistant.tools[0].type
        assistantDict['metadata'] = assistant.metadata

        makedirs(path.dirname(f'./src/{applicationName}/config/'), exist_ok=True)
        
        with open(f'./src/{applicationName}/config/{assistant.id}_{assistant.name}.json', mode, encoding='utf-8') as outputFile:
            dump(assistantDict, outputFile, ensure_ascii=False, indent=messageIndent)

        print('Created assistant with id: ' + str(assistant.id))

    def get_assistant_id(self, applicationName, assistantName):
        """Function to review the previously generated assistant json file configurations to return the ID associated"""
        configFiles = listdir(f'./src/{applicationName}/config/')
        assistantFiles = []

        for file in configFiles:
            if file.startswith('asst'):
                assistantFiles.append(file)
        
        for file in assistantFiles:
            with open(f'./src/{applicationName}/config/{file}', 'r') as data:
                config = load(data)
                name = config['name']
            
                if name == assistantName:
                    assistantId = config['id']
                    print('Found existing assistant with id: ' + assistantId)
        
        try:
            return assistantId
        except UnboundLocalError:
            raise Exception('Error: Assistant does not exist by name entered.  Please check the application and assistant name or call the create assistant function.')
    
    def upload_file_to_assistant(self, fileName, applicationName, assistantId, filePurpose='assistants', fileReadMode = 'rb', fileWriteMode = 'w', messageIndent=0):
        """Function to directly upload a file to OpenAI"""
        fileUploadDict = {}

        with open(f'./src/{applicationName}/data/{fileName}', mode=fileReadMode) as fileToUpload:
            try:
                uploadResponse = self.files.create(
                    file=fileToUpload,
                    purpose=filePurpose
                )
            
                print('Succcess! File uploaded.')
            except Exception as e:
                print('Failure! Could not upload file, full error message: ' + str(e))
            else:
                try:
                    fileToAssistantResponse = self.beta.assistants.files.create(
                        assistant_id = assistantId,
                        file_id = uploadResponse.id
                    )
                
                    print('Succcess! File id associated with assistant: ' + str(fileToAssistantResponse.id))

                    fileUploadDict['id'] = fileToAssistantResponse.id
                    fileUploadDict['assistant_id'] = fileToAssistantResponse.assistant_id
                    fileUploadDict['created_at'] = fileToAssistantResponse.created_at
                    fileUploadDict['original_file_name'] = fileName

                    makedirs(path.dirname(f'./src/{applicationName}/config/'), exist_ok=True)
        
                    with open(f'./src/{applicationName}/config/{fileToAssistantResponse.id}_{fileName}_{fileToAssistantResponse.assistant_id}.json', fileWriteMode, encoding='utf-8') as outputFile:
                        dump(fileUploadDict, outputFile, ensure_ascii=False, indent=messageIndent)
                
                except Exception as e:
                    print('Failure! Could not associated uploaded file to assistant, full error message: ' + str(e))
            
    def check_for_existing_assistant_file_id(self, assistantId, fileName, applicationName):
        """Function to review the previously generated file upload json configurations to return the ID associated"""
        configFiles = listdir(f'./src/{applicationName}/config/')
        assistantFiles = []

        for file in configFiles:
            if file.startswith('file') and file.endswith(f'{assistantId}.json'):
                assistantFiles.append(file)

        for file in assistantFiles:
            with open(f'./src/{applicationName}/config/{file}', 'r') as data:
                config = load(data)
                name = config['original_file_name']
            
                if name == fileName:
                    fileId = config['id']
                    print('Found file associated with id: ' + config['id'])
    
        return fileId
    
    def create_assistant_thread(self, assistantId, applicationName, userId, mode='w', messageIndent=0):
        """Function to directly create a thread and associate with an assistant at OpenAI"""
        threadDict = {}
        threadResponse = self.beta.threads.create(
            metadata={"assistantId": assistantId, "userId": userId}
        )

        threadDict['id'] = threadResponse.id
        threadDict['created_at'] = threadResponse.created_at
        threadDict['assistant_id'] = threadResponse.metadata['assistantId']
        threadDict['user_id'] = int(threadResponse.metadata['userId'])

        makedirs(path.dirname(f'./src/{applicationName}/config/'), exist_ok=True)
        
        with open(f'./src/{applicationName}/config/{threadResponse.id}_{threadResponse.created_at}_{assistantId}.json', mode, encoding='utf-8') as outputFile:
            dump(threadDict, outputFile, ensure_ascii=False, indent=messageIndent)

    def get_thread_id_for_user(self, assistantId, applicationName, userId):
        """Function to review the previously generated thread json file configurations to return the ID associated"""
        configFiles = listdir(f'./src/{applicationName}/config/')
        threadFiles = []

        for file in configFiles:
            if file.startswith('thread') and file.endswith(f'{assistantId}.json'):
                threadFiles.append(file)
    
        for file in threadFiles:
            with open(f'./src/{applicationName}/config/{file}', 'r') as data:
                config = load(data)
                threadId = config['id']
                userId = config['user_id']

            if userId == userId:
                userSpecificFileId = threadId
                print('Found existing thread for assistan and user with id: ' + str(userSpecificFileId))
            
        try:
            return userSpecificFileId
        except UnboundLocalError:
            raise Exception('Error: Thread does not exist for assistant and user ID.  Please check the assistant ID, application name, and user ID or call the create thread function.')
        
    def add_message_in_existing_thread(self, threadId, message, fileListToInclude):
        try:
            messageResponse = self.beta.threads.messages.create(
                thread_id = threadId,
                role = 'user',
                content = message,
                file_ids=fileListToInclude
            )

            print('Success! Message added to thread, full response: ' + str(messageResponse))
        except Exception as e:
            print('Failure! Message not added to thread, fill response: ' + str(e))

    def run_thread_for_assistant_response(self, threadId, assistantId, applicationName, userId, mode='w', messageIndent=0):
        try:
            createRunResponse = self.beta.threads.runs.create(
                thread_id = threadId,
                assistant_id = assistantId
            )
        except Exception as e:
            print('Failure! Could not run thread, full response: ' + str(e))
        else:
            try:
                runResponseDict = {}

                runResponse = self.beta.threads.runs.retrieve(
                thread_id = threadId,
                run_id = createRunResponse.id
                )

                runResponseDict['id'] = runResponse.id
                runResponseDict['assistant_id'] = runResponse.assistant_id
                runResponseDict['thread_id'] = runResponse.thread_id
                runResponseDict['user_id'] = userId
                runResponseDict['status'] = runResponse.status
                runResponseDict['created_at'] = runResponse.created_at
                runResponseDict['started_at'] = runResponse.started_at
                runResponseDict['completed_at'] = runResponse.completed_at
                runResponseDict['expires_at'] = runResponse.expires_at
                runResponseDict['failed_at'] = runResponse.failed_at
                runResponseDict['error_message'] = runResponse.last_error

                makedirs(path.dirname(f'./src/{applicationName}/data/run_logs/'), exist_ok=True)
        
                with open(f'./src/{applicationName}/data/run_logs/{runResponse.id}_{runResponse.created_at}_{runResponse.thread_id}.json', mode, encoding='utf-8') as outputFile:
                    dump(runResponseDict, outputFile, ensure_ascii=False, indent=messageIndent)
            
            except Exception as e:
                print('Failure! Could not retrieve run thread, full response: ' + str(e))
    
    #add new function or update one above to retrieve updated run status:
        # run = self.beta.threads.runs.retrieve(
        #     thread_id="thread_abc123",
        #     run_id="run_abc123"
        # )

    def retrieve_messages_in_existing_thread(self, threadId):
        try:
            threadMessageResponse = self.beta.threads.messages.list(thread_id = threadId)
            print('Success! Retrieved message list, full response: ' + str(threadMessageResponse))
        except Exception as e:
            print('Failure! Could not retrieve thread messages, full response: ' + str(e))
