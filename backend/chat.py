# --- Chat Node --- 

import os
from typing import List, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from copilotkit.langchain import copilotkit_customize_config

# Custom imports
from state import AgentState
from model import get_model
from download import get_resource
from retrieve import RetrieveFromPinecone
from arxiv import lookupArxiv
from services import save_response_to_db

@tool
def Search(queries: List[str]):
    """ A list of one or more search queries to find good resources to support the research. """

@tool
def WriteReport(report: str):
    """ Write the research report. """

@tool
def WriteResearchQuestion(research_question: str):
    """ Write the research question. """

@tool
def DeleteResources(urls: List[str]):
    """ Delete the URLs from the resources. """


async def chat_node(state: AgentState, config: RunnableConfig):
    """ Chat Node """

    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key"     : "report",
            "tool"          : "WriteReport",
            "tool_argument" : "report",
        }, {
            "state_key"     : "research_question",
            "tool"          : "WriteResearchQuestion",
            "tool_argument" : "research_question",
        }],
        emit_tool_calls="DeleteResources"
    )

    state["resources"] = state.get("resources", [])
    state["arvix_papers"] = state.get("arxiv_papers", [])

    research_question = state.get("research_question", "")
    report = state.get("report", "")

    resources = []
    arxiv_papers = state["arvix_papers"]

    for resource in state["resources"]:
        content = get_resource(resource["url"])
        if content == "ERROR":
            continue
        resources.append({
            **resource,
            "content": content
        })

    model = get_model(state)
    # Prepare the kwargs for the ainvoke method
    ainvoke_kwargs = {}
    if model.__class__.__name__ in ["ChatOpenAI"]:
        ainvoke_kwargs["parallel_tool_calls"] = False

    response = await model.bind_tools(
        [
            RetrieveFromPinecone,
            lookupArxiv,
            Search,
            WriteReport,
            WriteResearchQuestion,
            DeleteResources,
        ],
        **ainvoke_kwargs
    ).ainvoke([
        SystemMessage(
            content=f"""
            You are a research assistant. You help the user with writing a research report.
            Do not recite the resources, instead use them to answer the user's question.
            First, try to answer using resources from the RetrieveFromPinecone tool. ALWAYS DO THIS.
            If the user is not satisfied with the answer, proceed with the search tool.
            You should use the search tool to get resources before answering the user's question.
            If you finished writing the report, ask the user proactively for next steps, changes etc, make it engaging.
            To write the report, you should use the WriteReport tool. Never EVER respond with the report, only use the tool.
            Make sure the contents of the report are in well structured markdown format.
            If images are available in resources (Base64), produce the images such that they can be rendered in markdown viewers
            If a research question is provided, YOU MUST NOT ASK FOR IT AGAIN.
            REMEMBER, EVERY TIME THE USER ASKS A NEW QUESTION, USE THE RetrieveFromPinecone TOOL BEFORE PROCEEDING TO USE THE SEARCH TOOL.

            This is the research question:
            {research_question}

            This is the research report:
            {report}

            Here are the resources that you have available:
            {resources}

            Here are some of the research papers (title, summary, etc.) from Arvix that you have available (if any):
            {arxiv_papers}
            """
        ),
        *state["messages"],
    ], config)

    ai_message = cast(AIMessage, response)

    if ai_message.tool_calls:

        # print("FIRST", ai_message)

        if os.path.isfile("sourcedocument"):
            with open("sourcedocument", 'r', encoding='utf-8') as file:
                document_id = str(file.read())

        if ai_message.tool_calls[0]["args"].get("queries", None):
            with open("previousquestion", 'w', encoding="utf-8") as file:
                file.write(str(ai_message.tool_calls[0]["args"]["queries"][0]))
        
        if ai_message.tool_calls[0]["name"] == "WriteReport":

            report = ai_message.tool_calls[0]["args"].get("report", "")
            with open("previousquestion", 'r', encoding="utf-8") as file:
                question = str(file.read())
            
            # Save question with response to Snowflake
            if save_response_to_db(document_id, question, report):
                print("Response saved to database for ", document_id)

            # Remove the file
            if os.path.exists('previousquestion') and os.path.isfile('previousquestion'):
                os.remove('previousquestion')
            
            return {
                "report"    : report,
                "messages"  : [ai_message, ToolMessage(
                    tool_call_id    = ai_message.tool_calls[0]["id"],
                    content         = "Report written."
                )]
            }
        
        if ai_message.tool_calls[0]["name"] == "WriteResearchQuestion":
            return {
                "research_question" : ai_message.tool_calls[0]["args"]["research_question"],
                "messages"          : [ai_message, ToolMessage(
                    tool_call_id    = ai_message.tool_calls[0]["id"],
                    content         = "Research question written."
                )]
            }
        
    if "not satisfied" in ai_message.content.lower():
        return "search_node" 

    return {
        "messages": response
    }
