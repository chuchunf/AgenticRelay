"""Example demonstrating the MCP client's dictionary-based tool access."""
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from relay.mcp.client import MCPClient

def main():
    print("MCP Client - Dictionary-based Tool Access Example")
    print("=" * 50)
    
    # Create client (using fallback since server may not be running)
    client = MCPClient(server_url="http://localhost:8000")
    
    # Get all tool names
    print("\n1. Get all tool names:")
    tool_names = client.get_tool_names()
    print(f"   Available tools: {tool_names}")
    
    # Get all tools as a list (for LangChain agents)
    print("\n2. Get all tools as list:")
    tools = client.get_tools()
    print(f"   Number of tools: {len(tools)}")
    
    # Get a specific tool by name
    print("\n3. Get specific tool by name:")
    if "compare" in tool_names:
        compare_tool = client.get_tool("compare")
        print(f"   Tool name: {compare_tool.name}")
        print(f"   Tool description: {compare_tool.description}")
        
        # Use the tool
        print("\n4. Use the tool:")
        result = compare_tool.invoke({"num1": "100", "num2": "50"})
        print(f"   compare(100, 50) = {result}")
    
    # Close the client
    client.close()
    
    print("\n" + "=" * 50)
    print("Example completed!")

if __name__ == "__main__":
    main()
