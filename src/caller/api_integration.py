from os import makedirs, path, listdir
from datetime import datetime
from json import dump, load
from tiktoken import get_encoding
from requests import post
from base64 import b64encode
import pypdfium2 as pdfium


class OpenAIAPIIntegration():
    """Custom class to utilize APIs (REST) to work with OpenAI to do various functions"""
    def __init__(self, applicationName, virtualEnvironmentName):
        self.applicationName = applicationName
        self.virtualEnvironmentName = virtualEnvironmentName

        self.apiKey = self.get_api_key()
        self.organizationId = self.get_organization_key()

    def get_api_key(self): #Put API key in virtual environment folder, e.g. local
        """Function to get the API key to use for authorization in API calls"""
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
    
    def get_chat_response(self, systemPrompt, userPrompt, gptModel, gptTemperature = 1, apiURL = 'https://api.openai.com/v1/chat/completions'):
        """Function to call the OpenAI chat API and return a response in JSON format"""
        header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.apiKey}",
        "OpenAI-Organization": self.organizationId
        }

        payload = {
        "model": gptModel,
        "temperature": gptTemperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": systemPrompt + " #Output You will **ALWAYS** return your answer with keys in JSON format.  You will **NEVER** include linebreaks, indents, or extra formatting"},
            {"role": "user", "content": userPrompt}
            ],
        }

        response = post(apiURL, headers=header, json=payload)

        return response.json()

    def format_chat_response(self, gptResponse, systemPrompt, userPrompt):
        """Function to take results from OpenAI and format them with appropriate data points"""
        outputDict = {}
        systemAnswerRaw = gptResponse['choices'][0]['message']['content']
        systemAnswerFormatted = systemAnswerRaw.replace('\n', '').replace('{  ','{')

        systemAnswerDateUnix = gptResponse['created']
        systemAnswerDateTimeFormatted = datetime.utcfromtimestamp(systemAnswerDateUnix).strftime('%Y-%m-%d %H:%M:%S')
        
        systemModel = gptResponse['model']
        systemCompletionTokens = gptResponse['usage']['completion_tokens']
        systemPromptTokens = gptResponse['usage']['prompt_tokens']
        systemTotalTokens = gptResponse['usage']['total_tokens']

        outputDict['answer'] = systemAnswerFormatted
        outputDict['system_prompt'] = systemPrompt
        outputDict['user_prompt'] = userPrompt
        outputDict['model'] = systemModel
        outputDict['date_time_unix'] = systemAnswerDateUnix
        outputDict['date_time_formatted'] = systemAnswerDateTimeFormatted
        outputDict['prompt_tokens'] = systemPromptTokens
        outputDict['completion_tokens'] = systemCompletionTokens
        outputDict['total_tokens'] = systemTotalTokens

        return outputDict
    
    def write_formatted_chat_response_to_json_file(self, results, unixDateTimeFieldName = 'date_time_unix', modelFieldName = 'model', mode='w', messageIndent=0):
        """Function to take the results and output to JSON file for analysis"""
        uniqueDateTimeStamp = results[unixDateTimeFieldName]
        modelName = results[modelFieldName]
        makedirs(path.dirname(f'./src/{self.applicationName}/data/chat_messages/'), exist_ok=True)
        
        with open(f'./src/{self.applicationName}/data/chat_messages/{modelName}_{uniqueDateTimeStamp}.json', mode, encoding='utf-8') as outputFile:
            dump(results, outputFile, ensure_ascii=False, indent=messageIndent)
    
    def get_num_tokens_from_string(self, inputToCheck, encodingName='cl100k_base'):
        """Function to get number of tokens in any string value"""
        encoding = get_encoding(encodingName)
        numTokens = len(encoding.encode(inputToCheck))
        
        return numTokens
    
    def check_num_tokens_for_inputs(self, systemPrompt, userPrompt, maxTokenLimit, averageResponseTokens = 1000):
        """Function to check the number of tokens compared to the limit to proactively catch errors"""
        systemPromptTokens = self.get_num_tokens_from_string(systemPrompt)
        userPromptTokens = self.get_num_tokens_from_string(userPrompt) + 32

        if systemPromptTokens + userPromptTokens + averageResponseTokens < maxTokenLimit:
            proceed = True
        else:
            print('Too many tokens to send! Please choose another model or limit your prompts.')
            proceed = False
        
        return proceed

    def convert_pdf_to_images(self, pdfFileName, renderDPIScale=3, renderRotationDegrees=0):
        fileNameExtensionCharacterPosition = pdfFileName.find('.')
        fileNameWithoutExtension = pdfFileName[:fileNameExtensionCharacterPosition]
        outputFileNames = []

        try:
            pdf = pdfium.PdfDocument(f"./src/{self.applicationName}/data/{pdfFileName}")
        except pdfium.PdfiumError as e:
            print(f'Error! Not a valid PDF, please upload a different file. Full error message: {e}')
        else:
            totalPages = len(pdf)  # get the number of pages in the document

            for pageNumber in range(0, totalPages):
                page = pdf[pageNumber]

                bitmap = page.render(
                    scale = renderDPIScale,    # 72 * scale dpi resolution, e.g. 3 scale = 72 * 3 or 216 dpi
                    rotation = renderRotationDegrees, # 0, 90, 180, or 270 degrees (default is 0)
                )

                fileNameFormatted = f'./src/{self.applicationName}/data/{fileNameWithoutExtension}_{pageNumber + 1}.png'
                
                convertedImage = bitmap.to_pil()
                convertedImage.save(fileNameFormatted)
                
                outputFileNames.append(fileNameFormatted)
        
        return outputFileNames
    
    def encode_image_to_b64(self, imagePath):
        """Function to encode a local image to base64 to prep for sending to OpenAI"""
        with open(imagePath, "rb") as imageFile:
            return b64encode(imageFile.read()).decode('utf-8')
    
    def get_vision_response_from_local_files(self, imageFileNameOrNames, userPrompt, gptModel='gpt-4-vision-preview', maxTokens=4096, apiURL = 'https://api.openai.com/v1/chat/completions'):
        """Function to call the open AI vision/image API and return a response in JSON format"""
        
        header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.apiKey}",
        "OpenAI-Organization": self.organizationId
        }

        imageFileNamesToEncode = []

        if isinstance(imageFileNameOrNames, list):
            imageFileNamesToEncode = imageFileNameOrNames
        else:
            imageFileNamesToEncode = list(imageFileNameOrNames)

        contentArray = [{"type": "text", "text": userPrompt}]

        for images in imageFileNamesToEncode:        
            base64Image = self.encode_image(f'./{images}')
            imageContent = {"type": "image_url"
                 , "image_url": {"url": f"data:image/jpeg;base64,{base64Image}"}}
            contentArray.append(imageContent)


        payload = {
        "model": gptModel,
        "messages": [
            {
            "role": "user",
            "content": contentArray
            }
        ],
        "max_tokens": maxTokens
        }

        response = post(apiURL, headers=header, json=payload)

        return response.json()
    
    def create_assistant(self, name, instructions, assistantType='retrieval', apiURL = 'https://api.openai.com/v1/assistants', gptModel='gpt-4-1106-preview', mode='w', messageIndent=0):
        """Function to call the open AI API to create an assistant"""
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
            "OpenAI-Organization": self.organizationId,
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

        makedirs(path.dirname(f'./src/{self.applicationName}/data/config/'), exist_ok=True)
        
        with open(f'./src/{self.applicationName}/data/config/{assistantId}_{assistantName}.json', mode, encoding='utf-8') as outputFile:
            dump(responseJSON, outputFile, ensure_ascii=False, indent=messageIndent)

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
    
    def create_assistant_thread(self, assistantId, apiURL = 'https://api.openai.com/v1/threads', mode='w', messageIndent=0):
        """Function to call the open AI API to create a thread"""
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
            "OpenAI-Organization": self.organizationId,
            "OpenAI-Beta": "assistants=v1"
            }

        payload = ''

        response = post(apiURL, headers=header, json=payload)
        responseJSON = response.json()

        threadId = responseJSON['id']
        createdDate = responseJSON['created_at']

        makedirs(path.dirname(f'./src/{self.applicationName}/data/config/'), exist_ok=True)
        
        with open(f'./src/{self.applicationName}/data/config/{threadId}_{createdDate}_{assistantId}.json', mode, encoding='utf-8') as outputFile:
            dump(responseJSON, outputFile, ensure_ascii=False, indent=messageIndent)

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


    modelInformation = {"latest_models": [{"name":"gpt-3.5-turbo-1106", "max_tokens_supported":4096, "cost_per_1k_tokens": 0.0030}, {"name":"gpt-4-1106-preview", "max_tokens_supported":128000, "cost_per_1k_tokens": 0.04}], "historical_models" : [{"name":"gpt-3.5-turbo", "max_tokens_supported":4000, "cost_per_1k_tokens": 0.0030}, {"name":"gpt-4", "max_tokens_supported":16000, "cost_per_1k_tokens": 0.009}, {"name":"gpt-4-32k", "max_tokens_supported":32000, "cost_per_1k_tokens": 0.18}]}