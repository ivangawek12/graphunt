import os
import requests

DEFAULT_RELATIONSHIPS = ["contacted_urls", "contacted_domains", "contacted_ips"]


def vt_intelligence_search(query: str, limit: int = 40, api_key: str = None, relationships=None):
    """
    Run a VT Intelligence search and optionally request network relationships.
    Returns the raw JSON response.
    """
    api_key = api_key or os.getenv("VT_API_KEY")
    if not api_key:
        raise ValueError("VirusTotal API key not found. Set VT_API_KEY in .env or pass explicitly.")

    headers = {"x-apikey": api_key}
    url = "https://www.virustotal.com/api/v3/intelligence/search"
    params = {"query": query, "limit": limit}
    if relationships:
        if isinstance(relationships, (list, tuple)):
            params["relationships"] = ",".join(relationships)
        else:
            params["relationships"] = str(relationships)

    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code != 200:
        raise Exception(f"VT search failed: HTTP {response.status_code} - {response.text}")

    return response.json()


def build_graph_from_search_response(response_json):
    """
    Convert VT search response (with optional relationships) into node/edge lists.
    """
    nodes = []
    edges = []
    seen_nodes = set()

    for item in response_json.get("data", []):
        file_id = item.get("id")
        if not file_id:
            continue
        if file_id not in seen_nodes:
            nodes.append({"id": file_id, "type": "hash"})
            seen_nodes.add(file_id)

        relationships = item.get("relationships", {}) or {}
        for rel_name, rel_payload in relationships.items():
            data = rel_payload.get("data") if isinstance(rel_payload, dict) else None
            if data is None:
                continue
            rel_items = data if isinstance(data, list) else [data]
            for rel in rel_items:
                rel_id = rel.get("id")
                rel_type = rel.get("type")
                if not rel_id:
                    continue
                ioc_type = _map_vt_type(rel_type, rel_id)
                if rel_id not in seen_nodes:
                    nodes.append({"id": rel_id, "type": ioc_type})
                    seen_nodes.add(rel_id)
                edges.append({"src": file_id, "dst": rel_id, "relationship": rel_name})

    return nodes, edges


def _map_vt_type(rel_type, rel_id):
    if rel_type in {"domain", "domains"}:
        return "domain"
    if rel_type in {"ip_address", "ip"}:
        return "ip"
    if rel_type in {"url", "urls"}:
        return "url"
    if rel_type in {"file", "files"}:
        return "hash"
    if rel_id and "/" in rel_id:
        return "url"
    if rel_id and rel_id.count(".") == 3:
        return "ip"
    if rel_id and "." in rel_id:
        return "domain"
    return "unknown"