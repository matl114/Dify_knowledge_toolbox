from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dataset_utils import DifyDatasetInfo

class GetFullDocTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dataset = DifyDatasetInfo(**tool_parameters)
    
        delimiter = tool_parameters.get(
            "delimiter", "\n\n").encode().decode("unicode_escape")
        url = dataset.endpoint_doc("segments")
        headers = dataset.header()
        all_data = []
        page = 1
        has_more = True
        params = {"limit": 100}
        try:
            while has_more:
                params["page"] = page
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    raise Exception(f"{response.status_code} {response.text}")
                resp_json = response.json()
                all_data.extend(resp_json.get("data", []))
                has_more = resp_json.get("has_more", False)
                page += 1
        except Exception as e:
            yield self.create_text_message(f"Error fetching segments: {str(e)}")
            return

        text = delimiter.join([segment.get("content", "")
                              for segment in all_data])
        yield self.create_text_message(text)