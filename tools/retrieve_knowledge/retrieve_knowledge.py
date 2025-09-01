from collections.abc import Generator
from typing import Any
import base64
import json
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dataset_utils import _retrieve_knowledge, DifyDatasetInfo

# TODO need test
class RetrieveKnowledgeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        data = DifyDatasetInfo(tool_parameters)
        query = tool_parameters.get("retrieve")
        extra_param = tool_parameters.get("extra_param")
        topK = tool_parameters.get("top_k")
        value = _retrieve_knowledge(data, query, extra_param, topK)
        for val in value:
            yield self.create_json_message(val)
            