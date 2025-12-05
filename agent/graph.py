from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.extract_node import extract_node
from nodes.planner_node import planner_node
from nodes.clarification_node import clarification_node
from nodes.executor_node import executor_node


def should_continue_to_executor(state: AgentState) -> str:
    """Route to executor or end based on clarification need."""
    if state.get("needs_clarification"):
        return "end"
    return "executor"


def create_agent_graph():
    """Build the LangGraph workflow: extract → planner → clarification → executor."""
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("extract", extract_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("executor", executor_node)
    
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "planner")
    workflow.add_edge("planner", "clarification")
    workflow.add_conditional_edges(
        "clarification",
        should_continue_to_executor,
        {"executor": "executor", "end": END}
    )
    workflow.add_edge("executor", END)
    
    return workflow.compile()
