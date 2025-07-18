from collections.abc import Generator
from typing import Any
import base64
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import base64
import mimetypes
from utils.request_utlis import _read_blob,_get_fixed_url

class OperateFileTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters.get("file")  
        operate_type = tool_parameters.get("operate_type", "get_url")
        default_url = tool_parameters.get("default_file_url", "")
        if operate_type == "get_url":
            yield self.create_text_message(_get_fixed_url(file.url, default_url))
        elif operate_type == "dump_json":
            file_dict = file.dict()
            file_dict["blob"] = base64.b64encode(_read_blob(file, default_url= default_url)).decode("utf-8")
            yield self.create_text_message(
                json.dumps(file_dict, indent=2, ensure_ascii=False)
            )
        elif operate_type == "encode_b64":
            base64_blob = base64.b64encode(_read_blob(file, default_url= default_url)).decode("utf-8")
            yield self.create_text_message(base64_blob)
        elif operate_type == "encode_b64_uri":
            mime_type, _ = mimetypes.guess_type(file.filename)
            base64_blob = base64.b64encode(_read_blob(file, default_url= default_url)).decode("utf-8")
            yield self.create_text_message(f"data:{mime_type};base64,{base64_blob}")
        else :
            yield self.create_text_message(f"Operate type not supported: {operate_type}")