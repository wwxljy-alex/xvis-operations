#!/usr/bin/env python3
"""
浏览器管理模块
基于Playwright实现浏览器自动化
"""

import time
import random
from typing import Optional, Dict


class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self, config):
        self.config = config
        self.browser = None
        self.context = None
        self.page = None
        self._init_browser()
    
    def _init_browser(self):
        """初始化浏览器"""
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            
            # 选择浏览器
            browser_type = playwright.chromium
            
            # 启动配置
            launch_options = {
                'headless': self.config.get('browser.headless', False),
            }
            
            # 如果需要代理
            if self.config.get('proxy.enabled', False):
                proxy = self.config.get('proxy.pool', [{}])[0]
                if proxy:
                    launch_options['proxy'] = {
                        'server': f"http://{proxy.get('host')}:{proxy.get('port')}",
                        'username': proxy.get('username'),
                        'password': proxy.get('password')
                    }
            
            self.browser = browser_type.launch(**launch_options)
            
            # 创建上下文
            self.context = self.browser.new_context(
                user_agent=self.config.get('browser.user_agent'),
                viewport={'width': 1920, 'height': 1080}
            )
            
            # 设置默认超时
            self.context.set_default_timeout(
                self.config.get('browser.timeout', 30000)
            )
            
            # 创建页面
            self.page = self.context.new_page()
            
        except ImportError:
            print("警告: Playwright未安装，将使用selenium作为备选")
            self._init_selenium()
        except Exception as e:
            print(f"浏览器初始化失败: {e}")
            self._init_selenium()
    
    def _init_selenium(self):
        """备选：使用Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            if self.config.get('browser.headless', False):
                options.add_argument('--headless')
            
            self.browser = webdriver.Chrome(options=options)
            self.page = self.browser
        
        except ImportError:
            print("错误: 请安装playwright或selenium")
            raise
    
    def get_page(self):
        """获取页面对象"""
        return self.page
    
    def navigate(self, url: str, wait_until: str = "load"):
        """导航到URL"""
        self.page.goto(url, wait_until=wait_until)
        self._random_delay()
    
    def click(self, selector: str, timeout: int = 30000):
        """点击元素"""
        self.page.click(selector, timeout=timeout)
        self._random_delay()
    
    def fill(self, selector: str, value: str):
        """填写表单"""
        self.page.fill(selector, value)
        time.sleep(0.2)
    
    def select(self, selector: str, value: str):
        """选择选项"""
        self.page.select_option(selector, value)
    
    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """等待元素出现"""
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def wait_for_load(self, state: str = "load", timeout: int = 30000):
        """等待加载完成"""
        self.page.wait_for_load_state(state, timeout=timeout)
    
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        return self.page.locator(selector).text_content()
    
    def get_attribute(self, selector: str, attr: str) -> str:
        """获取元素属性"""
        return self.page.get_attribute(selector, attr)
    
    def get_page_html(self) -> str:
        """获取页面HTML"""
        return self.page.content()
    
    def screenshot(self, path: str = None) -> bytes:
        """截图"""
        return self.page.screenshot(path=path)
    
    def _random_delay(self):
        """随机延迟"""
        delay_min = self.config.get('application.delay_min', 3000) / 1000
        delay_max = self.config.get('application.delay_max', 8000) / 1000
        time.sleep(random.uniform(delay_min / 1000, delay_max / 1000))
    
    def wait_for_navigation(self, timeout: int = 30000):
        """等待导航完成"""
        self.page.wait_for_load_state('networkidle', timeout=timeout)
    
    def execute_script(self, script: str):
        """执行JavaScript"""
        return self.page.evaluate(script)
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
    
    def new_page(self):
        """创建新页面"""
        return self.context.new_page()
    
    def get_cookies(self) -> list:
        """获取Cookies"""
        return self.context.cookies()
    
    def set_cookies(self, cookies: list):
        """设置Cookies"""
        self.context.add_cookies(cookies)
    
    def delete_cookies(self):
        """删除Cookies"""
        self.context.clear_cookies()
