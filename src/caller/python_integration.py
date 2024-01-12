from os import makedirs, path, listdir
from json import dump, load
from openai import OpenAI
from time import sleep

class OpenAIPythonIntegration(OpenAI):
    """Custom class to utilize Python to directly work with OpenAI to do various functions"""
    def __init__(self, applicationName, virtualEnvironmentName):
        self.applicationName = applicationName
        self.virtualEnvironmentName = virtualEnvironmentName
        
        self.apiKey = self.get_api_key()
        self.organizationId = self.get_organization_key()
    
        super().__init__(organization=self.organizationId, api_key=self.apiKey)

    def get_api_key(self):
        """Function to get the API key to use for authorization when opening client object"""
        try:
            fileName = f'./{self.virtualEnvironmentName}/API_KEY.txt'
            
            with open(fileName, 'r', encoding='utf-8') as data:
                key = data.read().strip()
            return key
        except FileNotFoundError as e:
            print(f"Error: API key file not found! Full message: ${e}")
        
    def get_organization_key(self):
        """Function to get the Organization key to use with the API key when opening client object"""
        try:
            fileName = f'./{self.virtualEnvironmentName}/ORGANIZATION_KEY.txt'
            
            with open(fileName, 'r', encoding='utf-8') as data:
                key = data.read().strip()
            return key
        except FileNotFoundError as e:
            print(f"Error: Organization key file not found! Full message: ${e}")

    def create_assistant(self, name, instructions, metadata = {}, assistantType='retrieval', gptModel='gpt-4-1106-preview', mode='w', messageIndent=0):
        """Function to directly use OpenAI to create an assistant"""
        try:
            assistantDict = {}
            assistantResponse = self.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=gptModel,
                tools=[{"type": assistantType}],
                metadata=metadata
            ) 

            assistantDict['id'] = assistantResponse.id
            assistantDict['name'] = assistantResponse.name
            assistantDict['created_at'] = assistantResponse.created_at
            assistantDict['model'] = assistantResponse.model
            assistantDict['instructions'] = assistantResponse.instructions
            assistantDict['type'] = assistantResponse.tools[0].type
            assistantDict['metadata'] = assistantResponse.metadata

            makedirs(path.dirname(f'./src/{self.applicationName}/config/'), exist_ok=True)
            
            with open(f'./src/{self.applicationName}/config/{assistantResponse.id}_{assistantResponse.name}.json', mode, encoding='utf-8') as outputFile:
                dump(assistantDict, outputFile, ensure_ascii=False, indent=messageIndent)
            print('Success! Assistant successfully created and saved to config file with id: ' + str(assistantResponse.id))

        except Exception as e:
            print('Failure! Assistant failed to create, full response: ' + str(e))

        print('Created assistant with id: ' + str(assistantResponse.id))

    def get_assistant_id_from_config(self, assistantName):
        """Function to review the previously generated assistant json file configurations to return the ID associated"""
        configFiles = listdir(f'./src/{self.applicationName}/config/')
        assistantFiles = []

        for file in configFiles:
            if file.startswith('asst'):
                assistantFiles.append(file)
        
        for file in assistantFiles:
            with open(f'./src/{self.applicationName}/config/{file}', 'r') as data:
                config = load(data)
                name = config['name']
            
                if name == assistantName:
                    assistantId = config['id']
                    print('Found existing assistant with id: ' + assistantId)
        
        try:
            return assistantId
        except UnboundLocalError:
            raise Exception('Error: Assistant does not exist by name entered.  Please check the application and assistant name or call the create assistant function.')
    
    def upload_file_to_assistant(self, fileName, assistantId, filePurpose='assistants', fileReadMode = 'rb', fileWriteMode = 'w', messageIndent=0):
        """Function to directly upload a file to OpenAI"""
        fileUploadDict = {}

        with open(f'./src/{self.applicationName}/data/{fileName}', mode=fileReadMode) as fileToUpload:
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

                    makedirs(path.dirname(f'./src/{self.applicationName}/config/'), exist_ok=True)
        
                    with open(f'./src/{self.applicationName}/config/{fileToAssistantResponse.id}_{fileName}_{fileToAssistantResponse.assistant_id}.json', fileWriteMode, encoding='utf-8') as outputFile:
                        dump(fileUploadDict, outputFile, ensure_ascii=False, indent=messageIndent)
                
                except Exception as e:
                    print('Failure! Could not associate uploaded file to assistant, full error message: ' + str(e))
            
    def check_for_existing_assistant_file_id_from_config(self, assistantId, fileName):
        """Function to review the previously generated file upload json configurations to return the ID associated"""
        configFiles = listdir(f'./src/{self.applicationName}/config/')
        assistantFiles = []

        for file in configFiles:
            if file.startswith('file') and file.endswith(f'{assistantId}.json'):
                assistantFiles.append(file)

        for file in assistantFiles:
            with open(f'./src/{self.applicationName}/config/{file}', 'r') as data:
                config = load(data)
                name = config['original_file_name']
            
                if name == fileName:
                    fileId = config['id']
                    print('Found file associated with id: ' + config['id'])
    
        return fileId
    
    def create_assistant_thread(self, assistantId, userId, metadata = {}, mode='w', messageIndent=0):
        """Function to directly create a thread and associate with an assistant at OpenAI"""
        try:
            threadDict = {}
            threadResponse = self.beta.threads.create(
                metadata=metadata
            )

            threadDict['id'] = threadResponse.id
            threadDict['created_at'] = threadResponse.created_at
            threadDict['assistant_id'] = assistantId
            threadDict['user_id'] = userId

            makedirs(path.dirname(f'./src/{self.applicationName}/config/'), exist_ok=True)
            
            with open(f'./src/{self.applicationName}/config/{threadResponse.id}_{threadResponse.created_at}_{assistantId}.json', mode, encoding='utf-8') as outputFile:
                dump(threadDict, outputFile, ensure_ascii=False, indent=messageIndent)
            print('Success! Thread successfully created and saved to config file with id: ' + str(threadResponse.id))

        except Exception as e:
            print('Failure! Thread failed to create, full response: ' + str(e))


    def get_thread_id_for_user(self, assistantId, userId):
        """Function to review the previously generated thread json file configurations to return the ID associated"""
        configFiles = listdir(f'./src/{self.applicationName}/config/')
        threadFiles = []

        for file in configFiles:
            if file.startswith('thread') and file.endswith(f'{assistantId}.json'):
                threadFiles.append(file)
    
        for file in threadFiles:
            with open(f'./src/{self.applicationName}/config/{file}', 'r') as data:
                config = load(data)
                threadId = config['id']
                userId = config['user_id']

            if userId == userId:
                userSpecificFileId = threadId
                print('Found existing thread for assistant and user with id: ' + str(userSpecificFileId))
            
        try:
            return userSpecificFileId
        except UnboundLocalError:
            raise Exception('Error: Thread does not exist for assistant and user ID.  Please check the assistant ID, application name, and user ID or call the create thread function.')
        
    def add_message_in_existing_thread(self, threadId, message, fileListToInclude, userId, metadata={}, mode='w', messageIndent=0):
        try:
            messageResponseDict = {}

            messageResponse = self.beta.threads.messages.create(
                thread_id = threadId,
                role = 'user',
                content = message,
                file_ids=fileListToInclude,
                metadata=metadata
            )

            messageResponseDict['id'] = messageResponse.id
            messageResponseDict['created_at'] = messageResponse.created_at
            messageResponseDict['thread_id'] = messageResponse.thread_id
            messageResponseDict['run_id'] = messageResponse.run_id
            messageResponseDict['user_id'] = userId
            messageResponseDict['user'] = messageResponse.role
            messageResponseDict['response_type'] = messageResponse.content[0].type
            messageResponseDict['response_text'] = messageResponse.content[0].text.value

            makedirs(path.dirname(f'./src/{self.applicationName}/data/chat_messages/'), exist_ok=True)

            with open(f'./src/{self.applicationName}/data/chat_messages/{userId}_{messageResponse.role}_{messageResponse.id}_{messageResponse.created_at}_{messageResponse.run_id}.json', mode, encoding='utf-8') as outputFile:
                dump(messageResponseDict, outputFile, ensure_ascii=False, indent=messageIndent)

            print('Success! Message added to thread, full response: ' + str(messageResponse))
        except Exception as e:
            print('Failure! Message not added to thread, full response: ' + str(e))

    def run_thread_for_assistant_response(self, threadId, assistantId, userId, metadata={}, mode='w', messageIndent=0, runProcessingStatus='in_progress', maxRetries=5, retryWaitTimeSeconds=3):
        try:
            createRunResponse = self.beta.threads.runs.create(
                thread_id = threadId,
                assistant_id = assistantId,
                metadata=metadata
            )
        except Exception as e:
            print('Failure! Could not run thread, full response: ' + str(e))
        else:
            try:
                runResponseDict = {}
                tryCount = 1
                
                while runProcessingStatus == 'in_progress' and tryCount <= maxRetries:
                    runResponse = self.beta.threads.runs.retrieve(
                        thread_id = threadId,
                        run_id = createRunResponse.id
                    )

                    runProcessingStatus = runResponse.status
                    tryCount += 1
                    sleep(retryWaitTimeSeconds)

                if runProcessingStatus == 'in_progress':
                    print('Failure! Run not completed within max retry limit.  Please try again later.')
                else:
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

                    makedirs(path.dirname(f'./src/{self.applicationName}/data/run_logs/'), exist_ok=True)
            
                    with open(f'./src/{self.applicationName}/data/run_logs/{runResponse.id}_{runResponse.created_at}_{runResponse.thread_id}.json', mode, encoding='utf-8') as outputFile:
                        dump(runResponseDict, outputFile, ensure_ascii=False, indent=messageIndent)
            
            except Exception as e:
                print('Failure! Could not retrieve run thread, full response: ' + str(e))


    def get_latest_assistant_message_in_existing_thread(self, threadId, userId, assistantRoleName = 'assistant', mode='w', messageIndent=0):
        try:
            threadMessageResponse = self.beta.threads.messages.list(thread_id = threadId)
            latestMessage = threadMessageResponse.data[0]

            if latestMessage.role == assistantRoleName:
                for response in latestMessage.content:
                    messageResponseDict = {}
                    
                    messageResponseDict['id'] = latestMessage.id
                    messageResponseDict['created_at'] = latestMessage.created_at
                    messageResponseDict['thread_id'] = latestMessage.thread_id
                    messageResponseDict['run_id'] = latestMessage.run_id
                    messageResponseDict['user_id'] = userId
                    messageResponseDict['user'] = latestMessage.role
                    messageResponseDict['response_type'] = response.type
                    messageResponseDict['response_text'] = response.text.value

                    makedirs(path.dirname(f'./src/{self.applicationName}/data/chat_messages/'), exist_ok=True)
        
                    with open(f'./src/{self.applicationName}/data/chat_messages/{userId}_{latestMessage.role}_{latestMessage.id}_{latestMessage.created_at}_{latestMessage.run_id}.json', mode, encoding='utf-8') as outputFile:
                        dump(messageResponseDict, outputFile, ensure_ascii=False, indent=messageIndent)
            else:
                print('Failure! Latest message is not an assistant response.  Please re-run the function to run the assistant thread and try again.')
        except Exception as e:
            print('Failure! Could not retrieve thread messages, full response: ' + str(e))

    def get_all_messages_in_existing_thread(self, threadId, userId, mode='w', messageIndent=0):
        try:
            threadMessageResponse = self.beta.threads.messages.list(thread_id = threadId)
            latestMessage = threadMessageResponse.data

            for message in latestMessage:
                for response in message.content:
                    messageResponseDict = {}

                    messageResponseDict['id'] = message.id
                    messageResponseDict['created_at'] = message.created_at
                    messageResponseDict['thread_id'] = message.thread_id
                    messageResponseDict['run_id'] = message.run_id
                    messageResponseDict['user_id'] = userId
                    messageResponseDict['user'] = message.role
                    messageResponseDict['response_type'] = response.type
                    messageResponseDict['response_text'] = response.text.value

                    makedirs(path.dirname(f'./src/{self.applicationName}/data/chat_messages/'), exist_ok=True)
        
                    with open(f'./src/{self.applicationName}/data/chat_messages/{userId}_{message.role}_{message.id}_{message.created_at}_{message.run_id}.json', mode, encoding='utf-8') as outputFile:
                        dump(messageResponseDict, outputFile, ensure_ascii=False, indent=messageIndent)
            
            print('Success! All thread messages retrieved and saved')
        except Exception as e:
            print('Failure! Could not retrieve thread messages, full response: ' + str(e))
