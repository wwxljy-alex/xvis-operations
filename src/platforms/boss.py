#!/usr/bin/env python3
"""
BOSS直聘平台适配器
"""

import time
import json
from typing import Dict, List
from .base import BasePlatform


class BossPlatform(BasePlatform):
    """BOSS直聘平台"""
    
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.platform_name = "boss"
        self.login_url = config.get('platforms.boss.login_url', 'https://www.zhipin.com/')
        self.search_url = config.get('platforms.boss.search_url', 'https://www.zhipin.com/web/geek/job')
    
    def search_jobs(self, keywords: List[str], location: str = "", 
                    **kwargs) -> List[Dict]:
        """搜索职位"""
        jobs = []
        
        try:
            # 构建搜索URL
            keyword_str = ','.join(keywords)
            url = f"{self.search_url}?query={keyword_str}"
            if location:
                url += f"&city={location}"
            
            # 导航到搜索页
            self.page.goto(url)
            time.sleep(3)
            
            # 等待结果加载
            self.page.wait_for_selector('.job-list', timeout=10000)
            
            # 滚动加载更多
            self._scroll_load()
            
            # 解析职位列表
            job_cards = self.page.locator('.job-card').all()
            
            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        job['platform'] = self.platform_name
                        jobs.append(job)
                except Exception as e:
                    print(f"解析职位失败: {e}")
            
        except Exception as e:
            print(f"BOSS搜索失败: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """解析职位卡片"""
        try:
            # 提取基本信息
            title = card.locator('.job-title').text_content().strip()
            company = card.locator('.company-name').text_content().strip()
            salary = card.locator('.salary').text_content().strip()
            location = card.locator('.job-area').text_content().strip()
            
            # 提取详情链接
            link = card.locator('a').get_attribute('href')
            job_id = link.split('/')[-1].replace('.html', '') if link else ''
            
            # 提取描述（可能需要访问详情页）
            description = ""
            requirements = []
            
            # 提取标签
            tags = []
            tag_elements = card.locator('.tag').all()
            for tag in tag_elements:
                tags.append(tag.text_content().strip())
            
            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'tags': tags,
                'description': description,
                'requirements': requirements,
                'url': link
            }
            
        except Exception as e:
            print(f"解析卡片失败: {e}")
            return None
    
    def _scroll_load(self, max_scrolls: int = 3):
        """滚动加载更多"""
        for i in range(max_scrolls):
            self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)
    
    def get_job_detail(self, job_id: str) -> Dict:
        """获取职位详情"""
        try:
            url = f"https://www.zhipin.com/job_detail/{job_id}.html"
            self.page.goto(url)
            time.sleep(2)
            
            # 提取详情
            title = self.page.locator('.job-title').text_content().strip()
            company = self.page.locator('.company-name').text_content().strip()
            salary = self.page.locator('.salary').text_content().strip()
            
            # 提取职位描述
            desc_elements = self.page.locator('.job-desc').all()
            description = '\n'.join([e.text_content() for e in desc_elements])
            
            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'salary': salary,
                'description': description
            }
            
        except Exception as e:
            print(f"获取详情失败: {e}")
            return {}
    
    def apply(self, job_id: str, resume_path: str = None, 
              cover_letter: str = None) -> bool:
        """投递简历"""
        try:
            # 访问职位详情页
            url = f"https://www.zhipin.com/job_detail/{job_id}.html"
            self.page.goto(url)
            time.sleep(2)
            
            # 点击投递按钮
            deliver_btn = self.page.locator('.btn-deliver')
            if deliver_btn.count() > 0:
                deliver_btn.click()
                time.sleep(2)
                
                # 处理投递表单
                # 这里需要根据实际情况填写
                
                return True
            
            return False
            
        except Exception as e:
            print(f"投递失败: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """登录"""
        try:
            self.page.goto(self.login_url)
            time.sleep(2)
            
            # 点击登录按钮
            self.page.click('.login-btn')
            time.sleep(1)
            
            # 选择密码登录
            self.page.click('.password-login')
            time.sleep(1)
            
            # 填写账号密码
            self.page.fill('.username-input', username)
            self.page.fill('.password-input', password)
            
            # 点击登录
            self.page.click('.btn-login')
            time.sleep(3)
            
            return self.is_logged_in()
            
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查是否有用户头像
            avatar = self.page.locator('.user-avatar')
            return avatar.count() > 0
        except Exception:
            return False
