from caller.api_integration import OpenAIAPIIntegration

###VARIABLES###
systemPrompt = "#Task You are a financial advisor who's assisting a married couple in their early 30s with two kids, age 1 and 3, with a combined income of $150k.  They are looking for advice for balancing risk while maximizing return with a goal of retiring by 60 and saving up enough for both children to go to college. #Hint They already have more than 6 months in savings in case of emergencies and do not have any debt outside of a 30 year mortgage on their home. Please do not suggest anything around savings or debt."
userPrompt = "I recently received a $25k cash bonus from my company.  I already have about $50k in low risk, dividend heavy stocks and not sure if I should put more into there or look into bonds, CDs, real estate, or other options for my money?"
gptTemperature = 1

###MAIN###
client = OpenAIAPIIntegration(applicationName='sample_chat_app', virtualEnvironmentName='local')
gptModel = client.modelInformation['latest_models'][0]['name'] #0 = GPT 3.5, 1 = GPT 4
modelLimitTokens = client.modelInformation['latest_models'][0]['max_tokens_supported']

tokenCheckPass = client.check_num_tokens_for_inputs(systemPrompt, userPrompt, modelLimitTokens)

if tokenCheckPass:
    try:
        rawResponse = client.get_chat_response(systemPrompt, userPrompt, gptModel, gptTemperature)
    except Exception as e:
        print(f'Error: Issue getting response from OpenAI!  Full message: {e}')
    else:
        try:
            formattedResponse = client.format_chat_response(rawResponse, systemPrompt, userPrompt)
        except Exception as e:
            print(f'Error: Issue formatting response from OpenAI! Full message: {e}')
            print(rawResponse)
        else:
            try:
                client.write_formatted_chat_response_to_json_file(formattedResponse)
            except Exception as e:
                print(f'Error: Issue writing results to JSON! Full message: {e}')
                print(formattedResponse)
            else:
                print("Response successfully received and written to file!")
