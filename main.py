
from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Optional


load_dotenv()

llm = init_chat_model(
    model="ollama:llama3", #"anthropic:claude-3-5-latest",
    max_tokens=1000,
    temperature=0.3
)

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical", "other"] = Field(
        ...,
        description="Classify if the message reqires an emotioonal response (therapist) or logical response (engineer) or other"
    )


class State(TypedDict):
    message: Annotated[list, add_messages]
    message_types: Optional[str]
    next: Optional[str]

def classify_message(state: State):
    last_message = state["message"][-1]
    classfier_llm = llm.with_structured_output(MessageClassifier)
    response = classfier_llm.invoke(
        [
            {
                "role": "system", 
                "content": '''
                You are a message classifier.
                Classify the following message as emotional, logical or other.
                'emotional' - if the message reqires an emotioonal response (therapist)
                'logical' - if the message reqires a logical response (engineer)
                'other' - if the message reqires a response that is neither emotional nor logical
                '''
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ]
    )
    return {"message_types": response.message_type}
    
def router(state: State):
    message_type = state.get("message_types")
    if message_type == "emotional":
        return {"next": "therapist_agent"}
    elif message_type == "logical":
        return {"next": "engineer_agent"}
    else:
        return {"next": "other_agent"}
    

def therapist_agent(state: State):
    last_message = state["message"][-1]
    message = [
        {
            "role": "system", 
            "content": 
            """
                You are a compassionate therapist. 
                Respond to the user's message with empathy and understanding. 
                Focus on emotional aspects of the user's message. 
                Show empathy, validate their feelings and help them process their emotions. 
                Ask open ended questions to encourage them to share more about their feelings and experiences.
                Avoid giving logical solutions unless explicitly asked.
            """
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    response = llm.invoke(message)
    return {"message": [{"role": "assistant", "content": response.content}]}

def engineer_agent(state: State):
    last_message = state["message"][-1]
    message = [
        {
            "role": "system", 
            "content": 
            """
                You are a purely logical assistant. 
                Focus only on facts and information.
                Provide clear, concise answers based on logic and evidence. 
                Do not address emotions or provide emotional support.
                Be direct and straightforward in your responses.
            """
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    response = llm.invoke(message)
    return {"message": [{"role": "assistant", "content": response.content}]}

def other_agent(state: State):
    last_message = state["message"][-1]
    message = [
        {
            "role": "system", 
            "content": 
            """
                You are a neutral assistant. 
                Focus only on information.
                Be direct and straightforward in your responses.
            """
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    response = llm.invoke(message)
    return {"message": [{"role": "assistant", "content": response.content}]}



graph_builder = StateGraph(State)


# Add node
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist_agent", therapist_agent)
graph_builder.add_node("engineer_agent", engineer_agent)
graph_builder.add_node("other_agent", other_agent)

graph_builder.add_edge(START, end_key="classify_message")
graph_builder.add_edge(start_key="classify_message", end_key="router")

def route_fn(state):
    #print("STATE:", state)
    return state.get("next")

graph_builder.add_conditional_edges(
    "router",
    route_fn,
    {
        "therapist_agent": "therapist_agent",
        "engineer_agent": "engineer_agent",
        "other_agent": "other_agent"
    }
)

graph_builder.add_edge(start_key="therapist_agent", end_key=END)
graph_builder.add_edge(start_key="engineer_agent", end_key=END)
graph_builder.add_edge(start_key="other_agent", end_key=END)


# Compile the graph
graph = graph_builder.compile()

def run_chatbot():
    state = {"message": [], "message_types": None}
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting...\nBye")
            break

        state["message"] = state.get("message", []) + [{"role": "user", "content": user_input}]
        response = graph.invoke(state)

        if response.get("message") and len(response["message"]) > 0:
            last_message = response["message"][-1]
            print(f"Assistant: {last_message.content}")
            
from fastapi import FastAPI

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    response = graph.invoke({
        "message": [{"role": "user", "content": req.message}]
    })
    return {"response": response["message"][-1].content}

if __name__ == "__main__":
    # CLI mode (optional)
    while True:
        user_input = input("You: ")
        response = graph.invoke({
            "message": [{"role": "user", "content": user_input}]
        })
        print(response["message"][-1].content)

