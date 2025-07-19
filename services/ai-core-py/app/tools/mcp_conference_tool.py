import traceback
import asyncio # <<< Thêm import asyncio
from typing import Type, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from mcp import ClientSession

class MCPConferenceTool(BaseTool):
    name: str = "Conference Search"
    description: str = "Searches for technology conferences using a specific query. Use this for any request about finding conferences."
    
    class GetConferencesInput(BaseModel):
        searchQuery: str = Field(description="A URL-encoded query string to search for conferences. E.g., 'rank=B&country=Vietnam'")
    
    args_schema: Type[BaseModel] = GetConferencesInput
    
    # Thêm 2 thuộc tính mới
    session: ClientSession
    loop: asyncio.AbstractEventLoop # <<< Để lưu event loop chính

    class Config:
        arbitrary_types_allowed = True

    # --- THAY ĐỔI QUAN TRỌNG ---
    # Chuyển _run thành một hàm đồng bộ (def) thay vì async def
    def _run(self, searchQuery: str) -> str:
        """
        The synchronous entry point that CrewAI calls.
        This method safely schedules the async logic on the main event loop.
        """
        # Tạo một coroutine object từ hàm async của chúng ta
        coro = self._arun(searchQuery)
        
        # Sử dụng run_coroutine_threadsafe để gửi coroutine này đến event loop
        # đang chạy ở thread chính và chờ kết quả.
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        
        # Lấy kết quả khi nó hoàn thành. Lệnh này sẽ block thread hiện tại (thread B)
        # cho đến khi coroutine chạy xong trên thread chính (loop A).
        try:
            return future.result(timeout=60) # Thêm timeout để tránh treo vĩnh viễn
        except Exception as e:
            print(f"ERROR getting result from future: {e}")
            traceback.print_exc()
            return f"Error executing tool: {e}"

    async def _arun(self, searchQuery: str) -> str:
        """The actual async implementation of the tool's logic."""
        try:
            result = await self.session.call_tool(
                name="get_conferences",
                arguments={"searchQuery": searchQuery}
            )
            
            if isinstance(result, list) and result:
                content = result[0]
                if hasattr(content, 'text') and content.text:
                    return content.text
                return str(content)
            return str(result)

        except Exception as e:
            print(f"ERROR in MCPConferenceTool _arun: {e}")
            traceback.print_exc()
            return f"Error communicating with Conference MCP server: {e}"

# Sửa hàm factory để nhận cả session và loop
def create_mcp_conference_tool(session: ClientSession, loop: asyncio.AbstractEventLoop) -> MCPConferenceTool:
    return MCPConferenceTool(session=session, loop=loop)