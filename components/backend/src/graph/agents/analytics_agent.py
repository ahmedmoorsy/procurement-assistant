from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.graph_state import ANALYTICS_AGENT
from graph.utils import create_tool_calling_agent
from graph.llm import llm
from graph.config_llm import ConfigLLM
import datetime


class MongoSchema(BaseModel):
    mongodb_query: str = Field(description="MongoDB query to run")


@tool(parse_docstring=True, response_format="content_and_artifact")
def write_query_tool(user_query: str) -> str:
    """
    Writes a MongoDB query based on user request.

    Args:
        user_query: The user's question or request about data.
    """
    prompt = (
        """
        You are an expert in crafting advanced MongoDB aggregation pipelines in Python.
        Your task is to generate a MongoDB aggregation pipeline in Python syntax based on the `user_question`.
        Use the provided `ORDER Table Schema` and `Schema Description` as references to construct the pipeline.
        For date using python date like this `datetime.datetime(2010, 1, 1)` and add in the beginning of the pipeline `import datetime`. 

        ORDER Table schema:"""
        + ConfigLLM.ORDER_SCHEMA
        + """
        ORDER Schema Description: """
        + ConfigLLM.ORDER_SCHEMA_DESCRIPTION
        + """

        Here are some example:
        Input: what is Total number of orders created during 2010 to 2013
        Output: {json_ex_string_1}

        Input: what is sum of all values in total price field
        Output: {json_ex_string_2}

        Input: what is Identification of the quarter with the highest spending
        Output: {json_ex_string_3}

        Input: Total spending grouped by Acquisition Type
        Output: {json_ex_string_4}

        Note: You have to just return the python pipeline query nothing else. Don't return any additional text with the python pipeline query.
        Input: {user_query}
        """
    )
    PROMPT = ChatPromptTemplate.from_template(prompt)
    chain = PROMPT | llm.with_structured_output(MongoSchema)

    resp = chain.invoke(
        {
            "user_query": user_query,
            "json_ex_string_1": ConfigLLM.FEW_SHOT_EXAMPLE_1,
            "json_ex_string_2": ConfigLLM.FEW_SHOT_EXAMPLE_2,
            "json_ex_string_3": ConfigLLM.FEW_SHOT_EXAMPLE_3,
            "json_ex_string_4": ConfigLLM.FEW_SHOT_EXAMPLE_4,
        }
    )
    return "MongoDB query has been generated successfully.", {
        "generated_query": resp.mongodb_query,
        "user_query": user_query,
        "current_route": ANALYTICS_AGENT,
    }


analytics_agent_prompt = """
You are an Analytics Agent specialized in procurement data.
Users may ask you to query or analyze procurement data from the database.
You have these tools to help you:
- write_query_tool

Your process:
1. First, validate the user's request. If the request specifies a year outside the range of 2012 to 2015, clarify this to the user without proposing a schema.
2. Write or propose a MongoDB schema/query (use write_query_tool) if it's required.
3. Format the results for the user in a nice way.

Important Constraints:
- The minimum year for queries is 2012.
- The maximum year for queries is 2015.
- If the user's request includes a year outside this range, clarify the constraint to the user instead of generating or executing the query.
- Don't mention to the user to use the generated query. Just generate it and store it in the state.
Examples:
User: Show me total orders for 2010
Assistant: I'm sorry, I can only process queries for data between 2012 and 2015. Could you refine your request to fit within this range?

User: Show me total orders for 2013
Assistant: Sure. Let me propose a schema/query.
tool_call: write_schema_tool

Current Date: {current_date}
""".format(
    current_date=datetime.datetime.now().strftime("%Y-%m-%d")
)

analytics_agent = create_tool_calling_agent(
    llm,
    analytics_agent_prompt,
    ANALYTICS_AGENT,
    [write_query_tool],
    call_after_tool=False,
)
