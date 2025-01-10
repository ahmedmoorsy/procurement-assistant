import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    """
    Pytest fixture to initialize the FastAPI TestClient.
    This client will be used to make requests to the app in our tests.
    """
    return TestClient(app)


@pytest.mark.asyncio
async def test_chat_endpoint(client, mocker):
    """
    Tests the /bot/v1/chat endpoint to ensure it returns the expected response.
    Mocks external dependencies to focus on the endpoint’s behavior.
    """
    mock_mongo_client = MagicMock(name="MongoDBService")
    
    mock_graph_builder_init = AsyncMock(name="initialize_graph")
    mock_graph_builder_init.return_value = "mocked_graph"

    mock_standard_response = AsyncMock(name="standard_response")
    mock_standard_response.return_value = "Hello from the mocked bot!"

    mocker.patch(
        "graph.graph_builder.GraphBuilder.initialize_graph", 
        new=mock_graph_builder_init
    )

    mocker.patch(
        "services.conversation_service.ConversationService.standard_response",
        new=mock_standard_response
    )
    
    app.state.mongo_client = mock_mongo_client

    payload = {
        "user_message": "Hi there!",
        "thread_id": "test-thread-123"
    }

    response = client.post("/bot/v1/chat", json=payload)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    data = response.json()
    
    assert "bot_response" in data, "Response JSON should contain 'bot_response'"
    assert "thread_id" in data, "Response JSON should contain 'thread_id'"
    assert data["thread_id"] == payload["thread_id"], "thread_id in response does not match input"
    assert data["bot_response"] == "Hello from the mocked bot!", "bot_response is incorrect"
    mock_graph_builder_init.assert_awaited_once()
    mock_standard_response.assert_awaited_once_with(
        payload["user_message"],
        payload["thread_id"]
    )