import os
from typing import Sequence

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from configer import Configer
from logger import Logger
from skills import SkillsManager


class LLM:

    def __init__(self):
        self.logger = Logger(__name__)
        self._configer = Configer()
        self._skill_manager = SkillsManager()
        self._model = self._init_llm_model()


    def _init_llm_model(self):
        os.environ["GOOGLE_API_KEY"] = self._configer.get('GOOGLE_API_KEY')

        model = ChatGoogleGenerativeAI(model=self._configer.get('GOOGLE_MODEL_NAME'))
        return model


    def get_agent(self, skill_name: str|None = None, tools: Sequence|None = None ):
        skill = self._skill_manager.get_skill(skill_name) if skill_name \
            else "You are an assistant, please help user with follow request."

        agent = create_agent(
            self._model,
            tools=tools,
            system_prompt=SystemMessage(
                content=[
                    {
                        "type": "text",
                        "text": repr(skill),
                    },
                ]
            ),
            checkpointer=InMemorySaver(),
        )

        return agent







