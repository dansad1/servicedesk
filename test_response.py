import requests as r
import json

def get_response(response: str):
    url = "http://localhost:8085/rag_router/rag_final_response"
    data = {
        "text": 'sads',
        "encoding_model": "gigachat",
        "n_results": 10,
        "include_embeddings": "false"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = r.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data[0]
    else:
        return "Error: bad connection "


print(get_response('dsfsd'))