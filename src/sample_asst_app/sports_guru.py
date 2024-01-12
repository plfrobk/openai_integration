from caller.python_integration import OpenAIPythonIntegration

###VARIABLES###
fileNameOrNamesToUpload = []
userId = 1
assistantPrompt = 'You are a very helpful assistant who is good at answering sports trivia.  You can provide full detail about teams, players, and stats and help provide context for why they matter.  You also have no problem comparing teams and players across generations and take into consideration their competition, rules, and other environmental differences.'
assistantName = 'Sports Guru'
userPrompt = 'Who is considered the best team and player of all time in the NBA?'

###MAIN###

client = OpenAIPythonIntegration(applicationName='sample_asst_app', virtualEnvironmentName='local')

try:
    assistantId = client.get_assistant_id_from_config(assistantName=assistantName)
except:
    client.create_assistant(name=assistantName, instructions=assistantPrompt)
    assistantId = client.get_assistant_id_from_config(assistantName=assistantName)
else:
    fileListIds = []
    for file in fileNameOrNamesToUpload:
        try:
            fileId = client.check_for_existing_assistant_file_id_from_config(assistantId=assistantId, fileName=file)
            fileListIds.append(fileId)
        except:
            client.upload_file_to_assistant(fileName=file, assistantId=assistantId)
            fileId = client.check_for_existing_assistant_file_id_from_config(assistantId=assistantId, fileName=file)
            fileListIds.append(fileId)

    try:
        userThreadId = client.get_thread_id_for_user(assistantId=assistantId, userId=userId)
    except:
        client.create_assistant_thread(assistantId=assistantId, userId=userId, metadata={"assistantId": assistantId, "userId": userId})
        userThreadId = client.get_thread_id_for_user(assistantId=assistantId, userId=userId)
    else:
        client.add_message_in_existing_thread(threadId=userThreadId, message=userPrompt, fileListToInclude=fileListIds, userId=userId, metadata={"assistantId": assistantId, "userId": userId})
        client.run_thread_for_assistant_response(threadId=userThreadId, assistantId=assistantId, userId=userId)
        client.get_latest_assistant_message_in_existing_thread(threadId=userThreadId, userId=userId)