from collections.abc import Generator
from typing import Any
import base64
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dataset_utils import _set_cache, _get_cache

# TODO need test
class SetParamTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_base_url = tool_parameters.get("api_base_url", None)
        api_base_url = api_base_url if api_base_url != "" else None
        api_key = tool_parameters.get("api_key", None)
        api_key = api_key if api_key != "" else None
        knowledge_id = tool_parameters.get("knowledge_id", None)
        knowledge_id = knowledge_id if knowledge_id != "" else None
        document_id = tool_parameters.get("document_id", None)
        document_id = document_id if document_id != "" else None
        type = tool_parameters.get("type")
        resetFlag = type == "reset"
        _set_cache(api_base_url, api_key, knowledge_id, document_id, resetFlag)
        yield self.create_json_message(_get_cache())