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
            # 直接访问1688主页
            self.driver.get("https://www.1688.com")
            time.sleep(2)
            
            print("\n=== 登录指引 ===")
            print("1. 点击页面右上角的'请登录'按钮")
            print("2. 在登录界面选择'扫码登录'")
            print("3. 使用阿里巴巴/淘宝 App扫码")
            print("4. 登录成功后，请按回车继续...")
            input()
            
            # 简化登录验证
            time.sleep(2)  # 等待页面状态更新
            
            # 直接获取Cookie
            cookies = self.driver.get_cookies()
            if cookies:
                cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                print("成功获取Cookie！")
                return cookie_string
            else:
                print("未获取到Cookie，请确认是否已登录")
                return None
                
        except Exception as e:
            print(f"登录过程中出错: {e}")
            return None
            
    def search_products(self, keyword, max_pages=3):
        """搜索并获取产品信息"""
        all_products = []
        
        try:
            print(f"正在搜索: {keyword}")
            
            # 使用urllib.parse.quote正确编码中文关键词
            encoded_keyword = quote(keyword, encoding='gb2312')
            search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded_keyword}"
            print(f"访问URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(5)  # 增加等待时间
            
            print("等待页面加载...")
            
            # 等待任意一个可能的元素出现
            selectors = [
                '.sm-offer-item',  # 新版商品项
                '.offer-item',     # 传统商品项
                '.grid-item',      # 网格布局商品项
                'img.main-img',    # 商品图片
                '.price-item',     # 价格项
                '.title'           # 标题
            ]
            
            found = False
            for selector in selectors:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"找到元素: {selector}")
                    found = True
                    break
                except TimeoutException:
                    continue
            
            if not found:
                print("未找到任何商品元素，可能需要处理验证码")
                input("请处理验证码后按回车继续...")
                time.sleep(2)
            
            # 滚动页面以加载所有内容
            print("滚动页面加载更多内容...")
            self.scroll_page()
            time.sleep(3)  # 增加等待时间
            
            # 检查是否需要处理验证码
            if "验证" in self.driver.page_source or "滑块" in self.driver.page_source:
                print("\n检测到验证码，请手动完成验证...")
                input("完成验证后按回车继续...")
                time.sleep(2)
            
            # 直接使用JavaScript提取商品信息
            print("\n尝试使用JavaScript提取商品信息...")
            products = self.extract_products_js()
            
            if products:
                all_products.extend(products)
                print(f"成功提取 {len(products)} 个商品")
                self.save_page_data(products, keyword, 1)
            else:
                print("未能提取到商品信息，尝试备用方法...")
                # 保存页面源码以供分析
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print("页面源码已保存到 debug_page.html")
                
                # 让用户确认页面状态
                print("\n请检查页面是否正常显示商品列表")
                input("确认后按回车继续...")
                
                # 尝试备用提取方法
                products = self.extract_products_backup()
                if products:
                    all_products.extend(products)
                    print(f"备用方法成功提取 {len(products)} 个商品")
                    self.save_page_data(products, keyword, 1)
            
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
            
    def extract_products_js(self):
        """使用JavaScript提取商品信息"""
        try:
            # 使用JavaScript提取商品信息
            products = self.driver.execute_script("""
                const products = [];
                // 查找所有可能的商品容器
                const items = document.querySelectorAll('.sm-offer-item, .offer-item, .grid-item, [data-offer-id]');
                
                items.forEach(item => {
                    try {
                        const product = {};
                        
                        // 提取图片
                        const img = item.querySelector('img.main-img');
                        if (img) {
                            product.image_url = img.src;
                        }
                        
                        // 提取标题
                        const titleEl = item.querySelector('.title') || 
                                      item.querySelector('[title]') ||
                                      item.querySelector('div:not([class])');
                        if (titleEl) {
                            product.title = titleEl.innerText.trim() || titleEl.getAttribute('title');
                        }
                        
                        // 提取价格
                        const priceItem = item.querySelector('.price-item');
                        if (priceItem) {
                            const priceText = priceItem.textContent.trim();
                            if (priceText) {
                                product.price = priceText;
                            }
                        }
                        
                        // 提取链接
                        const link = item.querySelector('a[href*="detail.1688.com"]');
                        if (link) {
                            product.link = link.href;
                        }
                        
                        if (product.title && product.price) {
                            products.push(product);
                        }
                    } catch (e) {
                        console.error('提取商品信息时出错:', e);
                    }
                });
                
                return products;
            """)
            
            return products
        except Exception as e:
            print(f"JavaScript提取失败: {e}")
            return []

    def extract_products_backup(self):
        """备用的提取方法"""
        products = []
        try:
            # 查找所有图片元素
            images = self.driver.find_elements(By.CSS_SELECTOR, 'img.main-img')
            print(f"找到 {len(images)} 个商品图片")
            
            for img in images:
                try:
                    product = {}
                    
                    # 获取图片URL
                    product['image_url'] = img.get_attribute('src')
                    
                    # 获取父元素
                    parent = img.find_element(By.XPATH, '../..')
                    
                    # 查找标题
                    try:
                        title = parent.find_element(By.CSS_SELECTOR, 'div:not([class])')
                        product['title'] = title.text.strip()
                    except:
                        continue
                    
                    # 查找价格
                    try:
                        price_item = parent.find_element(By.CSS_SELECTOR, '.price-item')
                        product['price'] = price_item.text.strip()
                    except:
                        continue
                    
                    if product.get('title') and product.get('price'):
                        products.append(product)
                        print(f"找到商品: {product['title'][:30]}...")
                    
                except Exception as e:
                    print(f"处理单个商品时出错: {e}")
                    continue
            
        except Exception as e:
            print(f"备用提取方法出错: {e}")
        
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
    """主函数：程序入口点"""
    crawler = AlibabaCrawler()
    
    try:
        print("\n=== 1688商品爬虫 ===")
        print("程序将打开浏览器，请按照提示操作...")
        
        # 获取登录Cookie
        cookie = crawler.login_with_cookie("")
        if not cookie:
            print("获取Cookie失败，程序退出")
            return
        
        while True:
            try:
                # 获取爬取参数
                keyword = input("\n请输入要搜索的产品关键词（输入q退出）: ").strip()
                if not keyword:
                    print("关键词不能为空！")
                    continue
                    
                if keyword.lower() == 'q':
                    break
                
                # 验证输入的关键词
                print(f"您要搜索的是: {keyword}")
                if input("确认搜索这个关键词吗？(y/n): ").lower() != 'y':
                    continue
                
                max_pages = input("请输入要爬取的页数（直接回车默认为3页）: ")
                max_pages = int(max_pages) if max_pages.strip() else 3
                
                # 执行爬取
                products = crawler.search_products(keyword, max_pages)
                
                # 输出结果
                print(f"\n爬取完成！")
                print(f"共获取 {len(products)} 个商品信息")
                print(f"数据保存在 {crawler.output_dir} 目录下")
                
                # 询问是否继续
                if input("\n是否继续搜索其他产品？(y/n): ").lower() != 'y':
                    break
                    
            except ValueError:
                print("请输入有效的页数！")
            except Exception as e:
                print(f"发生错误: {e}")
                if input("是否继续？(y/n): ").lower() != 'y':
                    break
                
    finally:
        # 确保浏览器被正确关闭
        crawler.close()

if __name__ == "__main__":
    main() 