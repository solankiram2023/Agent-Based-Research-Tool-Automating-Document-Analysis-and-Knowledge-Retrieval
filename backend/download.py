# --- This module contains the implementation of the download_node function ---

import aiohttp
import html2text
from copilotkit.langchain import copilotkit_emit_state
from langchain_core.runnables import RunnableConfig

# Custom imports
from state import AgentState

_RESOURCE_CACHE = {}

def get_resource(url: str):
    """ Get a resource from the cache. """
    
    return _RESOURCE_CACHE.get(url, "")


_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

async def _download_resource(url: str):
    """ Download a resource from the internet asynchronously. """
    
    try:
        async with aiohttp.ClientSession() as session:
            
            async with session.get(
                url,
                headers = {"User-Agent": _USER_AGENT},
                timeout = aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                
                html_content      = await response.text()
                markdown_content  = html2text.html2text(html_content)
                _RESOURCE_CACHE[url]   = markdown_content
                
                return markdown_content
    
    except Exception as e:
        _RESOURCE_CACHE[url] = "ERROR"
        
        return f"Error downloading resource: {e}"

async def download_node(state: AgentState, config: RunnableConfig):
    """ Download resources from the internet. """
    
    resources_to_download= []
    state["resources"] = state.get("resources", [])
    state["logs"]      = state.get("logs", [])

    logs_offset = len(state["logs"])

    # Find resources that are not downloaded
    for resource in state["resources"]:
        if not get_resource(resource["url"]):
            resources_to_download.append(resource)
            
            state["logs"].append({
                "message"   : f"Downloading {resource['url']}",
                "done"      : False
            })

    # Emit the state to let the UI update
    await copilotkit_emit_state(config, state)

    # Download the resources
    for i, resource in enumerate(resources_to_download):
        await _download_resource(resource["url"])
        state["logs"][logs_offset + i]["done"] = True

        # update UI
        await copilotkit_emit_state(config, state)

    return state
