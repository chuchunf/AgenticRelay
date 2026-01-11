from typing import TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent import get_response_or_raise
from agent.llm import LLM


class SOPState(TypedDict):
    messages: list[AnyMessage]
    # messages: Annotated[list[AnyMessage], operator.add]

class SOP:
    def __init__(self):
        self.llm = LLM()
        self.agent_ba = self.llm.get_agent('business_analysis')
        self.agent_dev = self.llm.get_agent('development')


    def re_write(self, state:SOPState):
        result = self.agent_ba.invoke(
            {"messages":[HumanMessage(state["messages"])]}
        )

        return get_response_or_raise(result)

    def generate_workflow(self, state:SOPState):
        result = self.agent_dev.invoke(
            {"messages":[HumanMessage(state["messages"])]}
        )

        return get_response_or_raise(result)

    def process(self, sop: str)->str:
        workflow = (
            StateGraph(SOPState)
            .add_node("rewrite", self.re_write)
            .add_node("generate", self.generate_workflow)
            .add_edge(START, "rewrite")
            .add_edge("rewrite", "generate")
            .add_edge("generate", END)
            .compile()
        )

        result = workflow.invoke({
            "messages": [sop]
        })

        if 'messages' in result:
            messages = result['messages']
            return messages[0]

        raise ValueError("failed to generate response")

