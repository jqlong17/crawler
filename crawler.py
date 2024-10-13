# 本项目目标：爬取中小学教材版本、年级、学科、学段信息，结构化的保存到output.txt
# 不断的校验 log.txt以及output.txt文件，如果找到"信息不足"字样，则询问是否重新爬取该页面
# 整个代码按照以下步骤进行
# 1.分析识别待爬取的网站和爬取任务目标，并将识别的一些想法和结果记录在日志log.txt中，log中说明是第一步分析阶段
# 2.进行初步的爬取，根据上一步分析的结果，简单的进行初步的爬取，并且将爬取的结果记录在log中，说明这是一个初步的结果尝试（注意这步骤关键是框架和尝试，而不是详细的爬取）
# 3. 重新分析，这次请分析log日志的结果，对结果进行分析，从而找到下一步可能的爬取思路、框架、元素。
# 4. 重复第二步骤和第三步骤各一次，并且询问用户是否继续这个循环。给出分析，目标和实际结果之间的差异还有多少。

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import json
import os
from dotenv import load_dotenv

# 在文件开头添加以下代码
load_dotenv()  # 加载 .env 文件中的环境变量

# 待爬取的网站URL
TARGET_URL = "https://yw.zxxk.com/p/books/"

# 设置日志记录
logging.basicConfig(filename='crawler.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_webpage_content(url):
    """
    获取网页内容
    :param url: 目标网页URL
    :return: BeautifulSoup对象或None（如果获取失败）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果响应状态不是200，将引发HTTPError异常
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logging.error(f"获取网页内容时出错: {e}")
        return None

def analyze_webpage_structure(soup):
    """
    分析网页结构
    :param soup: BeautifulSoup对象
    :return: 包含网页结构信息的字典
    """
    return {
        "title": soup.title.string if soup.title else "No title found",
        "headings": [h.text for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
        "links": len(soup.find_all('a')),
        "divs": len(soup.find_all('div')),
        "classes": list(set([cls for tag in soup.find_all() for cls in tag.get('class', [])]))
    }

def callAI(prompt):
    """
    调用AI模型进行分析
    :param prompt: 提示文本
    :return: AI模型的响应或None（如果调用失败）
    """
    url = "https://p33279i881.vicp.fun/v1/chat/completions"
    payload = {
        "model": "moonshot-v1-128k",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': os.getenv('API_KEY')
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        logging.error(f"调用API时发生错误：{str(e)}")
        return None

def analyze_website(task_id, url):
    """
    分析网站结构并调用AI进行解析
    :param task_id: 任务ID
    :param url: 目标网页URL
    :return: AI分析结果
    """
    soup = get_webpage_content(url)
    if not soup:
        return "无法获取网页内容"
    structure_info = analyze_webpage_structure(soup)
    prompt = f"分析以下网站结构信息，重点关注如何提取中小学教材版本、年级、学科、学段信息：{json.dumps(structure_info, ensure_ascii=False)}"
    analysis_result = callAI(prompt)
    logging.info(f"任务ID: {task_id} - 分析结果: {analysis_result}")
    return analysis_result

def extract_information(soup, task_id):
    """
    从网页内容中提取所需信息
    :param soup: BeautifulSoup对象
    :param task_id: 任务ID
    :return: 提取的信息列表
    """
    extracted_data = []
    try:
        sections = soup.find_all('div', class_='book-item')
        for section in sections:
            try:
                stage = section.find('span', class_='stage').text.strip()
                subject = section.find('span', class_='subject').text.strip()
                version = section.find('span', class_='version').text.strip()
                grade = section.find('span', class_='grade').text.strip()
                extracted_data.append((stage, subject, version, grade))
            except AttributeError as e:
                logging.warning(f"任务ID: {task_id} - 信息提取不完整: {e}")
                extracted_data.append(("信息不足", "信息不足", "信息不足", "信息不足"))
    except Exception as e:
        logging.error(f"任务ID: {task_id} - 提取信息时出错: {e}")
    return extracted_data

def setup_driver():
    """
    设置并返回Chrome WebDriver
    :return: Chrome WebDriver实例
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_data(task_id, url):
    """
    爬取网页数据
    :param task_id: 任务ID
    :param url: 目标网页URL
    :return: 提取的数据列表
    """
    try:
        driver = setup_driver()
        logging.info(f"任务ID: {task_id} - 访问URL: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "book-item")))
        
        # 处理动态内容，滚动页面以加载更多内容
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        extracted_data = extract_information(soup, task_id)
        
        # 将提取的数据写入output.txt文件
        with open('output.txt', 'w', encoding='utf-8') as file:
            for stage, subject, version, grade in extracted_data:
                file.write(f"任务ID: {task_id} - 学段: {stage}, 学科: {subject}, 教材版本: {version}, 年级: {grade}\n")
        
        driver.quit()
        logging.info(f"任务ID: {task_id} - 爬取完成")
        return extracted_data
    except (WebDriverException, TimeoutException) as e:
        logging.error(f"任务ID: {task_id} - 浏览器操作时出错: {e}")
    except Exception as e:
        logging.error(f"任务ID: {task_id} - 其他错误: {e}")
    return []

def check_output():
    """
    检查output.txt文件中是否存在"信息不足"
    :return: 如果存在"信息不足"则返回True，否则返回False
    """
    try:
        with open('output.txt', 'r', encoding='utf-8') as file:
            return "信息不足" in file.read()
    except FileNotFoundError:
        logging.warning("output.txt 文件不存在")
        return False

def main():
    """
    主函数，控制整个爬虫的执行流程
    """
    task_id = 1
    while True:
        # 步骤1：分析网站
        analysis_result = analyze_website(task_id, TARGET_URL)
        
        # 步骤2：爬取数据
        extracted_data = scrape_data(task_id, TARGET_URL)
        
        # 步骤3和4：检查结果并决定是否继续
        if not extracted_data or check_output():
            reanalysis_result = callAI(f"任务ID: {task_id} - 重新分析爬取结果，提供改进建议")
            logging.info(f"任务ID: {task_id} - 重新分析结果: {reanalysis_result}")
            
            print("是否继续爬取？")
            if input("输入'y'继续，或其他键退出: ").strip().lower() != 'y':
                logging.info(f"任务ID: {task_id} - 用户选择停止爬取")
                print("爬取中止。")
                break
            task_id += 1
        else:
            print("爬取完成，结果已保存到output.txt")
            break

if __name__ == "__main__":
    main()
