from graph.agents.greeting_agent import greeting_agent
from graph.agents.analytics_agent import analytics_agent
from graph.agents.validation_agent import validation_agent
from graph.agents.execution_agent import execution_agent
from graph.graph_routes import (
    pre_greeting_routing,
    post_greeting_routing,
    analytics_routing,
    validation_routing,
)
from graph.graph_state import (
    AgentState,
    GREETING_AGENT,
    VALIDATION_AGENT,
    EXECUTION_AGENT,
    ANALYTICS_AGENT,
)
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver


class GraphBuilder:
    """
    A service to encapsulate the state graph initialization and operations.

    Attributes:
        mongo_client: An instance of a MongoDB client for database interactions.
        graph: The state graph for handling agents and transitions.
        graph_builder: A compiled version of the state graph with checkpointing.
    """

    def __init__(self, mongo_client):
        """
        Initializes the graph service with the provided MongoDB client.

        :param mongo_client: A MongoDB client for database interactions.
        """
        self.mongo_client = mongo_client

    async def initialize_graph(self) -> StateGraph:
        """
        Initializes and configures the state graph with agents and routing.

        :return: A configured StateGraph instance.
        """
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node(GREETING_AGENT, greeting_agent)
        graph.add_node(ANALYTICS_AGENT, analytics_agent)
        graph.add_node(VALIDATION_AGENT, validation_agent)

        async def execution_agent_with_mongo(state: AgentState, config: dict):
            return await execution_agent(state, config, self.mongo_client)

        graph.add_node(EXECUTION_AGENT, execution_agent_with_mongo)

        # Add conditional edges
        graph.add_conditional_edges(
            START,
            pre_greeting_routing(GREETING_AGENT),
            [GREETING_AGENT, ANALYTICS_AGENT, END],
        )
        graph.add_conditional_edges(
            GREETING_AGENT,
            post_greeting_routing(END),
            [ANALYTICS_AGENT, END],
        )
        graph.add_conditional_edges(
            ANALYTICS_AGENT,
            analytics_routing,
            [VALIDATION_AGENT, END],
        )
        graph.add_conditional_edges(
            VALIDATION_AGENT,
            validation_routing,
            [EXECUTION_AGENT, ANALYTICS_AGENT],
        )

        # Add direct edge
        graph.add_edge(EXECUTION_AGENT, ANALYTICS_AGENT)

        memory = MemorySaver()
        graph = graph.compile(checkpointer=memory)
        return graph
