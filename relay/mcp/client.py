from typing import List, Callable, Dict
import httpx
from langchain_core.tools import tool as langchain_tool

class MCPClient:
    """
    Simple MCP client that connects to an MCP server via HTTP and exposes tools as LangChain tools.
    
    This is a simplified implementation that makes direct HTTP calls to the MCP server
    using JSON-RPC protocol.
    """
    
    def __init__(self, server_url: str = "http://localhost:8000/mcp"):
        """
        Initialize the MCP client.
        
        Args:
            server_url: URL of the MCP server (default: http://localhost:8000/mcp)
        """
        self.server_url = server_url
        self.client = httpx.Client(timeout=30.0)
        self._tools = {}  # Changed to dict for key-value storage
        self._message_id = 0
        
        # Discover and wrap tools
        self._discover_tools()
    
    def _get_next_id(self) -> int:
        """Get next message ID for JSON-RPC."""
        self._message_id += 1
        return self._message_id
    
    def _send_jsonrpc_request(self, method: str, params: dict = None) -> dict:
        """
        Send a JSON-RPC request to the MCP server.
        
        Args:
            method: The JSON-RPC method name
            params: The parameters for the method
            
        Returns:
            The JSON-RPC response result
        """
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
            
            # Check if we got a valid response
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    raise Exception(f"MCP error: {data['error']}")
                return data.get("result", {})
            else:
                # If JSON-RPC doesn't work, return empty result
                return {}
        except Exception as e:
            print(f"Warning: Could not connect to MCP server: {e}")
            return {}
    
    def _discover_tools(self):
        """Discover available tools from the MCP server."""
        try:
            # Try to list tools via JSON-RPC
            result = self._send_jsonrpc_request("tools/list")
            tools_list = result.get("tools", [])
            
            if tools_list:
                # Create LangChain tool wrappers for each MCP tool
                for tool_info in tools_list:
                    tool_name = tool_info.get("name")
                    tool_description = tool_info.get("description", "")
                    
                    langchain_tool_wrapper = self._create_langchain_tool(tool_name, tool_description)
                    self._tools[tool_name] = langchain_tool_wrapper
            else:
                # Fallback: create a default compare tool if server doesn't respond
                print("Note: Using fallback tool creation")
                self._create_fallback_tools()
                
        except Exception as e:
            print(f"Warning: Tool discovery failed: {e}. Using fallback tools.")
            self._create_fallback_tools()
    
    def _create_fallback_tools(self):
        """Create fallback tools when server discovery fails."""
        # Create a compare tool that calls the server directly
        @langchain_tool
        def compare(num1: str, num2: str) -> str:
            """Compare two numbers and return the larger one."""
            try:
                result = self._send_jsonrpc_request("tools/call", {
                    "name": "compare",
                    "arguments": {"num1": num1, "num2": num2}
                })
                
                content = result.get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", str(result))
                return str(result)
            except Exception as e:
                # Fallback to local comparison if server call fails
                try:
                    val1, val2 = float(num1), float(num2)
                    if val1 > val2:
                        return num1
                    elif val2 > val1:
                        return num2
                    else:
                        return f"{num1} (both are equal)"
                except:
                    return f"Error: {e}"
        
        self._tools["compare"] = compare
    
    def _create_langchain_tool(self, tool_name: str, tool_description: str):
        """
        Create a LangChain tool wrapper for an MCP tool.
        
        Args:
            tool_name: Name of the MCP tool
            tool_description: Description of the tool
        
        Returns:
            A LangChain tool function
        """
        client = self
        
        def tool_function(**kwargs) -> str:
            """Dynamically created tool function that calls the MCP server."""
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
        """
        Get all discovered tools as LangChain-compatible tools.
        
        Returns:
            List of LangChain tool functions
        """
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> Callable:
        """
        Get a specific tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            The LangChain tool function
            
        Raises:
            KeyError: If tool not found
        """
        return self._tools[tool_name]
    
    def get_tool_names(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
