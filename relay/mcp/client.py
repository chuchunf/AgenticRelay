from typing import List, Callable, Dict
import httpx
from langchain_core.tools import tool as langchain_tool

class MCPClient:
    def __init__(self, server_url: str = "http://localhost:8000/mcp"):
        self.server_url = server_url
        self.client = httpx.Client(timeout=30.0)
        self._tools = {}
        self._message_id = 0
        
        self._discover_tools()
    
    def _get_next_id(self) -> int:
        self._message_id += 1
        return self._message_id
    
    def _send_jsonrpc_request(self, method: str, params: dict = None) -> dict:
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        try:
            response = self.client.post(
                self.server_url,
                json=request_data,
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    raise Exception(f"MCP error: {data['error']}")
                return data.get("result", {})
            else:
                return {}
        except Exception as e:
            return {}
    
    def _discover_tools(self):
        try:
            result = self._send_jsonrpc_request("tools/list")
            tools_list = result.get("tools", [])
            
            if tools_list:
                for tool_info in tools_list:
                    tool_name = tool_info.get("name")
                    tool_description = tool_info.get("description", "")
                    
                    langchain_tool_wrapper = self._create_langchain_tool(tool_name, tool_description)
                    self._tools[tool_name] = langchain_tool_wrapper

            raise ValueError("No tools found")                
        except Exception as e:
            raise ValueError("Failed to discover tools", e)
        
    def _create_langchain_tool(self, tool_name: str, tool_description: str):
        client = self
        
        def tool_function(**kwargs) -> str:
            try:
                result = client._send_jsonrpc_request("tools/call", {
                    "name": tool_name,
                    "arguments": kwargs
                })
                
                content = result.get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", str(result))
                return str(result)
            except Exception as e:
                return f"Error calling tool {tool_name}: {e}"
        
        tool_function.__name__ = tool_name
        tool_function.__doc__ = tool_description or f"MCP tool: {tool_name}"
        
        return langchain_tool(tool_function)
    
    def get_tools(self) -> List[Callable]:
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> Callable:
        return self._tools[tool_name]
    
    def get_tool_names(self) -> List[str]:
        return list(self._tools.keys())
    
    def close(self):
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
