from fastapi import FastAPI
from context_handler import extract_user_info, get_session_memory, build_context
from moderations import moderate_message
from evaluation import evaluate_output
from schema import ChatRequest
from graph import graph

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    session = get_session_memory(req.session_id)

    session["messages"].append({"role": "user", "content": req.message})

    profile_update = extract_user_info(req.message)
    if profile_update.name:
        session["profile"]["name"] = profile_update.name

    context = build_context(session)

    # 🔴 INPUT MODERATION
    moderation_result = moderate_message(req.message)
    if not moderation_result.is_safe:
        return {
            "response": f"⚠️ Your message was flagged: {moderation_result.reason}"
        }

    # ✅ Normal flow
    response = graph.invoke({
        "message": context
    })
    
    bot_response = response["message"][-1].content
    moderation_result = moderate_message(bot_response)
    if not moderation_result.is_safe:
        return {
            "response": f"⚠️ Bot response was flagged: {moderation_result.reason}"
        }

    eval_result = evaluate_output(context, bot_response)

    if not eval_result.is_safe:
        return {
            "response": "⚠️ Bot response was flagged: ", "reason": eval_result.safety_reason
        }
    
    session["messages"].append({"role": "assistant", "content": bot_response})

    return {"response": bot_response, "evaluation": eval_result.dict()}

if __name__ == "__main__":
    # CLI mode (optional)
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = graph.invoke({
            "message": [{"role": "user", "content": user_input}]
        })
        print(f"Assistant: {response['message'][-1].content}")
