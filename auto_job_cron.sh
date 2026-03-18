#!/bin/bash
# AutoJob 自动化脚本
# 用于Cron定时任务

cd /home/ubuntu/clawd/auto_job

# 设置Python路径
export PYTHONPATH=/home/ubuntu/clawd/auto_job/src:$PYTHONPATH

# 日志文件
LOG_FILE="/home/ubuntu/clawd/auto_job/logs/autojob_cron.log"

echo "========== $(date) ==========" >> $LOG_FILE

# 导入Python模块并执行
python3 << 'EOF' >> $LOG_FILE 2>&1
import sys
sys.path.insert(0, '/home/ubuntu/clawd/auto_job/src')

from core.config import Config
from core.database import Database
from core.browser import BrowserManager
from platforms.boss_enhanced import BossPlatformEnhanced
from ai.cover_letter import CoverLetterGenerator
import time

def run_autojob():
    try:
        print("启动AutoJob...")
        
        # 初始化
        config = Config('/home/ubuntu/clawd/auto_job/config/config.yaml')
        db = Database('/home/ubuntu/clawd/auto_job/data/autojob.db')
        browser = BrowserManager(config)
        boss = BossPlatformEnhanced(browser, config)
        
        # 获取搜索关键词
        keywords = config.get('user.keywords', ['Web3', '产品经理'])
        locations = config.get('user.locations', ['深圳', '香港'])
        
        print(f"搜索关键词: {keywords}")
        print(f"搜索地点: {locations}")
        
        # 搜索职位
        all_jobs = []
        for kw in keywords:
            for loc in locations:
                print(f"搜索: {kw} {loc}")
                jobs = boss.search_jobs([kw], loc)
                all_jobs.extend(jobs)
                time.sleep(3)
        
        # 去重
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job.get('platform')}_{job.get('job_id')}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        print(f"找到 {len(unique_jobs)} 个新职位")
        
        # 保存到数据库
        for job in unique_jobs:
            db.save_job(job)
        
        # 检查是否需要投递
        # 这里可以实现自动投递逻辑
        
        browser.close()
        
        print("完成!")
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

run_autojob()
EOF

echo "========== 完成 ==========" >> $LOG_FILE
