from langchain.chat_models import init_chat_model

# main llm model
llm = init_chat_model(
    model="ollama:llama3",
    temperature=0.3
)

# separate moderation model
moderationllm = init_chat_model(
    model="ollama:llama3",
    temperature=0
)