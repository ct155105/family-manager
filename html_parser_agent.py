from dotenv import load_dotenv
load_dotenv()

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

class ParserState(TypedDict):
    url: str 
    html: str
    code: str
    error: bool
    template_filepath: str
    code_filepath: str


graph_builder = StateGraph(ParserState)

import os
from langchain.chat_models import init_chat_model


# agent = create_react_agent(
#     model="openai:gpt-4.1",
#     tools=tools,
# )

llm = init_chat_model("openai:gpt-4.1")


def fetch_template_content(state: ParserState):
    """
    Reads the content of a file and returns it as a string.
    """
    with open(state["template_filepath"], 'r', encoding='utf-8') as f:
        return {"code": f.read()}
    
def write_file_content(state: ParserState):
    """
    Writes the content to a file specified in the state.
    """
    with open(state["code_filepath"], 'w', encoding='utf-8') as f:
        f.write(state["code"])
    print(f"Code written to {state['code_filepath']} successfully.")

def get_relevant_html(state: ParserState):
    """
    Fetches the HTML from the given URL and returns the content of the <main> tag.
    If the <main> tag is not found, raises an exception.
    This function is useful for parsing web pages to extract relevant content.
    It can be used to scrape event listings or other structured data from web pages.
    """
    print(f"Fetching HTML from {state["url"]}...")
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(state["url"])
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find('main')
    if not main:
        raise Exception("No <main> tag found in the HTML.")
    print("Returning HTML segments from <main> tag that contain keywords:")
    return {"html": main.prettify()}

def create_parser_code(state: ParserState):
    """
    TODO
    """
    system_prompt = (
        "You are a helpful HTML parser agent. "
        "Your task is to generate Python code that can parse the HTML content "
        "Fill in the parser code inside of the ## PARSER CODE HERE ## comment block. "
        "The code should extract relevant information from the HTML and return it as a list of dictionaries. "
        "Each dictionary should contain the following keys: 'date_time', 'end_time', "
        "'title', 'description', 'venue', 'address'. "
        " If any of these keys are not present, just return an empty string for that key. "
        "The code should be able to handle cases where some fields are missing. "
        "The code should be able to handle cases where the HTML structure is slightly different. "
        "The code should be able to handle cases where the HTML contains multiple event listings. "
        "The code should be able to handle cases where the HTML contains nested elements. "
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the HTML content:\n{state['html']}\n\n"
                                    "Please generate the parser code that can extract the relevant information from this HTML. "
                                    "Make sure to fill in the ## PARSER CODE HERE ## comment block with the parser code."}
    ]
    response = llm.invoke(messages)
    code = response.content.strip()
    return {"code": code}
    


graph_builder.add_node("get_relevant_html", get_relevant_html)
graph_builder.add_node("read_file_content", fetch_template_content)
graph_builder.add_node("create_parser_code", create_parser_code)
graph_builder.add_node("write_file_content", write_file_content)

graph_builder.add_edge(START, "get_relevant_html")
graph_builder.add_edge("get_relevant_html", "read_file_content")
graph_builder.add_edge("read_file_content", "create_parser_code")
graph_builder.add_edge("create_parser_code", "write_file_content")


graph = graph_builder.compile()

result = graph.invoke({
    "url": "https://www.columbuszoo.org/events",
    "template_filepath": "events_tool_template.py",
    "code_filepath": "events_tool_zoo.py",
        })

print("Code generation completed successfully.")

