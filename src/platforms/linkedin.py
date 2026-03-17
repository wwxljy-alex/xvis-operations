#!/usr/bin/env python3
"""
LinkedIn平台适配器
"""

from typing import Dict, List
from .base import BasePlatform


class LinkedInPlatform(BasePlatform):
    """LinkedIn平台"""
    
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.platform_name = "linkedin"
        self.login_url = "https://www.linkedin.com/"
        self.search_url = "https://www.linkedin.com/jobs/"
    
    def search_jobs(self, keywords: List[str], location: str = "", **kwargs) -> List[Dict]:
        jobs = []
        # LinkedIn反爬较强，需要特殊处理
        return jobs
    
    def get_job_detail(self, job_id: str) -> Dict:
        return {}
    
    def apply(self, job_id: str, resume_path: str = None, cover_letter: str = None) -> bool:
        return False
    
    def login(self, username: str, password: str) -> bool:
        return False
    
    def is_logged_in(self) -> bool:
        return False
