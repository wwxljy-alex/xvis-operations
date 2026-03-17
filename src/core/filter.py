#!/usr/bin/env python3
"""
职位筛选与匹配模块
"""

import re
from typing import Dict, List, Optional


class JobMatcher:
    """职位匹配器"""
    
    def __init__(self, user_preferences: Dict):
        self.preferences = user_preferences
        self.keywords_include = user_preferences.get('keywords_include', [])
        self.keywords_exclude = user_preferences.get('keywords_exclude', [])
        self.locations = user_preferences.get('locations', [])
        self.salary_min = user_preferences.get('salary_min', 0)
        self.salary_max = user_preferences.get('salary_max', 0)
        self.experience_min = user_preferences.get('experience_min', 0)
    
    def match(self, job: Dict) -> Dict:
        """
        匹配职位
        返回职位及匹配分数
        """
        score = 0
        reasons = []
        
        # 关键词匹配
        if self.keywords_include:
            title = job.get('title', '').lower()
            desc = job.get('description', '').lower()
            
            keyword_matches = 0
            for kw in self.keywords_include:
                if kw.lower() in title or kw.lower() in desc:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                score += keyword_matches * 10
                reasons.append(f"关键词匹配: {keyword_matches}/{len(self.keywords_include)}")
        
        # 排除关键词
        for kw in self.keywords_exclude:
            title = job.get('title', '').lower()
            if kw.lower() in title:
                return {'match': False, 'job': job, 'score': 0, 'reasons': ['排除关键词']}
        
        # 地点匹配
        if self.locations:
            location = job.get('location', '').lower()
            for loc in self.locations:
                if loc.lower() in location:
                    score += 15
                    reasons.append(f"地点匹配: {loc}")
                    break
        else:
            score += 5  # 无地点限制
            reasons.append("地点不限")
        
        # 薪资匹配
        salary = self._parse_salary(job.get('salary', ''))
        if salary:
            if self.salary_min and salary < self.salary_min:
                score -= 10
                reasons.append(f"薪资低于预期: {salary}K")
            elif self.salary_max and salary > self.salary_max:
                score -= 10
                reasons.append(f"薪资高于上限: {salary}K")
            else:
                score += 10
                reasons.append(f"薪资符合: {salary}K")
        
        return {
            'match': score > 0,
            'job': job,
            'score': score,
            'reasons': reasons
        }
    
    def filter(self, jobs: List[Dict]) -> List[Dict]:
        """批量过滤职位"""
        results = []
        
        for job in jobs:
            result = self.match(job)
            if result['match']:
                results.append(result)
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _parse_salary(self, salary_str: str) -> Optional[int]:
        """解析薪资字符串，返回月薪（K）"""
        if not salary_str:
            return None
        
        # 匹配如 "20K-40K", "20-40K", "2万-4万" 等
        patterns = [
            r'(\d+)[Kk]-(\d+)[Kk]',  # 20K-40K
            r'(\d+)[Kk]',  # 20K
            r'(\d+)-(\d+)万',  # 2-4万
            r'(\d+)万',  # 2万
            r'(\d+)-(\d+)k',  # 20k-40k
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_str)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    # 范围
                    return (int(groups[0]) + int(groups[1])) // 2
                else:
                    # 单一值
                    val = int(groups[0])
                    if '万' in salary_str:
                        return val * 10  # 转换为K
                    return val
        
        return None


class JobFilter:
    """职位过滤器"""
    
    @staticmethod
    def filter_by_keywords(jobs: List[Dict], include: List[str], exclude: List[str] = None) -> List[Dict]:
        """按关键词过滤"""
        exclude = exclude or []
        
        results = []
        for job in jobs:
            title = job.get('title', '').lower()
            desc = job.get('description', '').lower()
            
            # 必须包含至少一个关键词
            if include:
                if not any(kw.lower() in title or kw.lower() in desc for kw in include):
                    continue
            
            # 不能包含排除关键词
            if exclude:
                if any(kw.lower() in title for kw in exclude):
                    continue
            
            results.append(job)
        
        return results
    
    @staticmethod
    def filter_by_location(jobs: List[Dict], locations: List[str]) -> List[Dict]:
        """按地点过滤"""
        if not locations:
            return jobs
        
        results = []
        for job in jobs:
            location = job.get('location', '').lower()
            if any(loc.lower() in location for loc in locations):
                results.append(job)
        
        return results
    
    @staticmethod
    def filter_by_salary(jobs: List[Dict], min_salary: int = 0, max_salary: int = 0) -> List[Dict]:
        """按薪资过滤"""
        if min_salary == 0 and max_salary == 0:
            return jobs
        
        matcher = JobMatcher({'salary_min': min_salary, 'salary_max': max_salary})
        
        results = []
        for job in jobs:
            result = matcher.match(job)
            if result['match']:
                results.append(job)
        
        return results
    
    @staticmethod
    def filter_by_company(jobs: List[Dict], include: List[str] = None, exclude: List[str] = None) -> List[Dict]:
        """按公司过滤"""
        include = include or []
        exclude = exclude or []
        
        results = []
        for job in jobs:
            company = job.get('company', '').lower()
            
            # 排除公司
            if exclude and any(ex.lower() in company for ex in exclude):
                continue
            
            # 包含公司（可选）
            if include:
                if not any(inc.lower() in company for inc in include):
                    continue
            
            results.append(job)
        
        return results
    
    @staticmethod
    def deduplicate(jobs: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        results = []
        
        for job in jobs:
            key = f"{job.get('platform')}_{job.get('job_id')}"
            if key not in seen:
                seen.add(key)
                results.append(job)
        
        return results
