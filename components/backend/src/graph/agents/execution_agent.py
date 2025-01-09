from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from graph.graph_state import AgentState, EXECUTION_AGENT
from graph.utils import eval_mongodb_query
from services.mognodb_service import MongoDBService


async def execution_agent(
    state: AgentState, config: RunnableConfig, mongo_client: MongoDBService
):
    generated_query = state.get("generated_query")
    query_result = ""
    try:
        query_pipeline = eval_mongodb_query(generated_query)
        query_result = await mongo_client.aggregate_orders(query_pipeline)
        formatted_results = "\n".join([str(result) for result in query_result])
        response = f"The query results are as follows:\n {formatted_results}"
    except Exception as e:
        print("An error occurred while executing the query: ", str(e))
        user_query = state.get("user_query")
        response = f"An error occurred while executing the query: {user_query}."

    return {
        "messages": [AIMessage(content=response, name=EXECUTION_AGENT)],
        "query_result": query_result,
        "current_route": EXECUTION_AGENT,
    }
