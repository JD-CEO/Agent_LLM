from typing import Annotated
from autogen import ConversableAgent, register_function
from exa_py import Exa
import requests

exa_api_key = "3ca94b00-c7a3-40fe-a998-c5a7d4ceda22"
exa = Exa(api_key="3ca94b00-c7a3-40fe-a998-c5a7d4ceda22")


#------------------------------------

def extract_urls(chat_results):
    """
    Extracts URLs from the chat history of ChatResult objects.

    Args:
        chat_results (list): A list of ChatResult objects.

    Returns:
        list: A list of URLs extracted from the content property.
    """
    urls = []
    for chat_result in chat_results:
        for entry in chat_result.chat_history:
            if 'content' in entry and entry['content'] is not None:
                # Assuming the content is a string representation of a list
                try:
                    # Convert the string to a list
                    extracted_urls = eval(entry['content'])
                    if isinstance(extracted_urls, list):
                        urls.extend(extracted_urls)
                except (SyntaxError, NameError):
                    # Handle the case where eval fails
                    print("Failed to evaluate content:", entry['content'])
    return urls




#------------------------------------

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

#------------------------------
# TOOLS : 
# web searcher 
# url_parser -> to html
def webSearch(query : Annotated[str, "its what should be searched for"]) -> list:
    urls = []
    result = exa.search(
        query,
        type="neural",
        use_autoprompt=True
        )
    for res in result.results:
        urls.append(res.url)
    return urls

def get_html_content(url: Annotated[str, "Its a url which data must be extracted from"]) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return response.text  # Return the HTML content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
#----------------------------
# AGNETS : 
# searcher
# parser
# user proxy
# summarizer 


searcher = ConversableAgent(
    name="searcher",
    system_message="You are a great researcher who can find best related articles for a given query topic using your interaction with web search tool ",
    llm_config=llm_config,
)

parser = ConversableAgent(
    name="parser",
    system_message="first : You are given many urls which you have to use url parser tool to convert them to html contents , second You are a great html parser who can understand html pages and extract their text contents",
    llm_config=llm_config,
)


summarizer = ConversableAgent(
    name="summarizer",
    system_message="You are given many texts that you must convert these separated texts to a single summarized article",
    llm_config=llm_config,
)


userProxy = ConversableAgent(
    name="user-proxy",
    system_message="you are a proxy user who secures the interaction and reply to different tool requests",
    llm_config=llm_config,
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
)

register_function(
    webSearch,
    caller=searcher,
    executor=userProxy,
    name="web-search",
    description="its a web search tool which can search about any query and find related urls that arae correspond to the given query which"
)

register_function(
    get_html_content,
    caller=parser,
    executor=userProxy,
    name="url-parser",
    description="It gets a single url and returns html content of that url in an string format"
)


task = "Find the related articles to islam "

# Step 1: Search for URLs
search_result = userProxy.initiate_chats([
    {
        "recipient": searcher,
        "message": task,
        "max_turns": 2,
        "summary_method": "last_msg",
    }
])

# Extract URLs from the search result
cntnt = extract_urls(search_result)
print(" /n --------------------------- /n",cntnt)

urls = search_result  # Assuming the content contains the URLs
# Step 2: Parse the URLs
parse_result = userProxy.initiate_chats([
    {
        "recipient": parser,
        "message": f"These are the URLs found so far: {urls}",
        "max_turns": 1,
        "summary_method": "last_msg",
    }
])

# Extract HTML content from the parse result
html_content = parse_result# Assuming the content contains the HTML

# Step 3: Summarize the HTML content
summary_result = userProxy.initiate_chats([
    {
        "recipient": summarizer,
        "message": f"Articles are listed below : {html_content}. Summarize them into a single article.",
        "max_turns": 1,
        "summary_method": "last_msg",
    }
])

# Final summary output
final_summary = summary_result['content']  # Assuming the content contains the summary
print(final_summary) 
