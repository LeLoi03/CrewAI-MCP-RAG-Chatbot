import json
import traceback  # <<< THÊM IMPORT NÀY
from fastapi import APIRouter, Request # <<< Thêm Request để có thể log chi tiết hơn
from pydantic import BaseModel
from starlette.responses import StreamingResponse
import logging
log = logging.getLogger(__name__)
log.info(f"Module '{__name__}' is being imported and processed.")

# Import hàm điều phối chính từ crew.py
from app.crew import create_and_run_crew

# Khởi tạo router
router = APIRouter()

# --- Pydantic Model để xác thực dữ liệu đầu vào ---
class ChatRequest(BaseModel):
    """
    Defines the expected structure for an incoming chat request from the Gateway.
    """
    query: str
    user_id: str
    conversation_id: str

# --- API Endpoint chính ---
@router.post("/chat/invoke")
async def invoke_chat(chat_request: ChatRequest, http_request: Request): # <<< Thêm http_request
    """
    The main endpoint to handle chat requests.
    It receives a user query, kicks off the AI crew, and streams the results back
    using Server-Sent Events (SSE).
    """
    # Chuẩn bị input cho CrewAI, chỉ lấy những gì cần thiết
    inputs = {"query": chat_request.query}
    
    # Lấy thông tin client để log, giúp việc truy vết dễ dàng hơn
    client_host = http_request.client.host if http_request.client else "unknown"

    async def event_stream():
        """
        An asynchronous generator that yields events for the SSE stream.
        This function orchestrates the crew execution and handles streaming responses.
        """
        print(f"Received request from {client_host} for user '{chat_request.user_id}'. Query: '{chat_request.query}'")
        
        try:
            # 1. Gửi sự kiện trạng thái đầu tiên để client biết quá trình đã bắt đầu
            yield f"data: {json.dumps({'type': 'status', 'step': 'crew_kickoff', 'message': 'Crew is starting the task...'})}\n\n"
            
            # 2. Gọi hàm điều phối chính, nơi toàn bộ logic AI diễn ra
            # Hàm này quản lý vòng đời của MCP client và thực thi crew.
            result = await create_and_run_crew(inputs)
            
            # 3. Trích xuất kết quả cuối cùng từ output của CrewAI
            # `.raw` thường chứa chuỗi văn bản cuối cùng mà manager agent tổng hợp.
            final_message = result.raw
            
            # 4. Gửi sự kiện kết quả cuối cùng về cho client
            print(f"Crew finished successfully for user '{chat_request.user_id}'. Sending final result.")
            yield f"data: {json.dumps({'type': 'result', 'message': final_message})}\n\n"

        except Exception as e:
            # --- PHẦN GỠ LỖI QUAN TRỌNG NHẤT ---
            # 5. Nếu có bất kỳ lỗi nào xảy ra trong quá trình thực thi của crew:
            
            # In ra một tiêu đề rõ ràng trong console log của server
            print("\n--- CRITICAL ERROR DURING CREW EXECUTION ---")
            # In ra toàn bộ stack trace của lỗi. Đây là thông tin quan trọng nhất
            # để xác định chính xác lỗi xảy ra ở đâu và tại sao.
            traceback.print_exc()
            print("----------------------------------------\n")
            
            # Tạo một thông báo lỗi thân thiện để gửi về cho client
            error_message = f"An unexpected error occurred on the server: {e}"
            
            # Gửi sự kiện lỗi về cho client
            yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"

    # Trả về một StreamingResponse, sử dụng generator `event_stream`
    # và đặt media type là "text/event-stream" để trình duyệt hiểu đây là SSE.
    return StreamingResponse(event_stream(), media_type="text/event-stream")