import operator
from typing import TypedDict, Annotated

import requests
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.llm import LLM
from json_parser import JSONParser


class WorkflowState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Workflow:
    def __init__(self):
        self.llm = LLM()

    @staticmethod
    @tool
    def search_frankfurter(pair: str) -> str|None:
        """
        Searches the frankurter API with a currency pair to get the exchange rate
        :param pair: currency pair as string
        :return: exchange rate as string
        """
        url = f"https://economia.awesomeapi.com.br/json/last/{pair}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            result = data.get("SGDUSD", {})

            return result.get("ask", None)

        except requests.exceptions.RequestException as e:
            return None


    @staticmethod
    @tool
    def search_awesomepai(pair: str) -> str|None:
        """
        Searches the awsomeapi API with a currency pair to get the exchange rate
        :param pair: currency pair as string
        :return: exchange rate as string
        """
        base, target = pair.split("-")
        url = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={target}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            result = data.get("rates", {})

            return result.get(f"{target}", None)

        except requests.exceptions.RequestException as e:
            return None


    def get_tool(self, step_id: str):
        if step_id == 'fetch-awesomeapi-data':
            return self.search_frankfurter
        elif step_id == 'fetch-frankfurter-api-data':
            return self.search_awesomepai
        return None

    def get_step(self, step_id: str, name: str):
        llm_tool = self.get_tool(step_id)
        agent = self.llm.get_agent(
            tools = [llm_tool] if llm_tool else []
        )

        def do_step(state:WorkflowState):
            result = agent.invoke(
                {
                    "messages":[HumanMessage(state["messages"])]
                               + ([HumanMessage(name)] if not llm_tool else [])
                }
            )

            return {"messages": [result]}

        return do_step

    def process(self, workflow:str, pair:str) -> str:
        workflow_json = JSONParser.parse(workflow)
        workflow = StateGraph(WorkflowState)

        steps = workflow_json.get("steps", [])
        orders = [START]

        for step in steps:
            step_id = step.get("id")
            name = step.get("name")
            workflow = workflow.add_node(
                step_id,
                self.get_step(step_id, name)
            )
            orders.append(step_id)
        orders.append(END)

        for i in range(len(orders) - 1):
            current_step = orders[i]
            next_step = orders[i+1]
            workflow = workflow.add_edge(current_step, next_step)

        workflow = workflow.compile()

        result = workflow.invoke({
            "messages": [pair]
        })

        if 'messages' in result:
            messages = result['messages']
            return messages[-1]

        raise ValueError("failed to generate response")
