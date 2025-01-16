from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
from graph.graph_state import VALIDATION_AGENT
from graph.graph_state import AgentState
from graph.llm import llm
from graph.config_llm import ConfigLLM


class QueryValidation(BaseModel):
    is_valid: bool = Field(
        default=False,
        description="Whether the MongoDB query is valid or not according to the schema and security standards.",
    )
    explanation: str = Field(
        default="",
        description="A short and concise explanation of the validation result.",
    )


def validation_agent(state: AgentState, config: RunnableConfig):
    validation_agent_prompt = (
        """
        You are an Expert Validation Agent. Your task is to validate the MongoDB Python aggregation pipeline proposed by the Analytics Agent.
        Review the following:
        1. Ensure the pipeline references only the single existing collection (`ORDER`).
        2. Ensure the pipeline does not contain destructive operations (e.g., insert, update, delete, drop, rename).
        3. Ensure the pipeline does not pose security risks or attempt to access system collections.
        4. Validate that any predicates or stages in the pipeline correctly match the fields described in the schema.
        5. Validate that the pipeline structure adheres to valid MongoDB aggregation syntax in Python format.

        ORDER Table schema:
        """
        + ConfigLLM.ORDER_SCHEMA
        + """
        ORDER Schema Description: """
        + ConfigLLM.ORDER_SCHEMA_DESCRIPTION
        + """

        Validation Guidelines and Rules:
        1. Pipelines must be **read-only** and use aggregation stages exclusively.
        2. Prohibited operations include:
        - `insert`
        - `update`
        - `delete`
        - `drop`
        - `rename`
        3. The pipeline must not alter the database state or modify data in any form.
        4. If the user question cannot be fully answered with the aggregation pipeline, validate if the pipeline retrieves the closest relevant data without modifying the database.
        5. The pipeline must use proper Python syntax for MongoDB aggregation, including the correct use of data types like `datetime` where applicable.

        User asked query:
        {user_query}

        Generated pipeline:
        {generated_query}

        Now, based on this information, determine if the generated pipeline is valid or not.
        If the pipeline is valid, explain why it is valid.
        If the pipeline is invalid, provide reasoning and highlight which parts are incorrect, pose security issues, or deviate from the schema concisely.
        """
    )
    PROMPT = ChatPromptTemplate.from_template(validation_agent_prompt)
    chain = PROMPT | llm.with_structured_output(QueryValidation)
    user_query = state.get("user_query")
    generated_query = state.get("generated_query")
    resp = chain.invoke({"generated_query": generated_query, "user_query": user_query})
    bot_response = "The generated query is valid. It adheres to the schema, security standards, and MongoDB aggregation syntax."
    if not resp.is_valid:
        bot_response = f"The generated query: {generated_query} is invalid for user query: {user_query}, the following issues were identified: {resp.explanation}. Please try again and generate a valid query."

    validation_message = AIMessage(content=bot_response, name=VALIDATION_AGENT)
    state["messages"].append(validation_message)
    state["query_correct"] = resp.is_valid

    return {
        "messages": state["messages"],
        "query_correct": state["query_correct"],
        "current_route": VALIDATION_AGENT,
    }
