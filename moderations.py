from pydantic import BaseModel, Field
from typing import Literal

from llm_provider import moderationllm

class ModerationResult(BaseModel):
    is_safe: bool
    reason: str

def moderate_message(message: str):
    moderation_llm = moderationllm.with_structured_output(ModerationResult)
    response = moderation_llm.invoke(
        [
            {
                "role": "system", 
                "content": 
                """
                    You are a strict content moderation system.
                    
                    Check if the following message contains:
                    - violent content
                    - hate speech
                    - harassment
                    - self-harm
                    - explicit content
                    - sexual explicit content
                    - illegal activities
                    
                    Return:
                    - 'is_safe': true/false
                    - 'reason': short explanation if unsafe
                """
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )
    return response