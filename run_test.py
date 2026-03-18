#!/usr/bin/env python3
"""
AutoJob - 一键启动脚本
"""

import os
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import Config
from core.database import Database
from core.logger import setup_logger
from core.browser import BrowserManager
from platforms.boss_enhanced import BossPlatformEnhanced
from ai.cover_letter import CoverLetterGenerator
from core.notification import Notifier
import time


def main():
    print("=" * 50)
    print("🤖 AutoJob - AI求职投递助手")
    print("=" * 50)
    
    # 初始化
    config = Config('config/config.yaml')
    logger = setup_logger('INFO', 'logs/autojob.log')
    logger.info("启动AutoJob...")
    
    # 初始化数据库
    db = Database(config.get('database.path', 'data/autojob.db'))
    logger.info("数据库初始化完成")
    
    # 初始化浏览器
    logger.info("初始化浏览器...")
    browser = BrowserManager(config)
    logger.info("浏览器初始化完成")
    
    # 初始化平台
    logger.info("初始化平台...")
    boss = BossPlatformEnhanced(browser, config)
    logger.info("平台初始化完成")
    
    # 测试搜索
    print("\n🔍 测试搜索职位...")
    jobs = boss.search_jobs(["Web3", "产品经理"], "深圳")
    
    print(f"\n✅ 找到 {len(jobs)} 个职位:")
    for i, job in enumerate(jobs[:5]):
        print(f"  {i+1}. {job.get('title')} @ {job.get('company')} - {job.get('salary')}")
    
    # 保存到数据库
    for job in jobs:
        db.save_job(job)
    
    # 测试LLM
    print("\n📝 测试Cover Letter生成...")
    llm = CoverLetterGenerator(config)
    
    if jobs:
        sample_job = jobs[0]
        cover_letter = llm.generate(
            job_description=sample_job.get('description', ''),
            job_requirements=sample_job.get('requirements', [])
        )
        print(f"✅ Cover Letter生成成功 ({(len(cover_letter))}字符)")
    
    # 统计
    apps = db.get_applications()
    print(f"\n📊 投递统计: {len(apps)} 条记录")
    
    # 关闭
    browser.close()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
