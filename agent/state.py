from typing import TypedDict, NotRequired


class AgentState(TypedDict):
    topic: str
    search_results: NotRequired[list[dict]]
    analysis: NotRequired[str]
    draft_report: NotRequired[str]
    critic_feedback: NotRequired[str]
    revision_count: NotRequired[int]
    approved: NotRequired[bool]
