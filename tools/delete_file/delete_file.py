from collections.abc import Generator
from typing import Any
import json
import requests
import mimetypes
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.request_utlis import _request , _read_blob
from utils.json_wrap_utils import _wrap, _stringify, _stringify_and_wrap_list
from utils.dataset_utils import DifyDatasetInfo

class DeleteFileTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dataset = DifyDatasetInfo(**tool_parameters)
        url = dataset.endpoint_doc(None)
        header = dataset.header()
        try:
            response = requests.delete(url, headers= header)
            response.raise_for_status()
            yield self.create_text_message(f"Success")
        except Exception as e:
            yield self.create_text_message(f"Error while deleting document: {str(e)}")