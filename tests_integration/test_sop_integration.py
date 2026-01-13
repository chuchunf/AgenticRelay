from langchain_core.globals import set_debug, set_verbose

from relay.agent.sop import SOP

set_verbose(True)
set_debug(True)

class TestSOPIntegration:

    def test_sop(self):
        sop = SOP()
        result = sop.process("""
SOP: Exchange Rate Comparison
1. Fetch AwesomeAPI
Endpoint: GET https://economia.awesomeapi.com.br/json/last/{BASE}-{TARGET}

Target Field: bid

2. Fetch Frankfurter
Endpoint: GET https://api.frankfurter.dev/v1/latest?base={BASE}&symbols={TARGET}

Target Field: rates.{TARGET}

3. Compare and Output
Normalization: Parse both results as floats.

Selection: Select the highest value (for conversion profit) or lowest value (for cost savings).

Error Handling: If one source fails, return the available rate as the fallback.       
        """)

        print(f"{result}")
        assert result
