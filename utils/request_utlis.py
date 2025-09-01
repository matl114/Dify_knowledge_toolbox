import requests
from requests import Response
from dify_plugin.file.file import File
import httpx

def _request(url: str, parameters : str, header : dict, wait : bool = True) -> Response | Exception:
    try:
        response = requests.get(
            f"{url}?{parameters}", 
            headers= header
        )
        if wait:
            response.raise_for_status()
            return response
    except Exception as e:
        return e
    
def _get_fixed_url(url : str, default_url : str = None) -> str:
    return ("http://nginx" if default_url is None or default_url == "" else default_url)  + url if url.startswith("/file") else url
        
def _read_blob(file: File, default_url : str = None) -> bytes:
    if file._blob is None:
        fixed_url = _get_fixed_url(file.url, default_url)
        response = httpx.get(fixed_url)
        response.raise_for_status()
        file._blob = response.content
    assert file._blob is not None
    return file._blob