import requests

url = "http://127.0.0.1:8000/predict_camera/"
response = requests.post(url)
print("Detecciones:", response.json())
