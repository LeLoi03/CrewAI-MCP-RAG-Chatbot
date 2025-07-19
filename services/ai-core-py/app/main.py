# 1. Thiết lập logging ngay từ đầu, trước tất cả các import khác của app.
from app.config.logging_config import setup_logging
setup_logging()

import logging

# 2. Lấy một logger cho module này
log = logging.getLogger(__name__)

log.info("========================================================")
log.info("AI Core Service - Application Startup Sequence Begins...")
log.info("========================================================")

# 3. Import các thành phần khác
log.info("Importing FastAPI...")
from fastapi import FastAPI
log.info("FastAPI imported successfully.")

log.info("Importing API router from app.api.endpoints...")
from app.api.endpoints import router as api_router
log.info("API router imported successfully.")


# 4. Khởi tạo ứng dụng FastAPI
log.info("Creating FastAPI app instance...")
app = FastAPI(
    title="AI Core Service",
    description="Manages AI agent crews for the chatbot system.",
    version="1.0.0"
)
log.info("FastAPI app instance created.")

# 5. Sử dụng sự kiện "startup" của FastAPI
@app.on_event("startup")
async def startup_event():
    log.info("FastAPI 'startup' event triggered. The application is fully configured and ready to accept requests.")

# 6. Gắn router vào ứng dụng
log.info("Including API router into the app...")
app.include_router(api_router, prefix="/api/v1")
log.info("API router included successfully.")

# 7. Định nghĩa endpoint gốc
@app.get("/")
def read_root():
    log.info("Root endpoint '/' was called.")
    return {"status": "AI Core Service is running"}

log.info("main.py file has been fully processed. Uvicorn will now take over.")