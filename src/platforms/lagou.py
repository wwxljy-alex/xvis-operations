#!/usr/bin/env python3
"""
拉勾平台适配器
"""

import time
from typing import Dict, List
from .base import BasePlatform


class LagouPlatform(BasePlatform):
    """拉勾招聘平台"""
    
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.platform_name = "lagou"
        self.login_url = config.get('platforms.lagou.login_url', 'https://www.lagou.com/')
        self.search_url = config.get('platforms.lagou.search_url', 'https://www.lagou.com/jobs/list_')
    
    def search_jobs(self, keywords: List[str], location: str = "", **kwargs) -> List[Dict]:
        """搜索职位"""
        jobs = []
        
        try:
            keyword_str = ','.join(keywords)
            url = f"{self.search_url}{keyword_str}"
            if location:
                url += f"?city={location}"
            
            self.page.goto(url)
            time.sleep(3)
            
            # 等待加载
            self.page.wait_for_selector('.job_list', timeout=10000)
            
            # 解析职位
            job_cards = self.page.locator('.job_list .job Li').all()
            
            for card in job_cards:
                try:
                    job = {
                        'platform': self.platform_name,
                        'job_id': card.locator('.position').get_attribute('data-id'),
                        'title': card.locator('.position .name').text_content().strip(),
                        'company': card.locator('.company .name').text_content().strip(),
                        'salary': card.locator('.salary').text_content().strip(),
                        'location': card.locator('.city').text_content().strip(),
                    }
                    jobs.append(job)
                except Exception:
                    pass
            
        except Exception as e:
            print(f"拉勾搜索失败: {e}")
        
        return jobs
    
    def get_job_detail(self, job_id: str) -> Dict:
        """获取职位详情"""
        return {}
    
    def apply(self, job_id: str, resume_path: str = None, cover_letter: str = None) -> bool:
        """投递简历"""
        return False
    
    def login(self, username: str, password: str) -> bool:
        """登录"""
        return False
    
    def is_logged_in(self) -> bool:
        """检查登录"""
        return False
