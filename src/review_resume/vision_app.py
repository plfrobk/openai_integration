from caller.api_integration import OpenAIAPIIntegration

###VARIABLES###
fileName = "RKairis_Resume_2023.pdf"
applicationName = "review_resume"
systemPrompt = "Not provided"
userPrompt = "Is this a valid resume (key of valid with y/n value)? If it's valid, provide a summary (key of summary) of the full resume in no more than 3 sentences.  Also include a detailed transcript of any text in the document (key of detail)."

###MAIN###

chatGPT = OpenAIAPIIntegration(applicationName=applicationName, virtualEnvironmentName='local')

if fileName.endswith('.pdf'):
    imageFileOrFilesNames = chatGPT.convert_pdf_to_images(pdfFileName=fileName)
else:
    imageFileOrFilesNames = fileName

try:
    rawResponse = chatGPT.get_vision_response_from_local_files(imageFileOrFilesNames, userPrompt)
except Exception as e:
        print(f'Error: Issue getting response from OpenAI!  Full message: {e}')
else:
    try:
        formattedResponse = chatGPT.format_chat_response(rawResponse, systemPrompt, userPrompt)
    except Exception as e:
        print(f'Error: Issue formatting response from OpenAI! Full message: {e}')
        print(rawResponse)
    else:
        try:
            chatGPT.write_formatted_chat_response_to_json_file(formattedResponse)
        except Exception as e:
            print(f'Error: Issue writing results to JSON! Full message: {e}')
            print(formattedResponse)
        else:
            print("Response successfully received and written to file!")