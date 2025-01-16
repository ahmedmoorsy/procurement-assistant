import logging
from fastapi import APIRouter, Request
from routes.schema import RequestSchema, ResponseSchema
from graph.graph_builder import GraphBuilder
from services.conversation_service import ConversationService


router = APIRouter(prefix="/bot/v1")
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ResponseSchema.Conversation)
async def chat(
    conversation_request: RequestSchema.Conversation, request: Request
) -> ResponseSchema.Conversation:
    graph = request.app.state.graph
    conversation_service = ConversationService(graph)
    bot_response = await conversation_service.standard_response(
        conversation_request.user_message, conversation_request.thread_id
    )

    return ResponseSchema.Conversation(
        bot_response=bot_response, thread_id=conversation_request.thread_id
    )
