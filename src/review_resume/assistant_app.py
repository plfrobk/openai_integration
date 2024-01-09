from caller.api_integration import OpenAIAPIIntegration

###VARIABLES###
fileNameOrNamesToUpload = 'RKairis_Resume_2023.pdf'
applicationName = 'review_resume'
assistantPrompt = 'You are an experienced recruiter helping people find jobs.  You will help people build resumes, if they do not already have one, or provide feedback to improve them if they do using your experience and knowledge of the latest trends in hiring.  You will also have guide applicants on how to change their resume to be a better fit after reviewing a job posting and role information.  It will be important that your tips to improve users resumes utilize action oriented language and tight business language without many filler words or unnecessary detail.'
assistantName = 'Resume Helper'
userPrompt = ''
responseDict = {}

###MAIN###

chatGPT = OpenAIAPIIntegration()

assistantId = chatGPT.get_assistant_id(applicationName=applicationName, assistantName=assistantName)

if assistantId[0:5] != 'asst_':
    chatGPT.create_assistant(name=assistantName, instructions=assistantPrompt, applicationName=applicationName)
    assistantId = chatGPT.get_assistant_id(applicationName=applicationName, assistantName=assistantName)

print(assistantId)

threadId = chatGPT.get_thread_id(assistantId=assistantId, applicationName=applicationName)

if threadId[0:7] != 'thread_':
    chatGPT.create_assistant_thread(assistantId=assistantId, applicationName=applicationName)
    threadId = chatGPT.get_thread_id(assistantId=assistantId, applicationName=applicationName)

print(threadId)
#chatGPT.create_assistant(name='Resume Helper', instructions=assistantPrompt, applicationName=applicationName)
#chatGPT.create_assistant_thread(applicationName=applicationName)