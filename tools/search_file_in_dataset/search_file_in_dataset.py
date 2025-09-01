from collections.abc import Generator
from typing import Any
import requests
from requests import Response

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.request_utlis import _request
from utils.json_wrap_utils import _wrap, _stringify, _stringify_and_wrap_list
from utils.dataset_utils import DifyDatasetInfo

class SearchFileInDatasetTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dataset = DifyDatasetInfo(**tool_parameters)
        key_word = tool_parameters.get("key_word")
        format = tool_parameters.get("format", "ID")
        type = tool_parameters.get("type", "String")
        limit = tool_parameters.get("limit", -1)
        header = dataset.header()
        # test document
        datas = []
        request_url = dataset.endpoint_dat(None)
        parameters = f"limit=100&&page=1{'' if key_word == '' else f'&&keyword={key_word}'}"
        response = _request(request_url, parameters, header)
        if isinstance(response, Exception):
            yield self.create_text_message(f"Error while fetching document list: {str(response)}")
            return
        data = response.json()
        total = data["total"]
        # optimize: limit number
        if limit >= 0 :
            total = min(limit, total)
        datas.extend(data["data"])
        if total > 100:
            pages =  int(total -1)//100 + 1
            for i in range(1, pages):
                parameters = f"limit=100&&page={i + 1}{'' if key_word == '' else f'&&keyword={key_word}'}"
                response = _request(request_url, parameters, header)
                if isinstance(response, Exception):
                    yield self.create_text_message(f"Error while fetching document list: {str(response)}")
                    return
                data = response.json()
                datas.extend(data["data"])
        # limit number
        if limit >= 0:
            datas = datas[: limit]
        if format == "Name":
            values = [fileMetaData["name"] for fileMetaData in datas]
        elif format == "ID":
            values = [fileMetaData["id"] for fileMetaData in datas]
        elif format == "Meta":
            values = datas
        else :
            yield self.create_text_message(f"Illegal Parameter format {format}: format not supported")
            
        return_type = tool_parameters.get("type", "string_concat")
        if return_type == "string_concat":
            yield self.create_text_message(_stringify(values))
        elif return_type == "string_list":
            yield self.create_json_message(_stringify_and_wrap_list(values))
        elif return_type == "json_list":
            for var in values:
                yield self.create_json_message(_wrap(var))
        else:
            yield self.create_text_message(f"Illegal Parameter return type {return_type}: return type not supported")
            
    