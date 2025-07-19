import requests
import json
from urllib.parse import parse_qs
from pydantic import BaseModel, Field

# Bạn có thể cần một file config nhỏ ở đây hoặc đọc trực tiếp từ env
CONFERENCE_API_URL = "https://confhub.ddns.net/database/api/v1/conference"

class GetConferencesInput(BaseModel):
    """Input schema for the get_conferences tool."""
    searchQuery: str = Field(description="A URL-encoded query string to search for conferences. E.g., 'rank=B&country=Vietnam'")

def get_conferences_from_api(searchQuery: str) -> str:
    """
    The core logic to fetch conference data from the external API.
    This function is what the MCP tool will wrap.
    """
    try:
        params_dict = parse_qs(searchQuery)
        response = requests.get(CONFERENCE_API_URL, params=params_dict)
        response.raise_for_status()
        api_result = response.json()

        if "payload" in api_result and api_result["payload"]:
            # Trả về chuỗi JSON để agent có thể xử lý
            return json.dumps(api_result["payload"])
        elif "payload" in api_result and not api_result["payload"]:
            return "No conferences found matching the criteria."
        else:
            return f"Error from API: {api_result.get('errorMessage', 'Unknown error')}"

    except requests.exceptions.RequestException as e:
        return f"Error: Network error while fetching conferences: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"