# app/llms/gemini.py

# SỬA LỖI Ở ĐÂY: Import lớp LLM trực tiếp từ crewai
from crewai import LLM 
from app.config.settings import settings

# Khởi tạo LLM cho Host Agent (Manager)
host_llm = LLM(
    model=f"gemini/{settings.HOST_AGENT_MODEL_NAME}",
    config={
        "temperature": 0.3
    }
)

# Khởi tạo LLM cho các Sub Agent (Workers)
sub_agent_llm = LLM(
    model=f"gemini/{settings.SUB_AGENT_MODEL_NAME}",
    config={
        "temperature": 0.1
    }
)