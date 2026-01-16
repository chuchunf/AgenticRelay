"""Test script for MCP client."""
import time
import subprocess
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from relay.mcp.client import MCPClient

def test_mcp_client():
    """Test the MCP client by connecting to the server and calling tools."""
    
    print("Starting MCP server...")
    # Start the MCP server in the background
    server_process = subprocess.Popen(
        [sys.executable, "relay/mcp/server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        print("Connecting to MCP server...")
        # Create MCP client
        with MCPClient(server_url="http://localhost:8000") as client:
            print(f"Connected! Discovered {len(client.get_tools())} tools")
            
            # Get the tools
            tools = client.get_tools()
            
            # Print available tools
            print("\nAvailable tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test the compare tool
            print("\nTesting compare tool...")
            if tools:
                compare_tool = tools[0]  # Assuming compare is the first tool
                
                # Test cases
                test_cases = [
                    {"num1": "10", "num2": "5"},
                    {"num1": "3.14", "num2": "2.71"},
                    {"num1": "-5", "num2": "-10"},
                    {"num1": "42", "num2": "42"},
                ]
                
                for test_case in test_cases:
                    result = compare_tool.invoke(test_case)
                    print(f"  compare({test_case['num1']}, {test_case['num2']}) = {result}")
            
            print("\n[PASS] All tests passed!")
            
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop the server
        print("\nStopping MCP server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_mcp_client()
