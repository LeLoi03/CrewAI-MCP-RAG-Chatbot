import requests
import json
from pydantic import BaseModel, Field

# Đọc URL từ biến môi trường (sẽ được load bởi main.py)
import os
CONFERENCE_API_URL = os.getenv("CONFERENCE_API_URL", "https://confhub.ddns.net/database/api/v1/conference")

class GetConferencesInput(BaseModel):
    """Pydantic model for input validation."""
    searchQuery: str = Field(description="The user's specific query or topic to search for conferences.")

def execute_get_conferences(searchQuery: str) -> str:
    """
    The core business logic for fetching conference data.
    This function is now pure and separated from any framework.
    """
    try:
        # Logic gọi API của bạn được giữ nguyên
        params_dict = requests.utils.parse_header_links(f'<{searchQuery}>; rel="search"')[0]
        # Clean up params if needed, requests can handle list values
        cleaned_params = {k: v for k, v in params_dict.items() if k != 'rel'}

        response = requests.get(CONFERENCE_API_URL, params=cleaned_params)
        response.raise_for_status()
        api_result = response.json()

        if "payload" in api_result and api_result["payload"]:
            return json.dumps(api_result["payload"])
        elif "payload" in api_result and not api_result["payload"]:
            return "No conferences found matching your criteria."
        else:
            return f"Error from API: {api_result.get('errorMessage', 'Unknown error')}"

    except requests.exceptions.RequestException as e:
        return f"Error: Network error while fetching conferences: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"