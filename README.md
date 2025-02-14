# 1688商品爬虫

这是一个用于爬取1688.com商品信息的Python爬虫程序。该程序可以自动搜索和提取商品信息，包括标题、价格、销量、供应商等详细信息。

## 功能特点

- 自动搜索指定关键词的商品
- 支持扫码登录1688账号
- 提取商品详细信息：
  - 商品标题
  - 价格信息
  - 销量数据
  - 供应商信息
  - 商品链接
  - 商品图片
  - 回头率
- 自动保存数据为JSON格式
- 支持多页爬取
- 自动处理动态加载内容
- 智能处理验证码提示

## 环境要求

- Python 3.6+
- Chrome浏览器
- 以下Python包：
  ```
  selenium
  requests
  beautifulsoup4
  webdriver_manager
  ```

## 安装说明

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/your-username/1688crawler.git
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行程序：
   ```bash
   python alibaba_crawler.py
   ```

2. 按照提示完成登录：
   - 等待浏览器打开
   - 点击右上角"请登录"按钮
   - 使用阿里巴巴/淘宝App扫码登录
   - 登录成功后按回车继续

3. 输入搜索关键词：
   - 输入想要搜索的商品关键词
   - 确认搜索关键词
   - 输入要爬取的页数（直接回车默认为3页）

4. 等待程序完成爬取：
   - 如果出现验证码，请手动完成验证
   - 程序会自动保存结果到 alibaba_data 目录

## 数据格式

爬取的数据将保存为JSON格式，包含以下字段：
```json
{
  "title": "商品标题",
  "price": "价格",
  "min_order": "起订量",
  "company": "供应商名称",
  "location": "供应商地址",
  "rating": "商品评分",
  "reviews": "评价数量",
  "deals": "成交量",
  "link": "商品链接",
  "image_url": "商品图片链接"
}
```

## 注意事项

1. **反爬处理**：
   - 程序内置了随机延时
   - 模拟真实用户行为
   - 自动处理基本的反爬验证

2. **登录说明**：
   - 首次使用需要登录
   - 建议使用扫码登录
   - 登录信息会临时保存在会话中

3. **使用限制**：
   - 请合理控制爬取频率
   - 建议单次爬取页数不超过10页
   - 遵守网站的robots.txt规则

## 常见问题

1. **验证码处理**：
   - 出现验证码时请手动完成验证
   - 验证完成后程序会自动继续

2. **数据保存**：
   - 数据默认保存在 alibaba_data 目录
   - 每页数据单独保存，避免数据丢失
   - 支持断点续爬

3. **错误处理**：
   - 程序会自动重试失败的请求
   - 详细的错误日志帮助排查问题
   - 支持手动中断和继续

## 开发计划

- [ ] 添加代理IP支持
- [ ] 实现多线程爬取
- [ ] 添加数据分析功能
- [ ] 支持更多数据格式导出
- [ ] 添加GUI界面

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。  