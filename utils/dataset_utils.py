from typing import Any, Optional
import json
import requests

CACHED_API_BASE_URL = "http://nginx/v1"
CACHED_API_KEY = None
CACHED_KNOWLEDGE_ID = None
CACHED_DOCUMENT_ID = None

class DifyDatasetInfo:
    api_base_url : str
    
    api_key : str 
    knowledge_id : Optional[str] 
    document_id : Optional[str] 
    def __init__(self,  api_key: str, api_base_url: str = None, knowledge_id: str = None, document_id: str = None, **kwargs):
        global CACHED_API_BASE_URL 
        global CACHED_API_KEY
        global CACHED_KNOWLEDGE_ID
        global CACHED_DOCUMENT_ID   
        self.api_base_url = api_base_url if api_base_url is not None and api_base_url != "" else CACHED_API_BASE_URL
        self.api_key = api_key if api_key is not None and api_key != "" else CACHED_API_KEY
        self.knowledge_id = knowledge_id if knowledge_id is not None and knowledge_id != "" else CACHED_KNOWLEDGE_ID
        self.document_id = document_id if document_id is not None and document_id != "" else CACHED_DOCUMENT_ID
        
    def endpoint(self, endpoint : Optional[str]):
        return  f"{self.api_base_url.rstrip('/')}/datasets/{endpoint}" if endpoint is not None else  f"{self.api_base_url.rstrip('/')}/datasets"
        
    def endpoint_dat(self, endpoint : Optional[str]):
        return f"{self.api_base_url.rstrip('/')}/datasets/{self.knowledge_id}/documents/{endpoint}" if endpoint is not None else f"{self.api_base_url.rstrip('/')}/datasets/{self.knowledge_id}/documents"
    
    def endpoint_dat_with_doc(self, documentId : str, endpoint: Optional[str]):
        return f"{self.api_base_url.rstrip('/')}/datasets/{self.knowledge_id}/documents/{documentId}/{endpoint}" if endpoint is not None else f"{self.api_base_url.rstrip('/')}/datasets/{self.knowledge_id}/documents/{documentId}"
    
    def endpoint_doc(self, endpoint: Optional[str]):
        return  f"{self.api_base_url.rstrip('/')}/datasets/{self.knowledge_id}/documents/{self.document_id}/{endpoint}" if endpoint is not None else f"{self.api_base_url.rstrip('/')}/datasets/{self.knowledge_id}/documents/{self.document_id}"
    
    def header(self, application_type: Optional[str] = "application/json"):
        if application_type is None:
            return {
                "authorization": f"bearer {self.api_key}",
            }
        else:
            return {
                "authorization": f"bearer {self.api_key}",
                "content-type": application_type
            }
            
def _reset_cache():
    global CACHED_API_BASE_URL 
    CACHED_API_BASE_URL = "http://nginx/v1"
    global CACHED_API_KEY
    CACHED_API_KEY = None
    global CACHED_KNOWLEDGE_ID
    CACHED_KNOWLEDGE_ID = None
    global CACHED_DOCUMENT_ID
    CACHED_DOCUMENT_ID = None
    
def _set_cache(api_base_url: str = None, api_key: str = None, knowledge_id: str = None, document_id: str = None, resetFlag : bool = False):
    global CACHED_API_BASE_URL 
    if api_base_url is not None:
        CACHED_API_BASE_URL = api_base_url
    elif resetFlag:
        CACHED_API_BASE_URL = "http://nginx/v1"
    global CACHED_API_KEY
    if api_key is not None:
        CACHED_API_KEY = api_key
    elif resetFlag:
        CACHED_API_KEY = None
    global CACHED_KNOWLEDGE_ID
    if knowledge_id is not None:
        CACHED_KNOWLEDGE_ID = knowledge_id
    elif resetFlag:
        CACHED_KNOWLEDGE_ID = None
    global CACHED_DOCUMENT_ID
    if document_id is not None:
        CACHED_DOCUMENT_ID = document_id
    elif resetFlag:
        CACHED_DOCUMENT_ID = None
        
def _get_cache() :
    global CACHED_API_BASE_URL 
    global CACHED_API_KEY
    global CACHED_KNOWLEDGE_ID
    global CACHED_DOCUMENT_ID   
    return {
        "api_base_url": CACHED_API_BASE_URL,
        "api_key": CACHED_API_KEY,
        "knowledge_id" : CACHED_KNOWLEDGE_ID,
        "document_id": CACHED_DOCUMENT_ID
    }   
            
            
def _retrieve_knowledge(data: DifyDatasetInfo, query: str, extra_param: str, topK: int):
    response_meta = requests.get(data.endpoint_dat(None), headers= data.header())
    response_meta.raise_for_status()
    knowledge_meta = response_meta.json()
    knowledge_name = knowledge_meta["name"]
    request_url = f"http://localhost/v1/datasets/{data.document_id}/retrieve"
    sample_json = {
        "search_method": "hybrid_search",
        "reranking_enable": False,
        "reranking_mode": None,
        "reranking_model": {
            "reranking_provider_name": "",
            "reranking_model_name": ""
        },
        "weights": 0.5,
        "top_k": topK,
        "score_threshold_enabled": False,
        "score_threshold": None,
        "metadata_filtering_conditions": {
            "logical_operator": "and",
            "conditions": [
            ]
        }
        }
    if extra_param == "":
        extra_json = sample_json
    else:
        extra_json : dict = json.loads(extra_param)
        for key, value in sample_json.items():
            if key not in extra_json.keys():
                extra_json[key] = value
    extra_json["top_k"] = topK
    request_data = {
        "query": query,
        "retrieval_model": extra_json
    }
    response = requests.post(request_url, data = json.dumps(request_data), headers=  data.header())
    response.raise_for_status()
    data_list = response.json()["records"]
    results = []
    for data in data_list:
        result0 = {"content": data["segment"]["content"], "title": data["segment"]["document"]["name"]}
        meta = {
            "_source": "knowledge",
            "dataset_id": data.knowledge_id,
            "dataset_name": knowledge_name,
            "document_id": data["segment"]["document_id"],
            "document_name": data["segment"]["document"]["name"],
            "data_source_type": data["segment"]["document"]["data_source_type"],
            "segment_id": data["segment"]["index_node_id"],
            "retriever_from":  "workflow",
            "score": data["score"],
            "segment_hit_count": data["segment"]["hit_count"],
            "segment_word_count": data["segment"]["word_count"],
            "segment_position": data["segment"]["position"],
            "segment_index_node_hash": data["segment"]["index_node_hash"],
            "doc_metadata": data["segment"]["document"]["doc_metadata"],
            "position": data["tsne_position"]
        }
        result0["metadata"] = meta 
        results.append(result0)
    return results
