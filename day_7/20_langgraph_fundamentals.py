# State - A shared data structure that holds the current information or context 
#           of an entire application (like an application's memory, keeping track of variables)

# Nodes - Individual functions or operations that perform specific tasks within the graph

# Graph - A structure which maps out how different tasks(nodes) are connected and executed
#         Graph visually represents the workflow 

# Edges - connections between nodes that determine the flow of execution 

# Conditional edges - specialized connections that decide the next node to execute based on 
#                     specific conditions or logic applied to the current state 

#StateGraph - a class used in langGraph to build and compile graph structure 



# sample workflow 

from typing import TypedDict
from langgraph.graph import StateGraph

# create the agent state           
class AgentState(TypedDict):
    message : str


def greeting_node(state:AgentState):
    """ Simple node that adds a greeting message to the agent state"""
    state['message'] = "Hey " + state["message"] + ", How is your day going?"
    return state

# create the graph flow 
graph = StateGraph(AgentState)

graph.add_node("greeter",greeting_node)
graph.set_entry_point("greeter")
graph.set_finish_point("greeter")

app = graph.compile()
result = app.invoke({"message":"Arib"})
print(result["message"])

# GRAPH FLOW 
# START                   ___start____
#  ↓                           ↓
# Node                     greeter
#  ↓                           ↓
# End                      ___end___

from IPython.display import Image,display
# display(Image(app.get_graph().draw_mermaid_png()))

with open("graph.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())  #display the images 
