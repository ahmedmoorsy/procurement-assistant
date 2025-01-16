from graph.graph_state import AgentState
from langchain_core.messages import HumanMessage
from graph.graph_builder import GraphBuilder
from services.mognodb_service import MongoDBService
from config import Config
import asyncio
import logging


EXPECTED_RESULTS = {
    "Find the top 3 most frequently ordered line items in 2013, including their order count": [{'order_count': 4, 'itemName': 'food'}, {'order_count': 2, 'itemName': 'chairs'}, {'order_count': 2, 'itemName': 'fish food'}],
    "Total number of orders created during Q1 of 2013.": [{'total_orders': 11}]
    ,
    "Total spending grouped by acquisition type in 2013": [
        {"productCategory": "Electronics", "totalRevenue": 500000},
        {"productCategory": "Books", "totalRevenue": 300000},
    ],
}


async def get_query_result(query: str, graph):
    """
    Execute the query and return the predicted results.
    """
    state = await graph.ainvoke(
        {"messages": [HumanMessage(content=query, name="User")]},
        {"configurable": {"thread_id": "test_thread_id"}}
    )

    query_result = state.get("query_result")
    generated_query = state.get("generated_query")
    print("generated_query ", generated_query)

    print("query_result: ", query_result)
    return query_result


async def evaluate_query(query: str, graph):
    """
    Evaluate the query results by comparing the predicted results with expected results.
    """
    logging.info(f"Evaluating query: {query}")
    predicted_results = await get_query_result(query, graph)
    expected_results = EXPECTED_RESULTS.get(query)
    if expected_results is None:
        logging.warning(f"No expected results found for query: {query}")
        return

    if predicted_results == expected_results:
        logging.info(f"Query results match for query: {query}")
        return True
    else:
        logging.error(
            f"Query results do not match for query: {query}\n"
            f"Expected: {expected_results}\n"
            f"Predicted: {predicted_results}"
        )
    return False


async def main():
    logging.basicConfig(level=logging.INFO)

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

    queries = list(EXPECTED_RESULTS.keys())
    total_eval = 0
    for query in queries:
        is_correct = await evaluate_query(query, graph)
        total_eval += 1 if is_correct else 0
    
    print(f"Number of correct queries: {total_eval}/{len(queries)}")
        

if __name__ == "__main__":
    asyncio.run(main())