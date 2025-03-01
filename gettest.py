import requests
import json

def get_metrics():
    """
    调用API获取指标数据
    """
    start_date = "2025-02-27"  # 开始日期
    end_date = "2025-03-31"  # 结束日期
    url = f"http://localhost:8000/api/metrics?start_date={start_date}&end_date={end_date}"  # 可以根据实际情况修改此URL
    
    try:
        response = requests.get(url)
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
    get_metrics()
