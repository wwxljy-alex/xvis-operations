#!/usr/bin/env python3
"""
AutoJob - AI求职投递助手
主程序入口
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import Config
from core.database import Database
from core.browser import BrowserManager
from core.logger import setup_logger
from platforms.boss import BossPlatform
from platforms.lagou import LagouPlatform
from platforms.liepin import LiepinPlatform
from platforms.jobsdb import JobsDBPlatform
from platforms.linkedin import LinkedInPlatform
from ai.cover_letter import CoverLetterGenerator


class AutoJob:
    """AutoJob主类"""
    
    def __init__(self, config_path="config/config.yaml"):
        # 初始化配置
        self.config = Config(config_path)
        
        # 初始化日志
        self.logger = setup_logger(
            self.config.get('logging.level', 'INFO'),
            self.config.get('logging.file', 'logs/autojob.log')
        )
        
        # 初始化数据库
        self.db = Database(self.config.get('database.path', 'data/autojob.db'))
        
        # 初始化浏览器
        self.browser = BrowserManager(self.config)
        
        # 初始化LLM
        self.llm = CoverLetterGenerator(self.config)
        
        # 初始化平台
        self.platforms = {}
        self._init_platforms()
        
        self.logger.info("AutoJob 初始化完成")
    
    def _init_platforms(self):
        """初始化平台"""
        platform_configs = self.config.get('platforms', {})
        
        if platform_configs.get('boss', {}).get('enabled', False):
            self.platforms['boss'] = BossPlatform(self.browser, self.config)
            
        if platform_configs.get('lagou', {}).get('enabled', False):
            self.platforms['lagou'] = LagouPlatform(self.browser, self.config)
            
        if platform_configs.get('liepin', {}).get('enabled', False):
            self.platforms['liepin'] = LiepinPlatform(self.browser, self.config)
            
        if platform_configs.get('jobsdb', {}).get('enabled', False):
            self.platforms['jobsdb'] = JobsDBPlatform(self.browser, self.config)
            
        if platform_configs.get('linkedin', {}).get('enabled', False):
            self.platforms['linkedin'] = LinkedInPlatform(self.browser, self.config)
        
        self.logger.info(f"已加载平台: {list(self.platforms.keys())}")
    
    def search_jobs(self, keywords: list, location: str = "", **kwargs):
        """搜索职位"""
        results = []
        
        for platform_name, platform in self.platforms.items():
            try:
                self.logger.info(f"搜索平台: {platform_name}")
                jobs = platform.search_jobs(keywords, location, **kwargs)
                results.extend(jobs)
                self.logger.info(f"{platform_name} 找到 {len(jobs)} 个职位")
            except Exception as e:
                self.logger.error(f"{platform_name} 搜索失败: {e}")
        
        # 去重
        results = self._deduplicate_jobs(results)
        
        # 保存到数据库
        for job in results:
            self.db.save_job(job)
        
        return results
    
    def _deduplicate_jobs(self, jobs: list) -> list:
        """去重"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = f"{job.get('platform')}_{job.get('job_id')}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def apply_job(self, job: dict, resume_path: str = None) -> bool:
        """投递简历"""
        platform = job.get('platform')
        
        if platform not in self.platforms:
            self.logger.error(f"未知平台: {platform}")
            return False
        
        try:
            # 生成Cover Letter
            cover_letter = self.llm.generate(
                job_description=job.get('description', ''),
                job_requirements=job.get('requirements', [])
            )
            
            # 投递
            result = self.platforms[platform].apply(
                job_id=job.get('job_id'),
                resume_path=resume_path or self.config.get('user.resume_path'),
                cover_letter=cover_letter
            )
            
            # 记录结果
            self.db.save_application({
                'job_id': job.get('job_id'),
                'platform': platform,
                'status': 'success' if result else 'failed',
                'applied_at': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"投递失败: {e}")
            return False
    
    def apply_batch(self, jobs: list, resume_path: str = None) -> dict:
        """批量投递"""
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for i, job in enumerate(jobs):
            self.logger.info(f"投递进度: {i+1}/{len(jobs)}")
            
            # 检查是否已投递
            if self.db.is_applied(job.get('job_id')):
                results['skipped'] += 1
                continue
            
            # 投递
            if self.apply_job(job, resume_path):
                results['success'] += 1
            else:
                results['failed'] += 1
            
            # 延迟
            delay = self.config.get('application.delay_min', 3000) / 1000
            import time
            time.sleep(delay)
        
        return results
    
    def get_applications(self) -> list:
        """获取投递记录"""
        return self.db.get_applications()
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        apps = self.get_applications()
        
        return {
            'total': len(apps),
            'success': len([a for a in apps if a.get('status') == 'success']),
            'failed': len([a for a in apps if a.get('status') == 'failed']),
            'pending': len([a for a in apps if a.get('status') == 'pending'])
        }
    
    def close(self):
        """关闭"""
        self.browser.close()
        self.logger.info("AutoJob 已关闭")


def main():
    parser = argparse.ArgumentParser(description="AutoJob - AI求职投递助手")
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--search', nargs='+', help='搜索关键词')
    parser.add_argument('--location', default='', help='工作地点')
    parser.add_argument('--apply', action='store_true', help='自动投递')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    
    args = parser.parse_args()
    
    # 创建AutoJob实例
    autojob = AutoJob(args.config)
    
    try:
        if args.search:
            # 搜索职位
            jobs = autojob.search_jobs(args.search, args.location)
            print(f"\n找到 {len(jobs)} 个职位:")
            for job in jobs[:10]:
                print(f"  - {job.get('title')} @ {job.get('company')} ({job.get('platform')})")
            
            # 自动投递
            if args.apply:
                results = autojob.apply_batch(jobs)
                print(f"\n投递结果: 成功 {results['success']}, 失败 {results['failed']}, 跳过 {results['skipped']}")
        
        elif args.stats:
            # 显示统计
            stats = autojob.get_stats()
            print(f"\n投递统计:")
            print(f"  总计: {stats['total']}")
            print(f"  成功: {stats['success']}")
            print(f"  失败: {stats['failed']}")
            print(f"  待处理: {stats['pending']}")
        
        else:
            parser.print_help()
    
    finally:
        autojob.close()


if __name__ == '__main__':
    main()
