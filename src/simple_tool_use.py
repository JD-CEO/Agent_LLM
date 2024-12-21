from typing import Annotated, Literal
from autogen import ConversableAgent


config_list = [
    {
        "model" : "ollama/llama3.1",
        "base_url" : "http://localhost:4000",
        "api_key" : "NULL",
    }
]

llm_config = {
    "config_list" : config_list,
    "seed" : 85,
    "temperature" : 0
}

Operator = Literal["+", "-", "*", "/"]


'''
    Tool definition 
'''
def calculator(a: str, b: str, operator: Annotated[Operator, "operator"]) -> int:
    a = int(a)
    b = int(b)
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return int(a / b)
    else:
        raise ValueError("Invalid operator")
'''
    Agents definition
'''
mathmatition = ConversableAgent(
    name="Mathmatition",
    system_message="You are an assistant in solving simple mathmatical problems ",
    llm_config=llm_config,
)
userProxy = ConversableAgent(
    name="user proxy",
    system_message="you are a proxy user who secures the interaction and reply to different tool requests",
    llm_config=llm_config,
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
)

'''
    Tool registeration
'''
mathmatition.register_for_llm(name="calculator", description="Its simple calculator with four operations that are summation, subtraction, multiplication and division")(calculator)
userProxy.register_for_execution(name="calculator")(calculator)

'''
    Defining the task
'''
task = "what is the result of 12*12"
chat_res = userProxy.initiate_chat(mathmatition, message=task)


