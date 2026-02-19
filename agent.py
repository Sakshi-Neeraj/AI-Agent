import asyncio
import json
import os
import re
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

def parse_user_input(user_input):
    """Parse user input and decide which tools to call"""
    user_lower = user_input.lower()
    tool_calls = []
    
    # Check if user wants to list files
    if any(keyword in user_lower for keyword in ["list", "show", "files", "what", "display"]):
        tool_calls.append({
            "tool": "list_files",
            "arguments": {}
        })
    
    # Check if user wants to create a file
    elif any(keyword in user_lower for keyword in ["create", "make", "new", "write"]):
        # Try to extract filename
        filename = None
        content = None
        
        # Look for patterns like "file called X" or "file X"
        file_match = re.search(r'(?:file|files?)\s+(?:called|named|path)?\s*["\']?([^"\'\s]+)["\']?', user_input, re.IGNORECASE)
        if file_match:
            filename = file_match.group(1)
        
        # Look for patterns like "with X" or "content X"
        content_match = re.search(r'(?:with|content|containing)\s+["\']?(.+?)["\']?(?:\s*$|\.)', user_input, re.IGNORECASE)
        if content_match:
            content = content_match.group(1).strip()
        
        # If we couldn't find filename, use a default
        if not filename:
            filename = "new_file.txt"
        
        # If we couldn't find content, use the full input
        if not content:
            content = user_input
        
        tool_calls.append({
            "tool": "create_file",
            "arguments": {
                "filename": filename,
                "content": content
            }
        })
    
    return tool_calls

async def run_agent():
    user_input = input("\nEnter your instruction: ")

    # Start the MCP server as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["git_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()
            
            tools = await session.list_tools()

            print("\nAvailable MCP tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print(f"\nUser request: {user_input}")
            
            # Parse user input without OpenAI
            tool_calls = parse_user_input(user_input)
            
            print(f"\nPlanned actions:")
            print(json.dumps({"tool_calls": tool_calls}, indent=2))

            # Execute the tool calls
            for tool_call in tool_calls:
                tool_name = tool_call["tool"]
                arguments = tool_call["arguments"]

                print(f"\nExecuting tool: {tool_name}")
                print(f"Arguments: {arguments}")

                try:
                    result = await session.call_tool(
                        tool_name,
                        arguments
                    )

                    # Display all results
                    if result.content:
                        for content in result.content:
                            print(f"Result: {content.text}")
                    else:
                        print("No result")
                except Exception as e:
                    print(f"Error executing tool: {e}")


if __name__ == "__main__":
    asyncio.run(run_agent())