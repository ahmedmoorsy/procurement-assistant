from graph.graph_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from graph.graph_builder import GraphBuilder
from services.mognodb_service import MongoDBService


class ConversationService:
    def __init__(self, graph: GraphBuilder):
        """
        A service for handling conversations with a user. It uses `graph` to simulate
        the conversation flow and predict bot responses.
        """
        self.graph = graph

    async def standard_response(self, user_message: str, thread_id: str) -> str:
        """
        Simulates a conversation with a single user message and returns the bot's response.

        :param user_message: The input message from the user.
        :param thread_id: A thread identifier for tracking conversation context.
        :return: The bot's response (as a string) or None if no response is generated.
        """
        state = AgentState(
            messages=[],
        )

        state["messages"].append(HumanMessage(content=user_message, name="User"))
        messages_before = len(state["messages"])

        state = await self.graph.ainvoke(
            state, {"configurable": {"thread_id": thread_id}}
        )
        new_messages = state["messages"][messages_before:]

        last_response = None
        for response in new_messages:
            if "tool_calls" in response.additional_kwargs:
                for call in response.additional_kwargs["tool_calls"]:
                    print(
                        f"({type(response).__name__}) "
                        f"{call['function']['name']}: {call['function']['arguments']}"
                    )
            else:
                print(
                    f"({type(response).__name__}) {response.name} : {response.content}"
                )

            if isinstance(response, AIMessage):
                last_response = response.content

        return last_response
