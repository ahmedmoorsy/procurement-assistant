import logging
from fastapi import APIRouter, Request
from routes.schema import RequestSchema, ResponseSchema
from services.mognodb_service import MongoDBService
from services.conversation_service import ConversationService
from graph.graph_builder import GraphBuilder


router = APIRouter(prefix="/bot/v1")
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ResponseSchema.Conversation)
async def chat(
    conversation_request: RequestSchema.Conversation, request: Request
) -> ResponseSchema.Conversation:
    mongo_client: MongoDBService = request.app.state.mongo_client
    graph_builder = GraphBuilder(mongo_client)
    graph = await graph_builder.initialize_graph()
    conversation_service = ConversationService(graph)
    bot_response = await conversation_service.standard_response(
        conversation_request.user_message, conversation_request.thread_id
    )

    return ResponseSchema.Conversation(
        bot_response=bot_response, thread_id=conversation_request.thread_id
    )
