# ===== 第一部分：导入必要的库 =====
# requests是爬虫最重要的库，没有它就无法获取网页内容
import requests  # 必需！用于发送网络请求，相当于在浏览器输入网址

# BeautifulSoup是第二重要的库，用于解析HTML，没有它就无法从网页中提取数据
from bs4 import BeautifulSoup  # 必需！用于从HTML中提取数据，就像从一堆杂乱的文字中找到我们要的内容

# time用于控制爬虫速度，防止请求太快被网站封禁
import time  # 重要！防止爬取太快被网站屏蔽

# json用于保存数据，如果不需要保存成json格式可以不用
import json  # 可选，用于将数据保存为结构化的JSON格式

# ===== 第二部分：定义爬虫类 =====
class QuotesCrawler:
    def __init__(self):
        """
        初始化函数，设置爬虫的基本参数
        在做其他爬虫项目时，这里需要改成你要爬取的网站地址
        """
        # 目标网站的基础URL，这是爬虫要访问的网站
        self.base_url = "http://quotes.toscrape.com"  # 重要！这是爬虫的目标网站
        
        # 创建一个空列表来存储所有爬取的数据
        self.quotes_data = []  # 重要！用于存储爬取的数据，所有爬虫都需要一个数据存储容器
    
    def get_page(self, url):
        """
        获取网页内容的函数
        这是任何爬虫项目最基础的函数，负责获取网页内容
        如果这个函数失败，整个爬虫就无法工作
        """
        try:
            # 设置请求头，这是爬虫的关键技巧之一
            # 如果不设置请求头，很多网站会拒绝访问
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # 发送GET请求获取网页内容
            # 这是爬虫最关键的一步，相当于在浏览器中打开网页
            response = requests.get(url, headers=headers)
            
            # 设置正确的编码，防止中文乱码
            response.encoding = 'utf-8'
            
            # 返回网页的文本内容
            return response.text
            
        except Exception as e:
            # 错误处理很重要！实际爬取时经常会遇到各种错误
            # 比如网络断开、网站超时等
            print(f"获取页面失败: {str(e)}")
            return None

    def parse_quotes(self, html):
        """
        解析网页内容的函数
        这是爬虫的第二个关键部分，负责从网页中提取我们需要的数据
        每个爬虫项目的这部分都不同，需要根据网页结构来写
        """
        # 创建BeautifulSoup对象，用于解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 找到所有包含名言的div元素
        # 这里的class_='quote'是通过观察网页结构得到的
        # 做新的爬虫项目时，需要自己观察网页找到正确的标签和类名
        quotes = soup.find_all('div', class_='quote')
        
        # 遍历每个名言元素，提取信息
        for quote in quotes:
            # 提取名言文本
            # 观察发现名言在class='text'的span标签中
            text = quote.find('span', class_='text').text.strip('""')
            
            # 提取作者名称
            # 作者在class='author'的small标签中
            author = quote.find('small', class_='author').text
            
            # 提取标签
            # 所有标签都在class='tag'的a标签中
            tags = [tag.text for tag in quote.find_all('a', class_='tag')]
            
            # 将数据组织成字典格式
            # 这种数据结构便于后续处理和保存
            quote_data = {
                'text': text,
                'author': author,
                'tags': tags
            }
            
            # 将提取的数据添加到存储列表中
            self.quotes_data.append(quote_data)
            
            # 打印进度信息
            # 这在开发调试时很有用，可以看到爬虫的工作状态
            print(f"\n--- 已抓取新名言 ---")
            print(f"作者: {author}")
            print(f"名言: {text[:50]}..." if len(text) > 50 else f"名言: {text}")
            print(f"标签: {', '.join(tags)}")

    def has_next_page(self, html):
        """
        检查是否有下一页的函数
        对于有分页的网站来说，这个函数很重要
        它决定了爬虫何时停止
        """
        soup = BeautifulSoup(html, 'html.parser')
        # 查找下一页按钮
        # 这需要观察网页结构来确定下一页按钮的特征
        next_button = soup.find('li', class_='next')
        return next_button is not None

    def crawl_all_pages(self):
        """
        爬取所有页面的主函数
        这是爬虫的控制中心，协调其他函数工作
        """
        current_url = self.base_url  # 从第一页开始
        page_num = 1  # 页面计数器
        
        # 循环爬取每一页
        while True:
            print(f"\n正在爬取第 {page_num} 页...")
            
            # 获取页面内容
            html = self.get_page(current_url)
            
            # 如果获取页面失败，就退出循环
            if not html:
                break
            
            # 解析当前页面的内容
            self.parse_quotes(html)
            
            # 检查是否还有下一页
            if not self.has_next_page(html):
                print("\n已到达最后一页")
                break
            
            # 构造下一页的URL
            soup = BeautifulSoup(html, 'html.parser')
            next_button = soup.find('li', class_='next')
            next_page = next_button.find('a')['href']
            current_url = f"{self.base_url}{next_page}"
            
            # 页面计数加1
            page_num += 1
            
            # 重要！添加延时避免请求过快
            # 这是爬虫的礼貌，也是避免被封禁的关键
            time.sleep(1)

    def save_to_file(self):
        """
        保存数据的函数
        这是爬虫的最后一步，将数据持久化存储
        """
        # 保存为JSON格式，便于程序读取
        with open('quotes.json', 'w', encoding='utf-8') as f:
            json.dump(self.quotes_data, f, ensure_ascii=False, indent=2)
        
        # 保存为文本格式，便于人类阅读
        with open('quotes.txt', 'w', encoding='utf-8') as f:
            for i, quote in enumerate(self.quotes_data, 1):
                f.write(f"\n=== 名言 {i} ===\n")
                f.write(f"作者: {quote['author']}\n")
                f.write(f"名言: {quote['text']}\n")
                f.write(f"标签: {', '.join(quote['tags'])}\n")
                f.write("\n")
        
        # 打印统计信息
        print(f"\n共抓取 {len(self.quotes_data)} 条名言")
        print("数据已保存到 quotes.json 和 quotes.txt")

# ===== 程序入口 =====
def main():
    """
    主函数，程序的入口点
    创建爬虫对象并执行爬取任务
    """
    crawler = QuotesCrawler()  # 创建爬虫对象
    crawler.crawl_all_pages()  # 开始爬取
    crawler.save_to_file()     # 保存数据

# 当直接运行此文件时执行main函数
if __name__ == "__main__":
    main()
