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
            encoded_keyword = quote(keyword, encoding='gb2312')  # 1688使用gb2312编码
            search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded_keyword}"
            print(f"访问URL: {search_url}")  # 调试用
            
            try:
                self.driver.get(search_url)
            except Exception as e:
                print(f"访问搜索页面失败: {e}")
                # 尝试备用方法
                backup_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(keyword)}"
                print(f"尝试备用URL: {backup_url}")
                self.driver.get(backup_url)
            
            time.sleep(3)  # 等待页面加载
            
            # 检查URL是否正确加载
            current_url = self.driver.current_url
            print(f"当前页面URL: {current_url}")
            
            # 如果URL不包含关键词，可能需要手动处理
            if "keywords" not in current_url:
                print("搜索页面可能未正确加载，尝试直接在搜索框输入")
                try:
                    # 尝试找到搜索框并输入
                    search_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="keywords"], #search-input, .search-input'))
                    )
                    search_input.clear()
                    search_input.send_keys(keyword)
                    
                    # 点击搜索按钮
                    search_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.search-button, .search-submit'))
                    )
                    search_button.click()
                    time.sleep(3)
                except Exception as e:
                    print(f"手动搜索失败: {e}")
            
            # 处理可能出现的验证码
            print("如果出现验证码，请手动完成验证后按回车继续...")
            input()
            
            # 处理每一页
            for page in range(1, max_pages + 1):
                print(f"\n正在处理第 {page} 页...")
                
                # 等待商品列表加载
                try:
                    # 尝试多个可能的商品列表选择器
                    selectors = [
                        '.offer-list-row',
                        '.list-content',
                        '.organic-offer-list',
                        '.grid-list',
                        '.sm-offer-item',  # 新增选择器
                        '.offer-item',     # 新增选择器
                        '.item-content'    # 新增选择器
                    ]
                    
                    found_selector = None
                    for selector in selectors:
                        try:
                            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                            print(f"找到商品列表: {selector}")
                            found_selector = selector
                            break
                        except TimeoutException:
                            continue
                            
                    if not found_selector:
                        print("未找到商品列表，可能需要处理验证码")
                        print("请处理完验证码后按回车继续...")
                        input()
                        continue
                    
                    # 滚动页面以加载所有商品
                    self.scroll_page()
                    
                    # 提取商品信息
                    products = self.extract_products()
                    if products:
                        all_products.extend(products)
                        print(f"第 {page} 页获取到 {len(products)} 个商品")
                        
                        # 保存当前页数据
                        self.save_page_data(products, keyword, page)
                    else:
                        print("当前页面未找到商品")
                        break
                    
                    # 处理翻页
                    if page < max_pages:
                        try:
                            # 尝试多个翻页按钮选择器
                            next_selectors = [
                                'a.page-next',
                                '.next-page',
                                'button[aria-label="下一页"]',
                                '.pagination-next',
                                '.next',  # 新增选择器
                                '[title="下一页"]'  # 新增选择器
                            ]
                            
                            clicked = False
                            for selector in next_selectors:
                                try:
                                    next_button = self.wait.until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    next_button.click()
                                    clicked = True
                                    time.sleep(2)
                                    break
                                except TimeoutException:
                                    continue
                                    
                            if not clicked:
                                print("没有找到下一页按钮，可能已经是最后一页")
                                break
                                
                        except Exception as e:
                            print(f"翻页失败: {e}")
                            break
                            
                except Exception as e:
                    print(f"处理第 {page} 页时出错: {e}")
                    print("如果出现验证码，请手动处理后按回车继续...")
                    input()
                    continue
                
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            print("请检查网页状态，如果需要处理验证码，请处理后按回车继续...")
            input()
            
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
        """提取商品信息"""
        products = []
        
        # 更新选择器，使用更多的可能组合
        selectors = [
            '.offer-list-row-offer, .list-item',
            '.sm-offer-item',
            '.offer-item',
            '.item-content'
        ]
        
        items = []
        for selector in selectors:
            items.extend(self.driver.find_elements(By.CSS_SELECTOR, selector))
        
        if not items:
            print("未找到商品元素，可能需要更新选择器")
            return products
        
        for item in items:
            try:
                # 使用更灵活的选择器组合
                try:
                    title = item.find_element(By.CSS_SELECTOR, 
                        'h2.title, .title a, .title, .item-title').text.strip()
                except:
                    continue  # 如果找不到标题，跳过这个商品
                    
                try:
                    price = item.find_element(By.CSS_SELECTOR, 
                        '.price, .price-container, .price-info').text.strip()
                except:
                    price = "价格未知"
                    
                try:
                    min_order = item.find_element(By.CSS_SELECTOR, 
                        '.min-order, .order-info, .min-quantity').text.strip()
                except:
                    min_order = "起订量未知"
                    
                try:
                    company = item.find_element(By.CSS_SELECTOR, 
                        '.company-name, .company, .store-name').text.strip()
                except:
                    company = "商家未知"
                    
                try:
                    location = item.find_element(By.CSS_SELECTOR, 
                        '.location, .address, .delivery-location').text.strip()
                except:
                    location = "地址未知"
                    
                try:
                    link = item.find_element(By.CSS_SELECTOR, 
                        'a.title-link, .title a, a[href*="detail"]').get_attribute('href')
                except:
                    link = ""
                    
                try:
                    image_url = item.find_element(By.CSS_SELECTOR, 
                        'img.offer-image, .item-image, img[src*="img.alicdn.com"]').get_attribute('src')
                except:
                    image_url = ""
                
                product = {
                    'title': title,
                    'price': price,
                    'min_order': min_order,
                    'company': company,
                    'location': location,
                    'link': link,
                    'image_url': image_url
                }
                
                products.append(product)
                print(f"找到商品: {title[:30]}...")
                
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