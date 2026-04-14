from typing import Optional
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from llm_provider import llm

memory_store = {}

def get_session_memory(session_id):
    if session_id not in memory_store:
        memory_store[session_id] = {"messages": [], "profile": {}}
    return memory_store[session_id]

class UserProfile(BaseModel):
    name: Optional[str] = None
    occupation: Optional[str] = None
    mood: Optional[str] = None

def extract_user_info(text: str):
    extractor = llm.with_structured_output(UserProfile)
    return extractor.invoke([
        {"role": "system", "content": "Extract name, occupation, mood, gender, age if present."},
        {"role": "user", "content": text}
    ])

def build_context(session):
    messages = session["messages"][-6:]
    profile = session["profile"]

    system_context = f'''
        User profile:
        Name: {profile.get("name", "Unknown")}
        Mood: {profile.get("mood", "Unknown")}
    '''

    return [{"role": "system", "content": system_context}] + messages