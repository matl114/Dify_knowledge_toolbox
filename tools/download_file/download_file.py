from collections.abc import Generator
from typing import Any
import json
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dataset_utils import DifyDatasetInfo
from utils.request_utlis import _get_fixed_url


class DownloadFileTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dataset = DifyDatasetInfo(**tool_parameters)
        format = tool_parameters.get("format", "url")
        url = dataset.endpoint_doc("upload-file")
        headers = dataset.header()
        # step 1: get the upload-file endpoint
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            download_url = data.get("download_url")
        except Exception as e:
            yield self.create_text_message(
                f"Error fetching upload-file endpoint: {str(e)}"
            )
            return

        if not download_url:
            yield self.create_text_message("No download URL found in the response.")
            return

        if format == "json":
            yield self.create_text_message(
                json.dumps(data, indent=2)
            )
            return
        elif format == "url":
            yield self.create_text_message(download_url)
            return

        # step 2: fetch the file
        fixed_url = _get_fixed_url(download_url, dataset.api_base_url[:-3])
        try:
            file_response = requests.get(fixed_url)
            file_response.raise_for_status()
            file_bytes = file_response.content
        except Exception as e:
            yield self.create_text_message(
                f"Error downloading file: {str(e)}"
            )
            return

        if format == "content":
            try:
                text = file_bytes.decode("utf-8")
                yield self.create_text_message(text)
            except Exception as e:
                yield self.create_text_message(
                    f"Error decoding file as UTF-8 text: {str(e)}"
                )
            return
        elif format == "file":
            yield self.create_blob_message(
                blob=file_bytes,
                meta={
                    "mime_type": data.get("mime_type"),
                    "filename": data.get("filename"),
                },
            )
            return
