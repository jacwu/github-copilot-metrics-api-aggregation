import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')
GITHUB_ORG = os.getenv('GITHUB_ORG')

def get_github_metrics():
    """
    调用API获取指标数据
    """
    # 从环境变量读取token
    token = GITHUB_API_TOKEN
    if not token:
        print("错误：未设置GITHUB_API_TOKEN环境变量")
        return None

    start_date = "2025-02-23"  # 开始日期
    end_date = "2025-03-31"  # 结束日期
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/copilot/metrics"  # 可以根据实际情况修改此URL
    
    # 设置Authorization header
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是 200，将引发异常
        
        # 解析响应数据
        metrics_data = response.json()
        
        # 打印获取的指标数据
        print("获取的指标数据:")
        print(json.dumps(metrics_data, indent=4, ensure_ascii=False))
        
        return metrics_data
    except requests.exceptions.RequestException as e:
        
        # 打印response里的json数据
        print(response.json())

        return None
    

def get_metrics():
    """
    调用API获取指标数据
    """
    # 从环境变量读取token
    token = os.getenv('GITHUB_API_TOKEN')
    if not token:
        print("错误：未设置GITHUB_API_TOKEN环境变量")
        return None

    start_date = "2025-02-23"  # 开始日期
    end_date = "2025-03-31"  # 结束日期
    url = f"http://localhost:8000/api/metrics?start_date={start_date}&end_date={end_date}"  # 可以根据实际情况修改此URL
    
    # 设置Authorization header
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是 200，将引发异常
        
        # 解析响应数据
        metrics_data = response.json()
        
        # 打印获取的指标数据
        print("获取的指标数据:")
        print(json.dumps(metrics_data, indent=4, ensure_ascii=False))
        
        return metrics_data
    except requests.exceptions.RequestException as e:
        
        # 打印response里的json数据
        print(response.json())

        return None

if __name__ == '__main__':
    # get_github_metrics()
    get_metrics()
