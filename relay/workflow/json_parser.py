import json
from typing import Dict, Any


class ParseError(Exception):
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column

class ValidationError(Exception):
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field

class JSONParser:
    @staticmethod
    def parse(json_string: str) -> Dict[str, Any]:
        if json_string is None:
            raise ParseError("JSON string cannot be None")

        if json_string == "":
            raise ParseError("JSON string cannot be empty")

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ParseError(
                f"Invalid JSON: {e.msg}",
                line=e.lineno,
                column=e.colno
            )

    @staticmethod
    def to_string(data: Dict[str, Any]) -> str:
        if data is None:
            raise ParseError("Data cannot be None")

        try:
            return json.dumps(data, indent=2, sort_keys=True)
        except (TypeError, ValueError) as e:
            raise ParseError(f"Failed to serialize data to JSON: {str(e)}")
