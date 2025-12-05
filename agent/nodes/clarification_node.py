from state import AgentState


def clarification_node(state: AgentState) -> AgentState:
    """Stop execution if clarification is needed, otherwise continue."""
    
    if state.get("needs_clarification"):
        return {**state, "final_result": None}
    
    return state
