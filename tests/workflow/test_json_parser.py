import json
import pytest
from hypothesis import given, strategies as st
from workflow.json_parser import JSONParser
from workflow.json_parser import ParseError

class TestJSONParser:

    @given(st.dictionaries(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.one_of(
            st.text(min_size=1, max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.lists(st.text(min_size=1, max_size=20), max_size=10)
        ),
        min_size=1,
        max_size=20
    ))
    def test_json_parsing_correctness(self, workflow_data):
        json_string = json.dumps(workflow_data)
        parsed_data = JSONParser.parse(json_string)
        assert parsed_data == workflow_data

    def test_parse_empty_string(self):
        with pytest.raises(ParseError) as exc_info:
            JSONParser.parse("")
        assert "cannot be empty" in str(exc_info.value)

    def test_parse_none_value(self):
        with pytest.raises(ParseError) as exc_info:
            JSONParser.parse(None)
        assert "cannot be None" in str(exc_info.value)

    def test_parse_malformed_json(self):
        malformed_json = '{"key": "value", "invalid": }'
        with pytest.raises(ParseError) as exc_info:
            JSONParser.parse(malformed_json)

        error = exc_info.value
        assert "Invalid JSON" in str(error)
        assert error.line is not None
        assert error.column is not None

    def test_parse_invalid_json_syntax(self):
        invalid_jsons = [
            '{"key": }',
            '{"key": "value",}',
            '{key: "value"}',
            '{"key": "value"',
            'not json at all'
        ]

        for invalid_json in invalid_jsons:
            with pytest.raises(ParseError):
                JSONParser.parse(invalid_json)

    def test_to_string_none_data(self):
        with pytest.raises(ParseError) as exc_info:
            JSONParser.to_string(None)
        assert "cannot be None" in str(exc_info.value)

    def test_to_string_valid_data(self):
        data = {"key": "value", "number": 42}
        result = JSONParser.to_string(data)

        assert isinstance(result, str)
        parsed_back = json.loads(result)
        assert parsed_back == data
