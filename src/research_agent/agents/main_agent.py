from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import BaseMessage, add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command, Send, Interrupt
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from research_agent.config import settings


class AgentState(StateGraph):
    messages: Annotated[List[BaseMessage], add_messages]


class ResearchAgent(StateGraph):
    def __init__(self):
        super().__init__(AgentState)
        self._build_graph()

    def _build_graph(self):
        pass