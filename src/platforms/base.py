#!/usr/bin/env python3
"""
平台基类
定义所有招聘平台适配器的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import time
import random


class BasePlatform(ABC):
    """招聘平台基类"""
    
    def __init__(self, browser, config):
        self.browser = browser
        self.config = config
        self.page = browser.get_page()
        self.platform_name = "base"
        self.login_url = ""
        self.search_url = ""
    
    def search_jobs(self, keywords: List[str], location: str = "", 
                    **kwargs) -> List[Dict]:
        """
        搜索职位
        返回职位列表
        """
        raise NotImplementedError
    
    def get_job_detail(self, job_id: str) -> Dict:
        """
        获取职位详情
        """
        raise NotImplementedError
    
    def apply(self, job_id: str, resume_path: str = None, 
              cover_letter: str = None) -> bool:
        """
        投递简历
        """
        raise NotImplementedError
    
    def login(self, username: str, password: str) -> bool:
        """
        登录
        """
        raise NotImplementedError
    
    def is_logged_in(self) -> bool:
        """
        检查是否已登录
        """
        raise NotImplementedError
    
    def _navigate_to_search(self):
        """导航到搜索页"""
        self.page.goto(self.search_url)
        self._wait_for_load()
    
    def _wait_for_load(self, timeout: int = 30000):
        """等待页面加载"""
        self.page.wait_for_load_state('networkidle', timeout=timeout)
    
    def _random_delay(self):
        """随机延迟"""
        delay_min = self.config.get('application.delay_min', 3000)
        delay_max = self.config.get('application.delay_max', 8000)
        time.sleep(random.uniform(delay_min / 1000, delay_max / 1000))
    
    def _parse_job_card(self, element) -> Dict:
        """
        解析职位卡片
        由子类实现具体解析逻辑
        """
        raise NotImplementedError
    
    def _handle_captcha(self) -> bool:
        """
        处理验证码
        返回是否成功
        """
        # 默认实现：等待用户处理
        print("请手动处理验证码...")
        time.sleep(30)
        return True
    
    def _safe_click(self, selector: str, retries: int = 3) -> bool:
        """安全点击"""
        for i in range(retries):
            try:
                self.page.click(selector)
                return True
            except Exception as e:
                if i < retries - 1:
                    time.sleep(1)
                else:
                    raise e
        return False
    
    def _safe_fill(self, selector: str, value: str) -> bool:
        """安全填写"""
        try:
            self.page.fill(selector, value)
            return True
        except Exception:
            return False
    
    def _extract_text(self, selector: str, default: str = "") -> str:
        """安全提取文本"""
        try:
            return self.page.locator(selector).text_content().strip()
        except Exception:
            return default
    
    def close(self):
        """关闭"""
        pass
