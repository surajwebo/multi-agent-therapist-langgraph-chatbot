from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical", "other"] = Field(
        ...,
        description="Classify if the message reqires an emotioonal response (therapist) or logical response (engineer) or other"
    )

class State(TypedDict):
    message: Annotated[list, add_messages]
    message_types: Optional[str]
    next: Optional[str]

class ChatRequest(BaseModel):
    message: str
    session_id: str
