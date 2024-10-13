# 学科网教材信息爬虫

这个项目是一个用于爬取中小学教材版本、年级、学科、学段信息的爬虫程序。它主要针对 https://yw.zxxk.com/p/books/ 网站进行爬取，并将结果结构化保存到 output.txt 文件中。

## 功能特点

- 自动分析网站结构和爬取目标
- 使用 Selenium 和 BeautifulSoup 进行网页解析和信息提取
- 支持动态内容加载
- 详细的日志记录
- 集成大模型 API 进行智能分析和决策
- 循环爬取和分析，不断优化爬取策略

## 文件说明

- `爬虫.py`: 主要的爬虫程序
- `crawler.log`: 爬虫运行日志
- `output.txt`: 爬取结果输出文件

## 准备工作

1. **Python 环境**：
   - 确保您的系统已安装 Python 3.7 或更高版本。

2. **依赖库**：
   安装所需的 Python 库：
   ```
   pip install selenium beautifulsoup4 requests webdriver-manager python-dotenv
   ```

3. **ChromeDriver**：
   - 不再需要手动下载 ChromeDriver，代码会自动管理。

4. **大模型 API**：
   - API来源：https://p33279i881.vicp.fun/log
   - API地址：`https://p33279i881.vicp.fun/v1/chat/completions`
   - 使用的模型：`moonshot-v1-128k`
   - 在 `callAI` 函数中已实现API调用逻辑。

## API密钥配置

为了保护API密钥，我们使用环境变量来存储它。请按照以下步骤操作：

1. 在项目根目录创建一个名为 `.env` 的文件。
2. 在 `.env` 文件中添加以下内容：

   ```
   API_KEY=your_api_key_here
   ```

   将 `your_api_key_here` 替换为您的实际API密钥。

3. 确保 `.env` 文件已添加到 `.gitignore` 中，以防止它被提交到版本控制系统。

## 使用方法

1. 克隆或下载本项目到本地。

2. 按照上述说明配置API密钥。

3. 如果需要更改目标网站，修改 `爬虫.py` 文件开头的 `TARGET_URL` 常量：
   ```python
   TARGET_URL = "https://your-target-website.com"
   ```

4. 运行爬虫：
   ```
   python 爬虫.py
   ```

5. 程序运行过程中，会询问是否继续爬取。输入 'y' 继续，或其他键退出。

6. 爬取结果将保存在 `output.txt` 文件中，日志信息保存在 `crawler.log` 文件中。

## 爬虫工作流程

1. 分析识别待爬取的网站和爬取任务目标。
2. 进行初步爬取，将结果记录在日志中。
3. 重新分析日志结果，找到下一步可能的爬取思路、框架、元素。
4. 重复步骤2和3，询问用户是否继续循环。
5. 分析目标和实际结果之间的差异。

## 注意事项

- 请遵守网站的使用条款和爬虫协议。
- 适当调整爬取频率，避免对目标网站造成过大压力。
- 定期检查和更新 ChromeDriver，以确保与 Chrome 浏览器版本兼容。
- 不要将包含API密钥的 `.env` 文件提交到公共仓库。

## 贡献

欢迎提交问题和改进建议。如果您想贡献代码，请先开 issue 讨论您想要改变的内容。

## 许可

[MIT License](LICENSE)