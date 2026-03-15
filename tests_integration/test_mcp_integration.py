import time
import subprocess
import sys
import pytest
from relay.mcp.client import MCPClient


class TestMCPClientIntegration:
    @pytest.fixture(scope="class")
    def mcp_server(self):
        print("\nStarting MCP server...")
        server_process = subprocess.Popen(
            [sys.executable, "relay/mcp/server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        yield server_process
        
        print("\nStopping MCP server...")
        server_process.terminate()
        server_process.wait()
    
    def test_client_connection(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            assert client is not None
            tools = client.get_tools()
            assert len(tools) > 0
    
    def test_tool_discovery(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            tool_names = client.get_tool_names()
            assert "compare" in tool_names
            assert len(tool_names) == 1
    
    def test_get_tools_list(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            tools = client.get_tools()
            assert isinstance(tools, list)
            assert len(tools) == 1
            assert tools[0].name == "compare"
    
    def test_get_tool_by_name(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            compare_tool = client.get_tool("compare")
            assert compare_tool is not None
            assert compare_tool.name == "compare"
            assert "compare" in compare_tool.description.lower() or "number" in compare_tool.description.lower()
    
    def test_get_tool_names(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            tool_names = client.get_tool_names()
            assert isinstance(tool_names, list)
            assert "compare" in tool_names
    
    def test_tool_invocation(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            compare_tool = client.get_tool("compare")
            
            test_cases = [
                ({"num1": "10", "num2": "5"}, "10"),
                ({"num1": "3.14", "num2": "2.71"}, "3.14"),
                ({"num1": "-5", "num2": "-10"}, "-5"),
            ]
            
            for args, expected in test_cases:
                result = compare_tool.invoke(args)
                assert result is not None
    
    def test_multiple_tool_calls(self, mcp_server):
        with MCPClient(server_url="http://localhost:8000") as client:
            tools = client.get_tools()
            compare_tool = tools[0]
            
            for i in range(5):
                result = compare_tool.invoke({"num1": str(i), "num2": str(i+1)})
                assert result is not None
