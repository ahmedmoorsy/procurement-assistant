from typing import Literal
from langgraph.graph import END
from graph.graph_state import (
    AgentState,
    GREETING_AGENT,
    VALIDATION_AGENT,
    EXECUTION_AGENT,
    ANALYTICS_AGENT,
)


def pre_greeting_routing(default_route: str):
    def routing(state: AgentState) -> str:
        if "current_route" in state and state["current_route"]:
            if state["current_route"] in [EXECUTION_AGENT, VALIDATION_AGENT]:
                return ANALYTICS_AGENT
            return state["current_route"]
        else:
            return default_route

    return routing


def post_greeting_routing(default_route: str):
    def routing(state: AgentState) -> str:
        if "current_route" not in state or state["current_route"] == GREETING_AGENT:
            return default_route
        elif "current_route" in state and state["current_route"]:
            if state["current_route"] in [EXECUTION_AGENT, VALIDATION_AGENT]:
                return ANALYTICS_AGENT
            return state["current_route"]

    return routing


def analytics_routing(state: AgentState) -> Literal["Validation_Agent", "__end__"]:
    current_route = state.get("current_route")
    query_generated = state.get("generated_query")
    if current_route == ANALYTICS_AGENT and query_generated:
        return VALIDATION_AGENT
    else:
        return END


def validation_routing(
    state: AgentState,
) -> Literal["Analytics_Agent", "Execution_Agent"]:
    current_route = state.get("current_route")
    is_valid = state.get("query_correct")
    if current_route == VALIDATION_AGENT and is_valid:
        return EXECUTION_AGENT
    else:
        return ANALYTICS_AGENT
