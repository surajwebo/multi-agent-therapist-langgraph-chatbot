from llm_provider import llm
from schema import MessageClassifier, State

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
    messages = state["message"]
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
    ] + messages
    response = llm.invoke(message)
    return {"message": [{"role": "assistant", "content": response.content}]}

def engineer_agent(state: State):
    messages = state["message"]
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
    ] + messages
    response = llm.invoke(message)
    return {"message": [{"role": "assistant", "content": response.content}]}

def other_agent(state: State):
    messages = state["message"]
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
    ] + messages
    response = llm.invoke(message)
    return {"message": [{"role": "assistant", "content": response.content}]}

def route_fn(state):
    return state.get("next")
