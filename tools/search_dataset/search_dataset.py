from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.request_utlis import _request
from utils.json_wrap_utils import _wrap, _stringify, _stringify_and_wrap_list
from utils.dataset_utils import DifyDatasetInfo

class SearchDatasetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dataset = DifyDatasetInfo(**tool_parameters)
        key_word = tool_parameters.get("knowledge_name", "")
        return_type = tool_parameters.get("return", "AnyId")
        limit = tool_parameters.get("limit", -1)
        header = dataset.header()
        values = []
        request_url = dataset.endpoint(None)     
        parameters = f"limit=100&&page=1{'' if key_word == '' else f'&&keyword={key_word}'}"
        response = _request(request_url, parameters, header)
        if isinstance(response, Exception):
            yield self.create_text_message(f"Error while fetching document list: {str(response)}")
            return
        data = response.json()
        knowledgeMetaData = data["data"]
        if return_type == "AnyId":
            values = [] if len(knowledgeMetaData ) == 0 else [knowledgeMetaData[0]["id"]]
        else:
            total = data["total"]
            if limit >= 0 :
                total = min(limit, total)
            values.extend(knowledgeMetaData)
            if total > 100:
                pages =  int(total -1)//100 + 1
                for i in range(1, pages):
                    parameters = f"limit=100&&page={i + 1}{'' if key_word == '' else f'&&keyword={key_word}'}"
                    response = _request(request_url, parameters, header)
                    if isinstance(response, Exception):
                        yield self.create_text_message(f"Error while fetching document list: {str(response)}")
                        return
                    values.extend(knowledgeMetaData)
            if limit >= 0 :
                values = values[: limit]
            if return_type == "AllId":
                values = [meta[id] for meta in values]
            else :
                yield self.create_text_message(f"Illegal Parameter return value {return_type}: return value not supported")

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
            
            
