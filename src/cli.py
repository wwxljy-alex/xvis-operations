#!/usr/bin/env python3
"""
AutoJob CLI 命令行界面
"""

import sys
import argparse
from core.config import Config
from core.database import Database
from core.browser import BrowserManager
from core.logger import setup_logger
from platforms.boss import BossPlatform
from platforms.lagou import LagouPlatform
from ai.cover_letter import CoverLetterGenerator


class AutoJobCLI:
    """AutoJob命令行界面"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = Config(config_path)
        self.logger = setup_logger('INFO')
        self.db = Database(self.config.get('database.path', 'data/autojob.db'))
        self.browser = None
        self.platforms = {}
    
    def init(self):
        """初始化"""
        self.logger.info("初始化AutoJob...")
        
        # 初始化浏览器
        try:
            self.browser = BrowserManager(self.config)
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {e}")
            return False
        
        # 初始化平台
        if self.config.get('platforms.boss.enabled'):
            self.platforms['boss'] = BossPlatform(self.browser, self.config)
        
        if self.config.get('platforms.lagou.enabled'):
            self.platforms['lagou'] = LagouPlatform(self.browser, self.config)
        
        self.logger.info(f"已加载平台: {list(self.platforms.keys())}")
        return True
    
    def search(self, keywords, location="", platform=None):
        """搜索职位"""
        results = []
        
        target_platforms = [platform] if platform else self.platforms.keys()
        
        for p in target_platforms:
            if p not in self.platforms:
                self.logger.warning(f"平台 {p} 未启用")
                continue
            
            try:
                self.logger.info(f"搜索平台: {p}")
                jobs = self.platforms[p].search_jobs(keywords, location)
                results.extend(jobs)
                self.logger.info(f"{p} 找到 {len(jobs)} 个职位")
            except Exception as e:
                self.logger.error(f"{p} 搜索失败: {e}")
        
        # 去重
        results = self._deduplicate(results)
        
        # 保存
        for job in results:
            self.db.save_job(job)
        
        return results
    
    def apply(self, job_id, platform, resume_path=None, cover_letter=None):
        """投递简历"""
        if platform not in self.platforms:
            self.logger.error(f"未知平台: {platform}")
            return False
        
        # 生成Cover Letter
        if not cover_letter:
            llm = CoverLetterGenerator(self.config)
            job = self.db.get_job(platform, job_id)
            if job:
                cover_letter = llm.generate(
                    job_description=job.get('description', ''),
                    job_requirements=job.get('requirements', [])
                )
        
        # 投递
        try:
            result = self.platforms[platform].apply(
                job_id, resume_path, cover_letter
            )
            
            # 记录
            self.db.save_application({
                'job_id': job_id,
                'platform': platform,
                'status': 'success' if result else 'failed',
                'cover_letter': cover_letter
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"投递失败: {e}")
            return False
    
    def list_jobs(self, platform=None, status=None, limit=50):
        """列出职位/投递记录"""
        if status:
            return self.db.get_applications(platform, status)
        else:
            return self.db.get_jobs(platform, limit=limit)
    
    def stats(self):
        """统计信息"""
        apps = self.db.get_applications()
        
        stats = {
            'total': len(apps),
            'success': len([a for a in apps if a.get('status') == 'success']),
            'failed': len([a for a in apps if a.get('status') == 'failed']),
            'pending': len([a for a in apps if a.get('status') == 'pending'])
        }
        
        # 按平台统计
        platform_stats = {}
        for app in apps:
            p = app.get('platform', 'unknown')
            if p not in platform_stats:
                platform_stats[p] = {'total': 0, 'success': 0}
            platform_stats[p]['total'] += 1
            if app.get('status') == 'success':
                platform_stats[p]['success'] += 1
        
        return stats, platform_stats
    
    def _deduplicate(self, jobs):
        """去重"""
        seen = set()
        unique = []
        
        for job in jobs:
            key = f"{job.get('platform')}_{job.get('job_id')}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        
        return unique
    
    def close(self):
        """关闭"""
        if self.browser:
            self.browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="AutoJob - AI求职投递助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m cli search Web3 香港
  python -m cli search 产品经理 深圳 --platform boss
  python -m cli apply 123456 boss --resume resume.pdf
  python -m cli list --status pending
  python -m cli stats
        """
    )
    
    parser.add_argument('--config', default='config/config.yaml', help='配置文件')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # search命令
    search_parser = subparsers.add_parser('search', help='搜索职位')
    search_parser.add_argument('keywords', nargs='+', help='搜索关键词')
    search_parser.add_argument('--location', '-l', default='', help='工作地点')
    search_parser.add_argument('--platform', '-p', help='指定平台')
    
    # apply命令
    apply_parser = subparsers.add_parser('apply', help='投递简历')
    apply_parser.add_argument('job_id', help='职位ID')
    apply_parser.add_argument('platform', help='平台')
    apply_parser.add_argument('--resume', '-r', help='简历路径')
    apply_parser.add_argument('--cover-letter', '-c', help='求职信内容')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出职位/投递')
    list_parser.add_argument('--platform', '-p', help='平台过滤')
    list_parser.add_argument('--status', '-s', help='状态过滤')
    list_parser.add_argument('--limit', '-n', type=int, default=50, help='数量限制')
    
    # stats命令
    subparsers.add_parser('stats', help='统计信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建CLI
    cli = AutoJobCLI(args.config)
    
    if not cli.init():
        print("初始化失败")
        return
    
    try:
        if args.command == 'search':
            jobs = cli.search(args.keywords, args.location, args.platform)
            print(f"\n找到 {len(jobs)} 个职位:")
            for job in jobs[:20]:
                print(f"  [{job.get('platform')}] {job.get('title')} @ {job.get('company')} - {job.get('location')} - {job.get('salary')}")
        
        elif args.command == 'apply':
            result = cli.apply(
                args.job_id,
                args.platform,
                args.resume,
                args.cover_letter
            )
            print(f"\n投递{'成功' if result else '失败'}")
        
        elif args.command == 'list':
            items = cli.list_jobs(args.platform, args.status, args.limit)
            print(f"\n共 {len(items)} 条记录:")
            for item in items:
                print(f"  [{item.get('platform')}] {item.get('title') or item.get('job_id')} - {item.get('status')}")
        
        elif args.command == 'stats':
            stats, platform_stats = cli.stats()
            print("\n投递统计:")
            print(f"  总计: {stats['total']}")
            print(f"  成功: {stats['success']}")
            print(f"  失败: {stats['failed']}")
            print(f"  待处理: {stats['pending']}")
            
            print("\n按平台统计:")
            for p, s in platform_stats.items():
                print(f"  {p}: {s['success']}/{s['total']}")
    
    finally:
        cli.close()


if __name__ == '__main__':
    main()
