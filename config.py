"""
爬虫配置文件
"""
CONFIG = {
    'WAIT_TIME': 10,  # 显式等待时间
    'PAGE_LOAD_WAIT': 3,  # 页面加载等待时间
    'SCROLL_WAIT': 2,  # 滚动等待时间
    'RETRY_COUNT': 3,  # 重试次数
    'HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    'OUTPUT_DIR': 'alibaba_data',
    'CHROME_OPTIONS': [
        '--disable-gpu',
        '--window-size=1920,1080',
        '--no-sandbox',
        '--disable-dev-shm-usage'
    ]
} 