from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.adapters.openai import convert_message_to_dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

def chat_bot_node(messages):
    messages = [convert_message_to_dict(m) for m in messages]
    chat_bot_response = my_chat_bot(messages)
    return AIMessage(content=chat_bot_response["content"])

def _swap_roles(messages):
    new_messages = []
    for m in messages:
        if isinstance(m, AIMessage):
            new_messages.append(HumanMessage(content=m.content))
        else:
            new_messages.append(AIMessage(content=m.content))
    return new_messages

def simulated_user_node(messages):
    system_prompt_template = """You are a customer of an organization that sells charging fans in Nigeria. \
    You are interacting with a user who is a customer support person in the organization. 

    {instructions}
    When you are finished with the conversation, respond with a single word 'TERMINATE'"""

    instructions = """Your name is Olasammy. You are trying to get a refund for the charging fan you bought.\
    You want them to give you ALL the money back. \
    You bought the fan 2 days back. \
    And it is not working properly after testing it."""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(name="Olasammy", instructions=instructions)

    model = ChatOpenAI()
    simulated_user = prompt | model

    new_messages = _swap_roles(messages)
    response = simulated_user.invoke({"messages": new_messages})
    return HumanMessage(content=response.content)

def should_continue(messages):
    if len(messages) > 6:
        return "end"
    elif messages[-1].content == "TERMINATE":
        return "end"
    else:
        return "continue"
