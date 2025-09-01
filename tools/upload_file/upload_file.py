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

class UploadFileTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dataset = DifyDatasetInfo(**tool_parameters)
        files = tool_parameters.get("file")
        name = tool_parameters.get("document_name", "")
        format = tool_parameters.get("format", "async")
        rule = tool_parameters.get("data", "")
        if rule == "":
            # todo test auto mode
            data_json = {
                "process_rule":{
                    "rules":{
                        "pre_processing_rules":[
                            {"id":"remove_extra_spaces","enabled": True}
                            ],
                        "segmentation":{
                            "separator":"\n\n","max_tokens":1024}
                        },
                    "mode":"custom"
                }
            }
        else :
            try:
                data_json = json.loads(rule)
            except Exception as e:
                yield self.create_text_message(
                    f"Error parsing extra data json: {str(e)}"
                    )
                return
        request_url =   f"{dataset.api_base_url.rstrip('/')}/datasets/{dataset.knowledge_id}/document/create-by-file"
        new_doc_batch_list = []
        for file in files:
            file_content = _read_blob(file)
            if name == "":
                name = file.filename
                
            mime_type = file.mime_type
            if mime_type is None:
                mime_type, _ = mimetypes.guess_type(name)
            if mime_type is None:
                mime_type = "application/octet-stream"
            multiform = {
                "data": (None, json.dumps(data_json), "application/json"),
                "file": (name, file_content, mime_type)
            }
            header = dataset.header(None)
            try:
                res = requests.post(request_url, files = multiform, headers = header)#    _request(request_url, files = multiform, header = header, wait =  format == "sync")
                res.raise_for_status()
            except Exception as e:
                yield self.create_json_message({
                    "error": f"Error posting request: {str(e)}\n"
                })
                continue
            data = res.json()
            new_doc_batch_list.append(data["batch"])
            yield self.create_json_message(data)
        
        if format == "sync":
            for ids in new_doc_batch_list:
                self._await_spliting_status(dataset.api_base_url, dataset.api_key, dataset.knowledge_id, ids)
    def _await_spliting_status(self, api_base_url, api_key, dataset_id, doc_id):
        request_url = f"{api_base_url.rstrip('/')}/datasets/{dataset_id}/documents/{doc_id}/indexing-status"
        header = f"Authorization: Bearer {api_key}"
        while True:
            try:
                res = requests.get(request_url, headers= header)
                for result in res["data"]:
                    if result["indexing_status"] == "indexing" or result["indexing_status"] == "splitting":
                        continue
            except Exception as e:
                return
    