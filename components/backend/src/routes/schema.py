from pydantic import BaseModel, Field, field_validator


class RequestSchema:
    class Conversation(BaseModel):
        user_message: str = Field(..., title="User Message")
        thread_id: str = Field(..., title="Thread Identifier")

        @field_validator("user_message", "thread_id", mode="before")
        def validate_non_empty_string(cls, value: str, info) -> str:
            """
            Validates that a string field is not empty after stripping whitespace.
            This method applies to both `user_message` and `thread_id`.
            """
            stripped_value = value.strip()
            if len(stripped_value) < 1:
                raise ValueError(
                    f"{info.field_name.replace('_', ' ').capitalize()} must have a minimum length of 1 character after stripping whitespace."
                )
            return stripped_value


class ResponseSchema:
    class Conversation(BaseModel):
        bot_response: str = Field(..., title="Bot Response Message")
        thread_id: str = Field(..., title="Thread Identifier")
