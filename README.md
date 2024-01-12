# openai_integration
Application to integrate with OpenAI's functionality, both via API and Python, that will call and save results to local JSON files to use as a starter to develop applications.  Recommend the following to get started:

1.) Create a virtual environment

2.) Utilize the requirements.txt to install all necessary dependencies

3.) Create a "API_KEY.txt" and "ORGANIZATION_KEY.txt" file in your virtual environment folder with your API and Organization code from OpenAI (Note: This file and all other contents in the virtual environment folder are excluded from GitHub for security reasons)

4.) Run "pip install -e ." in your root folder to ensure the main caller package is avaiable to the other applications

After this, the main application are all contained in the "src" folder.  The "caller" application is the main class that any other application or use cases will run off.  Calling the main custom class requires you to pass along an "application name" that will then automatically create additional folders and files in the "src" folder as you run it.
