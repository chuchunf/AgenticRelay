from fastmcp import FastMCP

mcp = FastMCP("ComparisonServer")

def compare_numbers(num1: str, num2: str) -> str:
    try:
        value1 = float(num1)
        value2 = float(num2)
        
        if value1 > value2:
            return num1
        elif value2 > value1:
            return num2
        else:
            return f"{num1} (both are equal)"
            
    except ValueError as e:
        raise ValueError(f"Invalid number format: {e}")


@mcp.tool()
def compare(num1: str, num2: str) -> str:
    return compare_numbers(num1, num2)


if __name__ == "__main__":
    mcp.run()
