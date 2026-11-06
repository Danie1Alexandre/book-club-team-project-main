import requests
from api_client import get_json


def search_open_library(title):
    url = "https://openlibrary.org/search.json"
    params = {"title": title, "limit": 5}

    try:
        data = get_json(url, params=params, timeout=10)
        return data.get("docs", [])

    except requests.exceptions.RequestException as e:
        print(f"Could not conect to open libary: {e}")
        return []
