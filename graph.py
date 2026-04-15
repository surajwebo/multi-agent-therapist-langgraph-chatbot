from langgraph.graph import StateGraph, START, END
from schema import State
from nodes import (
    classify_message, 
    router, 
    therapist_agent, 
    engineer_agent, 
    other_agent, 
    route_fn
)

def create_graph():
    graph_builder = StateGraph(State)

    # Add nodes
    graph_builder.add_node("classify_message", classify_message)
    graph_builder.add_node("router", router)
    graph_builder.add_node("therapist_agent", therapist_agent)
    graph_builder.add_node("engineer_agent", engineer_agent)
    graph_builder.add_node("other_agent", other_agent)

    # Add edges
    graph_builder.add_edge(START, "classify_message")
    graph_builder.add_edge("classify_message", "router")

    graph_builder.add_conditional_edges(
        "router",
        route_fn,
        {
            "therapist_agent": "therapist_agent",
            "engineer_agent": "engineer_agent",
            "other_agent": "other_agent"
        }
    )

    graph_builder.add_edge("therapist_agent", END)
    graph_builder.add_edge("engineer_agent", END)
    graph_builder.add_edge("other_agent", END)

    return graph_builder.compile()

graph = create_graph()
