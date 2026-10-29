from langgraph.graph import StateGraph, START, END
from backend.state import AgentState
from backend.agents.planner import planner_agent
from backend.agents.designer import designer_agent
from backend.agents.coder import coder_agent
from backend.agents.tester import test_engine_agent
from backend.agents.repair import repair_agent
from backend.graph.approval import human_approval_node
from backend.graph.routing import route_after_test, route_after_approval
from backend.services.website_files import save_final

def save_final_agent(state: AgentState, config):
    save_final(state, str(config["configurable"]["thread_id"]))
    return {"approved": True}

def build_graph(checkpointer):
    builder = StateGraph(AgentState)
    builder.add_node("planner", planner_agent)
    builder.add_node("designer", designer_agent)
    builder.add_node("coder", coder_agent)
    builder.add_node("tester", test_engine_agent)
    builder.add_node("repair", repair_agent)
    builder.add_node("approval", human_approval_node)
    builder.add_node("save", save_final_agent)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "designer")
    builder.add_edge("designer", "coder")
    builder.add_edge("coder", "tester")
    builder.add_conditional_edges("tester", route_after_test, {"approval": "approval", "repair": "repair"})
    builder.add_edge("repair", "tester")
    builder.add_conditional_edges("approval", route_after_approval, {"save": "save", "repair": "repair", "end": END})
    builder.add_edge("save", END)
    return builder.compile(checkpointer=checkpointer)
