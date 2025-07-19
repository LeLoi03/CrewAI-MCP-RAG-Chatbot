import traceback
import httpx
import uuid
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"
class HTTPConferenceTool(BaseTool):
    """
    A CrewAI tool that communicates with a remote MCP server over HTTP.
    It acts as a true microservice client.
    """
    name: str = "Conference Search"
    description: str = "Searches for technology conferences using a specific query. Use this for any request about finding conferences."
    class GetConferencesInput(BaseModel):
        searchQuery: str = Field(description="A URL-encoded query string to search for conferences. E.g., 'rank=B&country=Vietnam'")

    args_schema: Type[BaseModel] = GetConferencesInput

    # Không cần session hay loop nữa, chỉ cần một HTTP client
    client: httpx.AsyncClient = Field(default_factory=lambda: httpx.AsyncClient())

    async def _run(self, searchQuery: str) -> str:
        """
        Sends a JSON-RPC request to the remote MCP server over HTTP.
        """
        # 1. Xây dựng payload theo chuẩn JSON-RPC 2.0 mà MCP sử dụng
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_conferences", # Tên tool trên server
                "arguments": {"searchQuery": searchQuery}
            },
            "id": str(uuid.uuid4()) # Mỗi request phải có một ID duy nhất
        }

        try:
            print(f"Sending HTTP request to MCP server: {request_payload}")
            response = await self.client.post(MCP_SERVER_URL, json=request_payload, timeout=60.0)
            response.raise_for_status() # Ném lỗi nếu status code là 4xx hoặc 5xx
            
            response_data = response.json()
            print(f"Received HTTP response from MCP server: {response_data}")

            # 2. Phân tích response JSON-RPC
            if "error" in response_data:
                return f"Error from MCP server: {response_data['error']}"
            
            result = response_data.get("result", {})
            
            # MCP trả về kết quả trong một list content
            content_list = result.get("content", [])
            if content_list:
                return content_list[0].get("text", "No text content found.")
            
            return "Received an empty result from the tool."

        except httpx.RequestError as e:
            print(f"HTTP Request Error to MCP server: {e}")
            traceback.print_exc()
            return f"Network error while communicating with the tool server: {e}"
        except Exception as e:
            print(f"An unexpected error occurred in HTTPConferenceTool: {e}")
            traceback.print_exc()
            return f"An unexpected error occurred: {e}"