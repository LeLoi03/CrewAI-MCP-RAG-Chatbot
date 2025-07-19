import asyncio
import sys
import os
from crewai import Crew, Process
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.llms.gemini import host_llm
# 1. Import cả manager và hàm tạo worker
from app.agents.host_agent import host_agent_manager
from app.agents.mcp_sub_agents import create_conference_researcher
from app.tasks.research_tasks import conference_research_task
from app.tools.mcp_conference_tool import create_mcp_conference_tool
import logging
log = logging.getLogger(__name__)
log.info(f"Module '{__name__}' is being imported and processed.")

# --- PHẦN CẢI TIẾN QUAN TRỌNG ---

# 1. Xác định đường dẫn tuyệt đối đến file main.py của MCP server.
#    Điều này giúp loại bỏ sự phụ thuộc vào thư mục làm việc hiện tại.
#    os.path.dirname(__file__) -> thư mục chứa file crew.py này (app)
mcp_main_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),  # -> services/ai-core-py/app
        "..",                       # -> services/ai-core-py
        "..",                       # -> services
        "conference-tool-mcp",
        "app",
        "main.py"
    )
)

# 2. Kiểm tra xem file có thực sự tồn tại không để gỡ lỗi sớm.
if not os.path.exists(mcp_main_path):
    raise FileNotFoundError(f"Could not find MCP server executable at: {mcp_main_path}")

# 3. Xây dựng lệnh thực thi một cách an toàn.
#    `sys.executable` đảm bảo chúng ta dùng đúng trình thông dịch Python
#    (quan trọng khi dùng môi trường ảo venv).
CONFERENCE_MCP_COMMAND = [
    sys.executable, 
    mcp_main_path
]

# 4. Tạo StdioServerParameters với cấu hình đầy đủ.
conference_server_params = StdioServerParameters(
    command=CONFERENCE_MCP_COMMAND[0],
    args=CONFERENCE_MCP_COMMAND[1:],
    # 5. QUAN TRỌNG: Kế thừa môi trường và đảm bảo PYTHONPATH.
    #    Điều này giúp tiến trình con tìm thấy các module cần thiết.
    env={
        **os.environ, # Kế thừa tất cả các biến môi trường hiện tại
        "PYTHONPATH": os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
)

# --- KẾT THÚC PHẦN CẢI TIẾN ---


async def create_and_run_crew(inputs: dict):
    """
    Manages the entire lifecycle: connects to MCP, creates the wrapper tool,
    initializes and runs the crew, and cleans up the connection.
    """
    print(f"Attempting to start MCP server with command: {' '.join(CONFERENCE_MCP_COMMAND)}")
    
    async with stdio_client(conference_server_params) as (read, write):
        print("MCP stdio_client context entered.")
        async with ClientSession(read, write) as session:
            print("MCP ClientSession context entered. Initializing session...")
            await session.initialize()
            print("MCP Session initialized successfully.")

            main_loop = asyncio.get_running_loop()
            mcp_conference_tool = create_mcp_conference_tool(session=session, loop=main_loop)
            conference_researcher_agent = create_conference_researcher(mcp_conference_tool)
            
            # --- THAY ĐỔI QUAN TRỌNG ---
            # 2. Cấu hình Crew một cách tường minh
            research_crew = Crew(
                agents=[conference_researcher_agent], # Danh sách các worker
                tasks=[conference_research_task],
                process=Process.hierarchical,
                # 3. Chỉ định rõ ai là manager
                manager_agent=host_agent_manager,
                # Bỏ `manager_llm` vì manager đã có llm của riêng nó
                verbose=True
            )

            # loop.run_in_executor vẫn là cách đúng để chạy kickoff
            result = await main_loop.run_in_executor(
                None,
                research_crew.kickoff,
                inputs
            )
            return result