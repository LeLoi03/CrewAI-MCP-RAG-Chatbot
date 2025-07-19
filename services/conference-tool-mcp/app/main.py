import logging
import os
import sys
from datetime import datetime

# --- Thiết lập đường dẫn để giải quyết vấn đề import ---
# Thêm thư mục cha của 'app' (tức là 'conference-tool-mcp') vào sys.path
# Điều này đảm bảo rằng `from app.tool_logic` sẽ luôn hoạt động,
# bất kể file này được chạy như thế nào.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# --- Phần Logging ---
# Tạo một thư mục log nếu chưa có
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)

# Cấu hình logging để ghi vào một file riêng
log_file_path = os.path.join(log_dir, f'mcp_server_{os.getpid()}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(process)d - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
    ]
)

logging.info("--- MCP Server Process Starting ---")
logging.info(f"Python executable: {sys.executable}")
logging.info(f"System Path: {sys.path}")


try:
    from mcp.server.fastmcp import FastMCP
    from app.tool_logic import get_conferences_from_api
    logging.info("Successfully imported FastMCP and tool logic.")
except ImportError as e:
    logging.error(f"Failed to import necessary modules: {e}", exc_info=True)
    exit(1)

# 1. Khởi tạo FastMCP server với cấu hình host và port
#    Chúng ta sẽ chạy nó trên cổng 8001 để tránh xung đột với ai-core-py (cổng 8000)
logging.info("Initializing FastMCP server for HTTP transport...")
server = FastMCP(
    name="ConferenceInformationService",
    instructions="A specialized service providing tools to search for and retrieve information about technology conferences.",
    # Thêm các thiết lập cho HTTP server
    host="127.0.0.1",
    port=8001,
    streamable_http_path="/mcp" # Endpoint mà client sẽ gọi tới
)
logging.info(f"FastMCP server '{server.name}' configured for http://{server.settings.host}:{server.settings.port}{server.settings.streamable_http_path}")

# 2. Đăng ký tool (giữ nguyên)
@server.tool(
    title="Get Conferences",
    description="Searches for conferences by generating a URL-encoded query string."
)
def get_conferences(searchQuery: str) -> str:
    logging.info(f"Tool 'get_conferences' called with searchQuery: {searchQuery}")
    result = get_conferences_from_api(searchQuery)
    logging.info(f"Tool 'get_conferences' finished. Result preview: {result[:100]}...")
    return result

logging.info("Tool 'get_conferences' has been registered.")

# 3. Chạy server với transport là 'streamable-http'
if __name__ == "__main__":
    try:
        logging.info("Server is now starting in Streamable HTTP mode...")
        # THAY ĐỔI DUY NHẤT Ở ĐÂY
        server.run(transport="streamable-http")
    except Exception as e:
        logging.error("A critical error occurred during server run", exc_info=True)