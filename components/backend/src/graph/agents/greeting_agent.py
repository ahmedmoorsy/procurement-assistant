from typing import Dict
from langchain_core.tools import tool

from graph.llm import llm
from graph.utils import create_tool_calling_agent
from graph.graph_state import GREETING_AGENT, ANALYTICS_AGENT


def greeting_agent_prompt(routes: Dict[str, str]) -> str:
    return f"""
    You are a Procurement Chatbot Assistant called Penny, here to help users interact with procurement data.
    Your role is to greet the user, understand their needs, and guide them to the appropriate specialized agent if necessary.

    Your primary goal is to:
    - Welcome the user.
    - Identify their needs by asking clarifying questions.
    - Redirect them to the appropriate assistant if their request requires specialized tasks.

    Here are the assistants you can redirect to:
    {''.join([f"- {key}: {value}" for key, value in routes.items()])}

    Example conversation:
    user: Hello
    assistant: Hello! Welcome to the Procurement Chatbot. How can I assist you today?
    user: Can you show me the total number of orders placed last month?
    assistant: Sure! Let me connect you to our analytics assistant for that.
    tool_call: redirect_tool
    """


@tool(parse_docstring=True, response_format="content_and_artifact")
def redirect_tool(
    next_agent: str,
) -> dict:
    """A tool that redirects to a specific agent.

    Args:
        next_agent: Name of the agent to redirect to.
    """
    return f"You will be redirected to {next_agent}", {"current_route": next_agent}


greeting_agent = create_tool_calling_agent(
    llm,
    greeting_agent_prompt(
        {
            ANALYTICS_AGENT: "Can analyze the data.",
        }
    ),
    GREETING_AGENT,
    [redirect_tool],
    call_after_tool=False,
)
