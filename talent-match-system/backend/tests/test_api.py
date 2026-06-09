import requests
import json

# 测试发送验证码接口
url = "http://localhost:8000/api/auth/send-code"
headers = {"Content-Type": "application/json"}
data = {"phone": "13800138000"}

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
print("Response:", response.json())

# 测试根路径
root_url = "http://localhost:8000/"
root_response = requests.get(root_url)
print("\nRoot Path Status Code:", root_response.status_code)
print("Root Path Response:", root_response.json())

# 测试健康检查
health_url = "http://localhost:8000/health"
health_response = requests.get(health_url)
print("\nHealth Check Status Code:", health_response.status_code)
print("Health Check Response:", health_response.json())