import os
from typing import TypedDict , Annotated , List
from langgraph.graph import StateGraph , END
from langchain_core.messages import HumanMessage , AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image

class Plannerstate(TypedDict):
    messages : Annotated[List[HumanMessage | AIMessage], "This is the message"]
    city: str
    interests: list[str]
    itinerary: str

from langchain_groq import ChatGroq
llm = ChatGroq(
    temperature=0,
    groq_api_key = "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",
    model_name = "llama-3.3-70b-versatile")
itinerary_prompt = ChatPromptTemplate.from_messages(
    [("system","you are a helpful travel assistant.create a day trip for itinerary for {city} based on user's interests:{interests}. provide a brief bulleted itinerary"),("human","create an itinerary for my day trip")]
) 
def input_city(state:Plannerstate) -> Plannerstate:
    print(f"please enter the city you want to visit for your day trip")
    user_message = input("Your Input: ")
    return{
    **state,
    "city": user_message,
    "messages": state['messages']+ [HumanMessage(content=user_message)]
}
def input_interests(state:Plannerstate) -> Plannerstate:
    print(f"please enter your interests : {state['city']} (comma-seperated)")
    user_message = input("Your Input: ")
    return{
    **state,
    "interests": [interests.strip() for interests in user_message.split(",")],
    "messages": state['messages']+ [HumanMessage(content=user_message)]
}
def create_itinerary(state:Plannerstate) -> Plannerstate:
    print(f"create an itinerary for {state['city']} based on interests : {', '.join(state['interests'])}")
    response = llm.invoke(itinerary_prompt.format_messages(
    city=state['city'], interests=', '.join(state['interests'])
))

    print("\nfinal itinerary :")
    print(response.content)
    return{
    **state, 
    "messages": state['messages']+ [AIMessage(content=response.content)],"itinerary": response.content}

workflow = StateGraph(Plannerstate)
workflow.add_node("input_city",input_city)
workflow.add_node("input_interests",input_interests)
workflow.add_node("create_itinerary",create_itinerary)
workflow.set_entry_point("input_city")
workflow.add_edge("input_city","input_interests")
workflow.add_edge("input_interests","create_itinerary")
workflow.add_edge("create_itinerary",END)
app = workflow.compile()

display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method = MermaidDrawMethod.API
        )
    )
)

def travel_planner(user_request:str):
        print(f"Initial Request :{user_request}\n")
        state = {
            "messages" : [HumanMessage(content=user_request)],
            "city":"",
            "interests": [],
            "itinerary":"",
        }
        for output in app.stream(state):
            pass
user_request = "I want to plan a day trip"
travel_planner(user_request)

import gradio as gr
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# 🧠 Define state structure
class Plannerstate(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "This is the message"]
    city: str
    interests: list[str]
    itinerary: str

# 🔑 LLM setup
llm = ChatGroq(
    temperature=0,
    groq_api_key="your_groq_api_key_here",  # Replace this securely
    model_name="llama-3-3-70b-versatile"
)

# ✏️ Prompt template
itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a day trip itinerary for {city} based on the user's interests: {interests}. Provide a brief bulleted itinerary."),
    ("human", "Create an itinerary for my day trip")
])

# ✅ Helper functions
def input_city(city: str, state: Plannerstate) -> Plannerstate:
    return {
        **state,
        "city": city,
        "messages": state['messages'] + [HumanMessage(content=city)]
    }

def input_interests(interests: str, state: Plannerstate) -> Plannerstate:
    return {
        **state,
        "interests": [i.strip() for i in interests.split(",")],
        "messages": state['messages'] + [HumanMessage(content=interests)]
    }

def create_itinerary(state: Plannerstate) -> str:
    response = llm.invoke(itinerary_prompt.format_messages(
        city=state['city'],
        interests=', '.join(state['interests'])
    ))
    state["itinerary"] = response.content
    state["messages"] += [AIMessage(content=response.content)]
    return response.content  # ✨ This is what Gradio will display

# 🌐 Gradio-connected function
def travel_planner(city: str, interests: str):
    state = {
        "messages": [],
        "city": "",
        "interests": [],
        "itinerary": "",
    }
    state = input_city(city, state)
    state = input_interests(interests, state)
    return create_itinerary(state)

# 🚀 Gradio UI setup
interface = gr.Interface(
    fn=travel_planner,
    inputs=[
        gr.Textbox(label="Enter the city for your day trip"),
        gr.Textbox(label="Enter your interests (comma-separated)"),
    ],
    outputs=gr.Textbox(label="Generated itinerary"),
    title="🧳 Travel Itinerary Planner",
    description="Enter a city and your interests to generate a travel itinerary for your day trip.",
    theme='Yntec/HaleyCH_Theme_Orange_Green',  # Optional, if theme installed
)

if __name__ == "__main__":
    interface.launch(share=True)  # Use `share=True` to get a public link



