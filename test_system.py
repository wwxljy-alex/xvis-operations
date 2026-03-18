#!/usr/bin/env python3
"""
AutoJob 简单测试
"""

import sys
import os

# 设置路径
BASE_DIR = '/home/ubuntu/clawd/auto_job'
sys.path.insert(0, f'{BASE_DIR}/src')

# 改变工作目录
os.chdir(BASE_DIR)

# 设置环境变量
os.environ['PYTHONPATH'] = f'{BASE_DIR}/src'

print("=" * 50)
print("🤖 AutoJob 测试")
print("=" * 50)

# 测试配置
print("\n1. 测试配置...")
from core.config import Config
config = Config(f'{BASE_DIR}/config/config.yaml')
print(f"   关键词: {config.get('user.keywords', [])}")
print(f"   地点: {config.get('user.locations', [])}")
print("   ✅ 配置OK")

# 测试数据库
print("\n2. 测试数据库...")
from core.database import Database
db = Database(f'{BASE_DIR}/data/autojob.db')
jobs = db.get_jobs()
apps = db.get_applications()
print(f"   职位数: {len(jobs)}")
print(f"   投递数: {len(apps)}")
print("   ✅ 数据库OK")

# 测试LLM
print("\n3. 测试LLM...")
from ai.cover_letter import CoverLetterGenerator
llm = CoverLetterGenerator(config)
test_cover = llm.generate(
    job_description="需要Web3产品经理",
    job_requirements=["Web3", "产品经理"]
)
print(f"   生成字符: {len(test_cover)}")
print("   ✅ LLM OK")

print("\n" + "=" * 50)
print("✅ 所有测试通过！")
print("=" * 50)

# 列出可用命令
print("""
📋 可用命令:

🔍 搜索职位:
   python src/telegram_bot.py 搜索 Web3 深圳
   
📝 投递简历:
   python src/telegram_bot.py 投递 职位ID

📊 查看统计:
   python src/telegram_bot.py 统计

⚙️ 自动运行:
   bash auto_job_cron.sh
""")
