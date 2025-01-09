from langgraph.graph import MessagesState

GREETING_AGENT = "Greeting_Agent"
ANALYTICS_AGENT = "Analytics_Agent"
VALIDATION_AGENT = "Validation_Agent"
EXECUTION_AGENT = "Execution_Agent"


class AgentState(MessagesState):
    current_route: str
    user_query: str
    generated_query: str
    query_correct: bool
    query_result: str
