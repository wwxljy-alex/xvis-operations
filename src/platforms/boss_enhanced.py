#!/usr/bin/env python3
"""
BOSS直聘平台适配器 - 增强版
"""

import time
import json
import random
from typing import Dict, List, Optional
from core.base import BasePlatform


class BossPlatformEnhanced(BasePlatform):
    """BOSS直聘平台增强版"""
    
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.platform_name = "boss"
        self.base_url = "https://www.zhipin.com"
        self.login_url = "https://www.zhipin.com/"
        self.search_url = "https://www.zhipin.com/web/geek/job"
    
    def search_jobs(self, keywords: List[str], location: str = "", 
                    salary: str = "", experience: str = "", **kwargs) -> List[Dict]:
        """搜索职位"""
        jobs = []
        
        try:
            # 构建搜索URL
            keyword_str = ','.join(keywords)
            url = f"{self.search_url}?query={keyword_str}&page=1"
            
            if location:
                # 转换为BOSS城市代码
                city_code = self._get_city_code(location)
                if city_code:
                    url += f"&city={city_code}"
            
            if salary:
                url += f"&salary={salary}"
            
            if experience:
                url += f"&exp={experience}"
            
            self.logger.info(f"搜索URL: {url}")
            
            # 导航
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # 处理验证码（如果有）
            if self._check_captcha():
                self._handle_captcha()
            
            # 滚动加载
            self._scroll_page(3)
            
            # 解析职位列表
            job_items = self.page.locator('.job-list .job-card').all()
            
            for item in job_items:
                try:
                    job = self._parse_job_item(item)
                    if job:
                        job['platform'] = self.platform_name
                        jobs.append(job)
                except Exception as e:
                    self.logger.debug(f"解析职位失败: {e}")
            
            self.logger.info(f"找到 {len(jobs)} 个职位")
            
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
        
        return jobs
    
    def _parse_job_item(self, item) -> Optional[Dict]:
        """解析职位项"""
        try:
            # 提取基本信息
            title_elem = item.locator('.job-title')
            title = title_elem.text_content().strip() if title_elem.count() else ''
            
            company_elem = item.locator('.company-name')
            company = company_elem.text_content().strip() if company_elem.count() else ''
            
            salary_elem = item.locator('.salary')
            salary = salary_elem.text_content().strip() if salary_elem.count() else ''
            
            location_elem = item.locator('.job-area')
            location = location_elem.text_content().strip() if location_elem.count() else ''
            
            # 提取链接和ID
            link_elem = item.locator('a')
            href = link_elem.get_attribute('href') if link_elem.count() else ''
            job_id = self._extract_job_id(href)
            
            # 提取标签
            tags = []
            tag_elems = item.locator('.tag').all()
            for tag in tag_elems[:3]:
                tags.append(tag.text_content().strip())
            
            # 提取公司标签
            company_tags = []
            ct_elems = item.locator('.company-tag-list .tag').all()
            for ct in ct_elems:
                company_tags.append(ct.text_content().strip())
            
            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'tags': tags,
                'company_tags': company_tags,
                'url': f"{self.base_url}{href}" if href else '',
                'description': '',
                'requirements': []
            }
            
        except Exception as e:
            self.logger.debug(f"解析失败: {e}")
            return None
    
    def _extract_job_id(self, url: str) -> str:
        """从URL提取职位ID"""
        if not url:
            return ''
        
        # URL格式: /job_detail/xxx.html
        parts = url.split('/')
        if parts:
            last = parts[-1]
            return last.replace('.html', '').replace('job_detail/', '')
        
        return ''
    
    def _get_city_code(self, city: str) -> str:
        """城市名转代码"""
        city_map = {
            '北京': '101010100',
            '上海': '101020100',
            '深圳': '101280600',
            '广州': '101280100',
            '杭州': '101210100',
            '成都': '101270100',
            '武汉': '101200100',
            '西安': '101110100',
            '南京': '101230100',
            '重庆': '101040100',
            '香港': '101080400',
        }
        
        return city_map.get(city, '')
    
    def _scroll_page(self, times: int = 3):
        """滚动页面"""
        for i in range(times):
            self.page.evaluate('window.scrollBy(0, 800)')
            time.sleep(random.uniform(1, 2))
    
    def _check_captcha(self) -> bool:
        """检查是否有验证码"""
        try:
            # 检查各种验证码元素
            captcha_selectors = [
                '.geetest_panel',
                '.geetest_slider',
                '.nc_wrapper',
                '#captcha',
                '.captcha-modal'
            ]
            
            for selector in captcha_selectors:
                if self.page.locator(selector).count() > 0:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def get_job_detail(self, job_id: str) -> Dict:
        """获取职位详情"""
        try:
            url = f"{self.base_url}/job_detail/{job_id}.html"
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # 提取详情
            title = self.page.locator('.job-title').text_content().strip()
            company = self.page.locator('.company-name').text_content().strip()
            salary = self.page.locator('.salary').text_content().strip()
            
            # 提取职位描述
            desc_parts = []
            desc_elems = self.page.locator('.job-desc p').all()
            for elem in desc_elems:
                text = elem.text_content().strip()
                if text:
                    desc_parts.append(text)
            
            description = '\n'.join(desc_parts)
            
            # 提取要求
            requirements = []
            req_elems = self.page.locator('.job-tags .tag').all()
            for elem in req_elems:
                requirements.append(elem.text_content().strip())
            
            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'salary': salary,
                'description': description,
                'requirements': requirements
            }
            
        except Exception as e:
            self.logger.error(f"获取详情失败: {e}")
            return {}
    
    def apply(self, job_id: str, resume_path: str = None, 
              cover_letter: str = None) -> bool:
        """投递简历"""
        try:
            # 访问职位详情页
            url = f"{self.base_url}/job_detail/{job_id}.html"
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # 查找投递按钮
            deliver_btn = self.page.locator('.btn-deliver')
            
            if deliver_btn.count() == 0:
                # 尝试其他按钮
                deliver_btn = self.page.locator('button:has-text("立即沟通")')
            
            if deliver_btn.count() > 0:
                deliver_btn.first.click()
                time.sleep(2)
                
                # 处理投递弹窗
                # 这里需要根据实际情况填写
                
                return True
            
            self.logger.warning("未找到投递按钮")
            return False
            
        except Exception as e:
            self.logger.error(f"投递失败: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """登录"""
        try:
            self.page.goto(self.login_url, wait_until='networkidle')
            time.sleep(2)
            
            # 点击登录按钮
            login_btn = self.page.locator('.login-btn')
            if login_btn.count() > 0:
                login_btn.click()
                time.sleep(1)
            
            # 选择密码登录
            pwd_login = self.page.locator('.password-login')
            if pwd_login.count() > 0:
                pwd_login.click()
                time.sleep(1)
            
            # 填写账号密码
            username_input = self.page.locator('input[name="username"]')
            password_input = self.page.locator('input[name="password"]')
            
            if username_input.count() > 0:
                username_input.fill(username)
            if password_input.count() > 0:
                password_input.fill(password)
            
            # 点击登录
            submit_btn = self.page.locator('.btn-login')
            if submit_btn.count() > 0:
                submit_btn.click()
                time.sleep(3)
            
            return self.is_logged_in()
            
        except Exception as e:
            self.logger.error(f"登录失败: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查用户头像
            avatar = self.page.locator('.user-avatar, .avatar, [class*="avatar"]')
            return avatar.count() > 0
        except Exception:
            return False
