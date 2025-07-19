# app/tools/get_conferences_tool.py
import requests
import json # Import thư viện json
from typing import Type
from urllib.parse import parse_qs
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from app.config.settings import settings

class GetConferencesInput(BaseModel):
    searchQuery: str = Field(description="The user's specific query or topic to search for conferences.")


class GetConferencesTool(BaseTool):
    name: str = "Conference Search Tool"
    # Phần description (prompt) của bạn đã rất tốt và không cần thay đổi.
    # Nó hướng dẫn LLM tạo ra một chuỗi query chuẩn.
    description: str = (
       "Searches for conferences by generating a URL-encoded query string based on specified criteria. This function is used to find any information about conferences."
    )
    args_schema: Type[BaseModel] = GetConferencesInput

    def _run(self, searchQuery: str) -> str:
        try:
            # BƯỚC 1: Phân tích chuỗi searchQuery thành một dictionary.
            # Ví dụ: "rank=B&country=Vietnam" -> {'rank': ['B'], 'country': ['Vietnam']}
            params_dict = parse_qs(searchQuery)

            # BƯỚC 2: Truyền dictionary đã phân tích vào tham số `params`.
            # `requests` sẽ tự động tạo URL đúng: ...?rank=B&country=Vietnam
            response = requests.get(
                settings.CONFERENCE_API_URL,
                params=params_dict
            )
            response.raise_for_status()
            api_result = response.json()


            # SỬA LỖI Ở ĐÂY:
            # 1. Kiểm tra sự tồn tại của key "payload" thay vì "success".
            # 2. Trả về nội dung của "payload" dưới dạng chuỗi JSON.
            if "payload" in api_result and api_result["payload"]:
                # Chuyển đổi list/dict trong payload thành một chuỗi JSON
                # để agent có thể đọc và xử lý.
                return json.dumps(api_result["payload"])
            elif "payload" in api_result and not api_result["payload"]:
                return "No conferences found matching your criteria."
            else:
                # Giữ lại logic báo lỗi nếu có errorMessage
                return f"Error from API: {api_result.get('errorMessage', 'Unknown error')}"

        except requests.exceptions.RequestException as e:
            return f"Error: Network error while fetching conferences: {e}"
        except Exception as e:
            return f"Error: An unexpected error occurred: {e}"

get_conferences_tool = GetConferencesTool()