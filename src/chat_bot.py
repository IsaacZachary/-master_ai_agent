from typing import List
import openai
from src.nodes import simulated_user_node, chat_bot_node, should_continue
from langgraph.graph import END, MessageGraph
from langgraph.checkpoint.sqlite import SqliteSaver

def my_chat_bot(messages: List[dict]) -> dict:
    system_message = {
        "role": "system",
        "content": "You are a customer support agent for a product company.",
    }
    messages = [system_message] + messages
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message

def run_chatbot():
    graph_message = MessageGraph()
    graph_message.add_node("user", simulated_user_node)
    graph_message.add_node("chat_bot", chat_bot_node)

    graph_message.set_entry_point("chat_bot")

    graph_message.add_edge("chat_bot", "user")
    graph_message.add_conditional_edges(
        "user",
        should_continue,
        {
            "end": END,
            "continue": "chat_bot",
        },
    )

    memory = SqliteSaver.from_conn_string(":memory:")
    graph_1 = graph_message.compile(checkpointer=memory)

    initial_message = {"role": "user", "content": "Hi, How are you?"}
    config = {"configurable": {"thread_id": "1", 'thread_ts': "2"}}
    
    for chunk in graph_1.stream({"role": "user", "content": initial_message["content"]}, config, stream_mode="values"):
        if END not in chunk:
            print(chunk)
            print("--------------------------------------------------------------------------------")
