import os
import sys
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Set up logging to stderr so it doesn't interfere with MCP communication
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)

load_dotenv()

# Use FOLDER_PATH from .env file
work_folder = os.getenv("FOLDER_PATH")
logger.info(f"Working folder: {work_folder}")

mcp = FastMCP("File MCP Server")

@mcp.tool()
def list_files() -> str:
    """List all files in the current folder"""
    try:
        files = os.listdir(work_folder)
        if not files:
            return "No files found"
        file_list = "\n".join([f"  - {f}" for f in files])
        logger.info(f"Listed {len(files)} files")
        return f"Files in {work_folder}:\n{file_list}"
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def create_file(filename: str, content: str) -> str:
    """Create a new file in the current folder with the given content"""
    try:
        path = os.path.join(work_folder, filename)

        with open(path, "w") as f:
            f.write(content)

        logger.info(f"Created file: {filename}")
        return f"File '{filename}' created successfully"
    except Exception as e:
        logger.error(f"Error creating file: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()