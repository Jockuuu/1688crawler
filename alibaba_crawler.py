# ===== 第一部分：导入必要的库 =====
import requests  # 用于发送网络请求（用于下载图片等简单请求）
from bs4 import BeautifulSoup  # 用于解析HTML（作为备用）
import json  # 用于保存数据为JSON格式
import time  # 用于添加延时
import os  # 用于文件和目录操作
from urllib.parse import quote  # 用于URL编码
import random  # 用于随机延时

# Selenium相关的导入
# 这些是爬取动态网站必需的库
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # 用于定位元素
from selenium.webdriver.support.ui import WebDriverWait  # 用于显式等待
from selenium.webdriver.support import expected_conditions as EC  # 用于设置等待条件
from selenium.common.exceptions import TimeoutException  # 用于处理超时异常

class AlibabaCrawler:
    def __init__(self):
        """
        初始化爬虫类
        自动安装和配置 ChromeDriver
        """
        self.setup_driver()
        self.output_dir = 'alibaba_data'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def setup_driver(self):
        """设置Chrome驱动，使用webdriver_manager自动安装"""
        try:
            chrome_options = Options()
            # 添加更多的选项来模拟真实浏览器
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            # 添加以下选项来减少被检测的概率
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 使用 webdriver_manager 自动安装和管理 ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行 JavaScript 来隐藏 Selenium 的特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            self.wait = WebDriverWait(self.driver, 10)
            print("Chrome驱动设置成功！")
            
        except Exception as e:
            print(f"设置Chrome驱动时出错: {e}")
            raise
        
    def login_with_cookie(self, cookie_string):
        """使用扫码方式登录1688"""
        try:
            # 直接访问1688登录页面
            self.driver.get("https://login.1688.com/member/signin.htm")
            time.sleep(2)  # 等待页面加载
            
            print("\n=== 登录指引 ===")
            print("1. 如果出现滑块验证，请按以下步骤操作：")
            print("   - 将鼠标移动到滑块上")
            print("   - 按住滑块慢慢拖动（模拟人工操作）")
            print("   - 如果失败请多尝试几次")
            print("2. 在页面上寻找二维码登录选项")
            print("3. 使用阿里巴巴/淘宝 App扫码登录")
            print("4. 登录成功后，请按回车继续...")
            input()
            
            # 验证登录状态
            print("正在验证登录状态...")
            
            # 先等待页面跳转到1688主页
            time.sleep(3)  # 给跳转一些时间
            
            # 检查当前URL是否已经跳转到1688域名
            current_url = self.driver.current_url
            if not "1688.com" in current_url:
                print(f"当前页面URL: {current_url}")
                print("等待页面跳转...")
                time.sleep(5)  # 多等待一会
            
            try:
                # 尝试多个可能的登录成功标识
                login_selectors = [
                    '.user-info',
                    '.member-name',
                    '.login-info',
                    '.user-avatar',
                    '.header-user-menu',
                    '.user-account',
                    'a[href*="member/"]',  # 包含member的链接
                    '.sm-widget-user'  # 新增可能的选择器
                ]
                
                print("检查登录状态...")
                for selector in login_selectors:
                    try:
                        element = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        print(f"找到登录标识: {selector}")
                        break
                    except TimeoutException:
                        continue
                else:
                    print("未找到任何登录标识")
                    # 尝试访问会员中心页面来验证登录
                    self.driver.get("https://work.1688.com/")
                    time.sleep(3)
                    
                # 获取所有Cookie
                cookies = self.driver.get_cookies()
                cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                
                # 验证Cookie是否包含关键值
                if any(cookie['name'] in ['_csrf_token', 'cookie2', '_tb_token_'] for cookie in cookies):
                    print("成功获取有效Cookie！")
                    return cookie_string
                else:
                    print("Cookie可能无效，请检查登录状态")
                    return None
                    
            except Exception as e:
                print(f"验证登录状态时出错: {e}")
                print("当前页面URL:", self.driver.current_url)
                print("尝试重新验证...")
                
                # 尝试重新加载页面
                self.driver.get("https://www.1688.com")
                time.sleep(3)
                
                # 再次获取Cookie
                cookies = self.driver.get_cookies()
                cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                return cookie_string
                
        except Exception as e:
            print(f"登录过程中出错: {e}")
            return None
            
    def search_products(self, keyword, max_pages=3):
        """搜索并获取产品信息"""
        all_products = []
        retry_count = 3  # 添加重试机制
        
        try:
            search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(keyword)}"
            
            for attempt in range(retry_count):
                try:
                    self.driver.get(search_url)
                    break
                except Exception as e:
                    if attempt == retry_count - 1:
                        raise
                    print(f"访问搜索页面失败，正在重试 ({attempt + 1}/{retry_count})")
                    time.sleep(2)
            
            # 处理每一页
            for page in range(1, max_pages + 1):
                print(f"\n正在处理第 {page} 页...")
                
                # 等待商品列表加载完成
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'offer-list-row')))
                
                # 滚动页面以加载所有商品
                self.scroll_page()
                
                # 提取商品信息
                products = self.extract_products()
                all_products.extend(products)
                
                print(f"第 {page} 页获取到 {len(products)} 个商品")
                
                # 保存当前页数据
                self.save_page_data(products, keyword, page)
                
                # 处理翻页
                if page < max_pages:
                    try:
                        # 查找并点击下一页按钮
                        next_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.page-next'))
                        )
                        next_button.click()
                        time.sleep(2)
                    except TimeoutException:
                        print("没有找到下一页按钮，可能已经是最后一页")
                        break
                        
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            
        return all_products
        
    def scroll_page(self):
        """
        滚动页面以加载所有商品
        这是处理动态加载的关键步骤
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 等待内容加载
            
            # 检查是否已经到底
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
    def extract_products(self):
        """
        提取商品信息
        使用Selenium的元素定位功能
        """
        products = []
        
        # 更新选择器，使用更通用的方式
        items = self.driver.find_elements(By.CSS_SELECTOR, '.offer-list-row-offer, .list-item')  # 添加备选选择器
        
        for item in items:
            try:
                # 使用更灵活的选择器组合
                product = {
                    'title': item.find_element(By.CSS_SELECTOR, 'h2.title, .title a').text.strip(),
                    'price': item.find_element(By.CSS_SELECTOR, '.price, .price-container').text.strip(),
                    'min_order': item.find_element(By.CSS_SELECTOR, '.min-order, .order-info').text.strip(),
                    'company': item.find_element(By.CSS_SELECTOR, '.company-name, .company').text.strip(),
                    'location': item.find_element(By.CSS_SELECTOR, '.location, .address').text.strip(),
                    'link': item.find_element(By.CSS_SELECTOR, 'a.title-link, .title a').get_attribute('href'),
                    'image_url': item.find_element(By.CSS_SELECTOR, 'img.offer-image, .item-image').get_attribute('src')
                }
                
                # 下载商品图片
                if product['image_url']:
                    product['local_image'] = self.download_image(
                        product['image_url'],
                        f"product_{len(products)}_{int(time.time())}.jpg"
                    )
                
                products.append(product)
                print(f"找到商品: {product['title'][:30]}...")
                
            except Exception as e:
                print(f"提取商品信息时出错: {e}")
                continue
                
        return products
        
    def download_image(self, url, filename):
        """
        下载商品图片
        使用requests直接下载，而不是截图
        """
        try:
            if not url:
                return None
            
            # 确保图片目录存在
            image_dir = os.path.join(self.output_dir, 'images')
            os.makedirs(image_dir, exist_ok=True)
            
            # 完整的保存路径
            save_path = os.path.join(image_dir, filename)
            
            # 使用requests下载图片
            response = requests.get(url, headers={
                'User-Agent': self.driver.execute_script("return navigator.userAgent"),
                'Referer': 'https://www.1688.com/'
            })
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return filename
            
        except Exception as e:
            print(f"下载图片失败 {url}: {e}")
        return None
            
    def save_page_data(self, products, keyword, page):
        """保存每页数据到JSON文件"""
        json_filename = os.path.join(
            self.output_dir, 
            f'{keyword}_page{page}_{int(time.time())}.json'
        )
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            
        print(f"数据已保存到: {json_filename}")
        
    def close(self):
        """
        关闭浏览器
        清理资源很重要
        """
        self.driver.quit()

def main():
    """
    主函数：程序入口点
    包含完整的使用流程
    """
    crawler = AlibabaCrawler()
    
    try:
        print("\n=== 1688商品爬虫 ===")
        print("程序将打开浏览器，请按照提示操作...")
        
        # 获取登录Cookie
        cookie = crawler.login_with_cookie("")
        if not cookie:
            print("获取Cookie失败，程序退出")
            return
            
        # 获取爬取参数
        keyword = input("请输入要搜索的产品关键词: ")
        max_pages = int(input("请输入要爬取的页数: "))
        
        # 执行爬取
        products = crawler.search_products(keyword, max_pages)
        
        # 输出结果
        print(f"\n爬取完成！")
        print(f"共获取 {len(products)} 个商品信息")
        print(f"数据保存在 {crawler.output_dir} 目录下")
        
    finally:
        # 确保浏览器被正确关闭
        crawler.close()

if __name__ == "__main__":
    main() 