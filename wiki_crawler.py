import requests
from bs4 import BeautifulSoup

def crawl_wikipedia(url):
    try:
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        # 发送请求
        print(f"正在请求页面: {url}")
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        # 检查响应状态
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return
        
        # 解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 获取标题
        title = soup.find(id='firstHeading').text
        print("\n=== 文章标题 ===")
        print(title)
        
        # 2. 获取第一段摘要
        # 查找第一个有实际内容的段落（跳过可能的警告框和空段落）
        intro = None
        for p in soup.find('div', class_='mw-parser-output').find_all('p'):
            if p.text.strip() and not p.find_parent(class_='hatnote'):
                intro = p
                break
                
        print("\n=== 文章摘要 ===")
        print(intro.text.strip() if intro else "未找到摘要")
        
        # 3. 获取目录
        print("\n=== 目录 ===")
        toc = soup.find(id='toc')
        if toc:
            for item in toc.find_all('span', class_='toctext'):
                # 获取目录层级（通过父元素的class判断）
                level = len(item.find_parent('li').find_parent('ul').find_parents('ul')) + 1
                indent = "  " * (level - 1)
                print(f"{indent}- {item.text}")
        else:
            print("未找到目录")
            
        # 4. 获取页面内部链接
        print("\n=== 内部链接 ===")
        # 找到主要内容区域
        content = soup.find('div', class_='mw-parser-output')
        # 获取所有内部链接（以/wiki/开头的链接）
        internal_links = set()  # 使用set去重
        for link in content.find_all('a'):
            href = link.get('href', '')
            if href.startswith('/wiki/') and ':' not in href:  # 排除特殊页面（如Category:, File:等）
                internal_links.add(link.text.strip())
        
        # 打印内部链接
        for link in sorted(internal_links):  # 排序后输出
            if link:  # 确保链接文本不为空
                print(f"- {link}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # 可以选择中文或英文维基百科的链接
    # 这里使用Python的维基百科页面作为示例
    wiki_url = "https://zh.wikipedia.org/wiki/Python"  # 中文
    # wiki_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"  # 英文
    
    crawl_wikipedia(wiki_url) 