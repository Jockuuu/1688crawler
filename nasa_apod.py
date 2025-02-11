# ===== 第一部分：导入必要的库 =====
import requests  # 用于发送网络请求，下载网页和图片
from bs4 import BeautifulSoup  # 用于解析HTML网页内容
import os  # 用于创建文件夹和处理文件路径
from datetime import datetime  # 用于获取当前日期
import json  # 用于保存和读取JSON格式的数据

# ===== 第二部分：定义NASA图片爬虫类 =====
class NASAImageCrawler:
    def __init__(self):
        """
        初始化函数
        设置基本的URL和图片保存目录
        这个爬虫专门用于下载NASA的每日天文图片
        """
        # NASA天文图片网站的基础URL
        self.base_url = "https://apod.nasa.gov/apod/"
        # 设置图片保存的文件夹名称
        self.image_dir = "nasa_images"
        # 创建保存图片的文件夹（如果不存在）
        # exist_ok=True 表示如果文件夹已存在也不会报错
        os.makedirs(self.image_dir, exist_ok=True)
        
    def get_page_content(self):
        """
        获取NASA天文图片网页的内容
        这是爬虫的第一步：获取网页
        """
        try:
            # 设置请求头，模拟浏览器访问
            # 这是爬虫的基本礼仪，也是避免被封禁的重要步骤
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            # 发送GET请求获取网页内容
            # f-string 用于构造完整的URL
            response = requests.get(f"{self.base_url}astropix.html", headers=headers)
            response.encoding = 'utf-8'  # 设置编码，避免乱码
            return response.text
        except Exception as e:
            # 错误处理：记录失败原因
            print(f"获取页面失败: {str(e)}")
            return None

    def download_image(self, image_url, file_name):
        """
        下载图片的函数
        参数:
            image_url: 图片的URL地址
            file_name: 保存的文件名
        返回:
            成功返回保存路径，失败返回None
        """
        try:
            # 处理相对URL的情况
            # 有些图片URL是相对路径，需要加上网站的基础URL
            if not image_url.startswith('http'):
                image_url = f"{self.base_url}{image_url}"
                
            print(f"正在下载图片: {image_url}")
            
            # 下载图片内容
            response = requests.get(image_url)
            if response.status_code == 200:  # 200表示请求成功
                # 构造保存路径并保存图片
                file_path = os.path.join(self.image_dir, file_name)
                # 'wb' 表示以二进制写入模式打开文件
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"图片已保存: {file_path}")
                return file_path
            else:
                print(f"下载失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"下载图片时出错: {str(e)}")
            return None

    def parse_page(self, html):
        """
        解析网页内容，提取需要的信息
        这是爬虫的核心部分，需要了解网页结构
        """
        try:
            # 创建BeautifulSoup对象解析HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # 获取网页标题
            title = soup.find('title').text.strip()
            print(f"\n标题: {title}")
            
            # 查找图片标签
            image = soup.find('img')
            if image:
                # 获取图片URL
                image_url = image['src']
                
                # 获取图片说明文字
                # NASA网站的图片说明通常在第二个p标签中
                explanation = ""
                p_tags = soup.find_all('p')
                if len(p_tags) > 1:
                    explanation = p_tags[1].text.strip()
                
                # 生成文件名：使用当前日期
                today = datetime.now().strftime("%Y%m%d")  # 格式：年月日
                # 获取原图片的扩展名（.jpg/.png等）
                image_extension = os.path.splitext(image_url)[1]
                # 组合新的文件名
                file_name = f"nasa_apod_{today}{image_extension}"
                
                # 下载图片
                image_path = self.download_image(image_url, file_name)
                
                # 整理所有信息到一个字典中
                data = {
                    "date": today,
                    "title": title,
                    "image_url": image_url,
                    "local_path": image_path,
                    "explanation": explanation
                }
                
                # 保存信息
                self.save_info(data)
                return data
            else:
                print("未找到图片")
                return None
                
        except Exception as e:
            print(f"解析页面时出错: {str(e)}")
            return None

    def save_info(self, data):
        """
        保存图片相关信息
        同时保存JSON格式（便于程序读取）和文本格式（便于人类阅读）
        """
        # 设置JSON文件路径
        json_path = os.path.join(self.image_dir, "image_info.json")
        
        # 读取现有的JSON数据（如果有的话）
        existing_data = []
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        
        # 添加新数据
        existing_data.append(data)
        
        # 保存更新后的JSON数据
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"信息已保存到: {json_path}")
        
        # 保存为易读的文本文件
        txt_path = os.path.join(self.image_dir, f"nasa_apod_{data['date']}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"日期: {data['date']}\n")
            f.write(f"标题: {data['title']}\n")
            f.write(f"图片URL: {data['image_url']}\n")
            f.write(f"本地路径: {data['local_path']}\n")
            f.write(f"\n说明:\n{data['explanation']}\n")
        
        print(f"详细信息已保存到: {txt_path}")

# ===== 程序入口 =====
def main():
    """
    主函数：程序的入口点
    创建爬虫对象并执行爬取任务
    """
    crawler = NASAImageCrawler()  # 创建爬虫对象
    print("开始获取NASA每日天文照片...")
    
    # 执行爬取流程
    html = crawler.get_page_content()
    if html:
        data = crawler.parse_page(html)
        if data:
            print("\n抓取完成！")
            print(f"图片保存在: {crawler.image_dir} 目录下")
        else:
            print("解析页面失败")
    else:
        print("获取页面失败")

# 当直接运行此文件时执行main函数
if __name__ == "__main__":
    main() 