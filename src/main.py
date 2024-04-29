import requests


def get_api_data(url):
    response = requests.get(url)
    return response.json()
