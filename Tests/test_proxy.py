import requests

proxies = {
    'http': 'http://123:123',
}

response = requests.get('http://example.com', proxies=proxies)
print(response.text)
