import datetime
from bson import ObjectId
import re
from typing import Callable, List
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import tools_condition, ToolNode


def create_tool_calling_agent(
    llm,
    system_promt: str,
    agent_name: str,
    tools: List[Callable],
    call_after_tool: bool = True,
):
    llm_with_tools = llm.bind_tools(tools)

    def agent(state, config):
        llm_response = llm_with_tools.invoke(
            [SystemMessage(system_promt)] + state["messages"]
        )
        llm_response.name = agent_name
        # invoke agent
        state["messages"].append(llm_response)

        # if tool calls detected invoke the tools
        if tools_condition(state) == "tools":
            tool_node = ToolNode(tools)
            response = tool_node.invoke(state)

            for tool_message in response["messages"]:
                state["messages"].append(tool_message)
                if tool_message.artifact:
                    state = {**state, **tool_message.artifact}

            if call_after_tool:
                agent(state, config)
            else:
                return state

        return state

    return agent


def eval_mongodb_query(generated_query: str):
    """
    Evaluates a MongoDB query string and handles conversions for MongoDB-specific types.

    Handles:
    - Converts 'null' to Python's None.
    - Converts 'ObjectId' to bson.ObjectId.
    - Supports datetime.datetime.

    :param generated_query: The MongoDB query string containing 'null', 'ObjectId', or datetime objects.
    :return: A Python representation of the MongoDB query.
    """

    def null_replacement(match):
        return "None"

    def objectid_replacement(match):
        object_id_str = match.group(1)
        return f"ObjectId('{object_id_str}')"

    processed_query = re.sub(r"\bnull\b", null_replacement, generated_query)
    processed_query = re.sub(
        r"ObjectId\(\"(.*?)\"\)", objectid_replacement, processed_query
    )

    return eval(processed_query, {"datetime": datetime, "ObjectId": ObjectId})
