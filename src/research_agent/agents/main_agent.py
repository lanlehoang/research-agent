from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import BaseMessage, add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command, Send, Interrupt
from pydantic import BaseModel, Field
from typing import List, Optional


class AgentState(StateGraph):
    messages: List[str]