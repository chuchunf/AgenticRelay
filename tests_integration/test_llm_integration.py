import uuid

from langchain_core.globals import set_debug, set_verbose

from relay.agent.llm import LLM

set_verbose(True)
set_debug(True)

class TestLLMIntegration:

    def test_llm_connectivity(self):
        llm = LLM()
        agent = llm.get_agent()

        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "which model are you using?",
                    }
                ]
            },
            config
        )

        assert result is not None
        assert len(result) > 0
        assert "messages" in result
        messages = result["messages"]
        assert len(messages) == 2
        ai_message = messages[1]
        assert ai_message is not None
        text = ai_message.text
        assert text == 'I am a large language model, trained by Google.'
