from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes import research_agent, analysis_agent, writer_agent, critic_agent


def should_continue_revisions(state: AgentState) -> str:
    if state.get("approved", False):
        return "end"
    if state.get("revision_count", 0) >= 3:
        return "end"
    return "continue"


workflow = StateGraph(AgentState)

workflow.add_node("research", research_agent)
workflow.add_node("analysis", analysis_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("critic", critic_agent)

workflow.set_entry_point("research")
workflow.add_edge("research", "analysis")
workflow.add_edge("analysis", "writer")

workflow.add_edge("writer", "critic")

workflow.add_conditional_edges(
    "critic",
    should_continue_revisions,
    {
        "continue": "writer",
        "end": END
    }
)

checkpointer = MemorySaver()
master_graph = workflow.compile(checkpointer=checkpointer, interrupt_before=["writer"])
