import autogen
'''
    A simple starting point with autogen
'''


config_list = [
    {
        "model": "ollama/llama3.1",  
        "base_url": "http://localhost:4000",
        "api_key" : "NULL",
    }
]

llm_config = {
    "config_list" : config_list
}

assistant = autogen.AssistantAgent(
    "assistant",
    llm_config = llm_config
)

user_proxy = autogen.UserProxyAgent(
    "user_proxy",
    code_execution_config = {'use_docker': False}
)

user_proxy.initiate_chat(
    assistant,
    message ="What is the name of the model you are based on?"
)

