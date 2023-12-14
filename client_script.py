import requests

url = "http://127.0.0.1:5000/analyze"  # Assuming your Flask server is running on the default port 5000
data = {"data": ["Structured document 1", "Structured document 2"]}

headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)

print(response.json())
