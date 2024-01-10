from caller.python_integration import OpenAIPythonIntegration

###VARIABLES###
fileNameOrNamesToUpload = ['RKairis_Resume_2023.pdf']
userId = 1
applicationName = 'review_resume'
assistantPrompt = 'You are an experienced recruiter helping people find jobs.  You will help people build resumes, if they do not already have one, or provide feedback to improve them if they do using your experience and knowledge of the latest trends in hiring.  You will also have guide applicants on how to change their resume to be a better fit after reviewing a job posting and role information.  It will be important that your tips to improve users resumes utilize action oriented language and tight business language without many filler words or unnecessary detail.'
assistantName = 'Resume Helper'
userPrompt = 'Please review the attached resume and provide any general feedback on the quality of the resume based on best practices in the recruiting field.'
responseDict = {}

###MAIN###

client = OpenAIPythonIntegration()

try:
    assistantId = client.get_assistant_id(applicationName=applicationName, assistantName=assistantName)
except:
    client.create_assistant(name=assistantName, instructions=assistantPrompt, applicationName=applicationName)
    assistantId = client.get_assistant_id(applicationName=applicationName, assistantName=assistantName)
else:
    fileListIds = []
    for file in fileNameOrNamesToUpload:
        try:
            fileId = client.check_for_existing_assistant_file_id(assistantId=assistantId, fileName=file, applicationName=applicationName)
            fileListIds.append(fileId)
        except:
            client.upload_file_to_assistant(fileName=file, applicationName=applicationName, assistantId=assistantId)
            fileId = client.check_for_existing_assistant_file_id(assistantId=assistantId, fileName=file, applicationName=applicationName)
            fileListIds.append(fileId)

    try:
        userThreadId = client.get_thread_id_for_user(assistantId=assistantId, applicationName=applicationName, userId=userId)
    except:
        client.create_assistant_thread(assistantId=assistantId, applicationName=applicationName, userId=userId)
        userThreadId = client.get_thread_id_for_user(assistantId=assistantId, applicationName=applicationName, userId=userId)
    else:
        #client.add_message_in_existing_thread(threadId=userThreadId, message=userPrompt, fileListToInclude=fileListIds)
        # client.run_thread_for_assistant_response(threadId=userThreadId, assistantId=assistantId, applicationName=applicationName, userId=userId)
        client.retrieve_messages_in_existing_thread(threadId=userThreadId)