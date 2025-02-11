# simple_crawler.py

import requests
from bs4 import BeautifulSoup

def get_webpage_content():
    # 1. 发送HTTP请求
    try:
        # 这里使用天气网作为示例
        url = "http://www.weather.com.cn/weather/101020100.shtml"
        
        # 添加请求头，模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 发送GET请求
        response = requests.get(url, headers=headers)
        
        # 设置响应的编码格式
        response.encoding = 'utf-8'
        
        # 2. 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. 提取天气信息
        weather_info = soup.find('ul', class_='t clearfix')
        if weather_info:
            # 获取第一天的天气信息
            first_day = weather_info.find('li')
            if first_day:
                date = first_day.find('h1').text
                weather = first_day.find('p', class_='wea').text
                temperature = first_day.find('p', class_='tem').text.strip()
                
                print(f"日期：{date}")
                print(f"天气：{weather}")
                print(f"温度：{temperature}")
        
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    get_webpage_content()