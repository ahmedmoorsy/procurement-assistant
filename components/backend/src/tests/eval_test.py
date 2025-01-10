from graph.graph_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from graph.graph_builder import GraphBuilder
from services.mognodb_service import MongoDBService
from config import Config
import asyncio


async def get_query_result(query: str, state, graph):
    state["messages"].append(HumanMessage(content=query, name="User"))
    messages_before = len(state["messages"])

    state = await graph.ainvoke(
        state, {"configurable": {"thread_id": "test_thread_id"}}
    )
    new_messages = state["messages"][messages_before:]
    

async def main():
    config = Config()
    mongo_client = MongoDBService(
        host=config.mongodb.HOST,
        port=config.mongodb.PORT,
        username=config.mongodb.USERNAME,
        password=config.mongodb.PASSWORD,
        db_name=config.mongodb.DB_NAME,
        orders_collection="Orders",
    )
    graph_builder = GraphBuilder(mongo_client)
    graph = await graph_builder.initialize_graph()
    state = AgentState(
        messages=[],
    )
    get_query_result("query", state, graph)


if "__main__" == __name__:
    asyncio.run(main())