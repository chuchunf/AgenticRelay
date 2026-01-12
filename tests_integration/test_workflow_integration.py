from agent.workflow import Workflow

from langchain_core.globals import set_debug, set_verbose

set_verbose(True)
set_debug(True)

class TestWorkflowIntegration:

    def test_workflow(self):
        workflow = Workflow()

        result = workflow.process("""
{
    "id": "exchange-rate-comparison-workflow",
    "steps": [
        {
            "id": "fetch-awesomeapi-data",
            "type": "action",
            "name": "Send GET request to AwesomeAPI and extract the bid value from the response",
            "next": "fetch-frankfurter-api-data"
        },
        {
            "id": "fetch-frankfurter-api-data",
            "type": "action",
            "name": "Send GET request to Frankfurter API and extract the target rate value from the response",
            "next": "process-and-select-optimal-rate"
        },
        {
            "id": "process-and-select-optimal-rate",
            "type": "action",
            "name": "Convert extracted values to float and select the optimal rate based on conversion or cost objective",
            "next": "monitor-and-handle-errors"
        }
    ]
}        
        """,
                                  "SGD-USD")

        print(f"{result}")
        assert result