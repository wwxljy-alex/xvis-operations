#!/usr/bin/env python3
"""
AutoJob Telegram 命令处理
集成到OpenClaw
"""

import os
import sys
import re
import time

# 设置路径
auto_job_path = '/home/ubuntu/clawd/auto_job'
sys.path.insert(0, f'{auto_job_path}/src')
os.chdir(auto_job_path)

from core.config import Config
from core.database import Database
from core.browser import BrowserManager
from platforms.boss_enhanced import BossPlatformEnhanced
from ai.cover_letter import CoverLetterGenerator
from core.notification import Notifier
from core.filter import JobMatcher, JobFilter


class AutoJobBot:
    """AutoJob Telegram机器人"""
    
    def __init__(self):
        self.config = Config('/home/ubuntu/clawd/auto_job/config/config.yaml')
        self.db = Database('/home/ubuntu/clawd/auto_job/data/autojob.db')
        self.browser = None
        self.platforms = {}
        self.llm = CoverLetterGenerator(self.config)
        
    def init_browser(self):
        """初始化浏览器"""
        if not self.browser:
            self.browser = BrowserManager(self.config)
            self.platforms['boss'] = BossPlatformEnhanced(
                self.browser, self.config
            )
    
    def handle_message(self, message: str, user_id: str = None) -> str:
        """处理消息"""
        message = message.strip().lower()
        
        # 帮助
        if message in ['help', '帮助', '/help']:
            return self.get_help()
        
        # 搜索
        if message.startswith('搜索') or message.startswith('search'):
            return self.handle_search(message)
        
        # 投递
        if message.startswith('投递') or message.startswith('apply'):
            return self.handle_apply(message)
        
        # 列表
        if message.startswith('列表') or message.startswith('list'):
            return self.handle_list(message)
        
        # 统计
        if message in ['统计', 'stats', '/stats']:
            return self.handle_stats()
        
        # 测试
        if message in ['test', '测试']:
            return self.handle_test()
        
        return "未知命令，输入 /help 查看帮助"
    
    def get_help(self) -> str:
        """帮助信息"""
        return """
🤖 AutoJob 命令帮助

🔍 搜索职位
  搜索 [关键词] [地点]
  例：搜索 Web3 深圳
  例：搜索 产品经理 香港

📝 投递简历
  投递 [职位ID]
  例：投递 123456

📋 查看列表
  列表
  列表 已投递
  列表 BOSS

📊 统计
  统计

⚙️ 设置
  设置 关键词 Web3,产品经理
  设置 地点 深圳,香港
  设置 薪资 20-50

❓ 帮助
  帮助
"""
    
    def handle_search(self, message: str) -> str:
        """处理搜索"""
        try:
            self.init_browser()
            
            # 解析命令
            parts = message.replace('搜索', '').replace('search', '').strip().split()
            
            keywords = []
            location = ""
            
            for part in parts:
                if part in ['深圳', '广州', '上海', '北京', '香港', '杭州', '成都']:
                    location = part
                else:
                    keywords.append(part)
            
            if not keywords:
                return "请输入搜索关键词\n例：搜索 Web3 深圳"
            
            # 搜索
            boss = self.platforms.get('boss')
            if not boss:
                return "❌ BOSS平台未初始化"
            
            jobs = boss.search_jobs(keywords, location)
            
            if not jobs:
                return f"🔍 关键词: {', '.join(keywords)}\n📍 地点: {location or '不限'}\n\n未找到职位"
            
            # 保存
            for job in jobs:
                self.db.save_job(job)
            
            # 格式化输出
            result = [f"🔍 找到 {len(jobs)} 个职位\n"]
            
            for i, job in enumerate(jobs[:10]):
                title = job.get('title', '')[:20]
                company = job.get('company', '')[:15]
                salary = job.get('salary', '薪资面议')
                job_id = job.get('job_id', '')[:10]
                
                result.append(
                    f"{i+1}. {title}"
                )
                result.append(
                    f"   {company} | {salary}"
                )
                result.append(
                    f"   ID: {job_id}"
                )
                result.append("")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 搜索失败: {str(e)}"
    
    def handle_apply(self, message: str) -> str:
        """处理投递"""
        try:
            # 解析ID
            parts = message.replace('投递', '').replace('apply', '').strip().split()
            if not parts:
                return "请输入职位ID\n例：投递 123456"
            
            job_id = parts[0]
            
            # 生成Cover Letter
            cover_letter = self.llm.generate(
                job_description="",
                job_requirements=[]
            )
            
            # 记录投递
            self.db.save_application({
                'job_id': job_id,
                'platform': 'boss',
                'status': 'pending',
                'cover_letter': cover_letter
            })
            
            return f"✅ 投递成功\n职位ID: {job_id}\n平台: BOSS直聘"
            
        except Exception as e:
            return f"❌ 投递失败: {str(e)}"
    
    def handle_list(self, message: str) -> str:
        """处理列表"""
        parts = message.replace('列表', '').replace('list', '').strip().split()
        
        platform = None
        status = None
        
        for part in parts:
            if part in ['boss', 'lagou', 'liepin']:
                platform = part
            elif part in ['已投递', '成功', '失败']:
                status = 'success' if part == '成功' else 'failed'
        
        jobs = self.db.get_jobs(platform=platform, limit=20)
        
        if not jobs:
            return "📋 暂无职位记录"
        
        result = [f"📋 职位列表 ({len(jobs)}条)\n"]
        
        for job in jobs[:10]:
            result.append(
                f"• {job.get('title', '')} @ {job.get('company', '')}"
            )
            result.append(
                f"  {job.get('location', '')} | {job.get('salary', '')}"
            )
        
        return "\n".join(result)
    
    def handle_stats(self) -> str:
        """处理统计"""
        apps = self.db.get_applications()
        
        total = len(apps)
        success = len([a for a in apps if a.get('status') == 'success'])
        failed = len([a for a in apps if a.get('status') == 'failed'])
        pending = len([a for a in apps if a.get('status') == 'pending'])
        
        return f"""
📊 投递统计

总计: {total}
成功: {success}
失败: {failed}
待处理: {pending}
"""
    
    def handle_test(self) -> str:
        """测试"""
        jobs_count = len(self.db.get_jobs(limit=1000))
        apps_count = len(self.db.get_applications())
        
        return f"""
✅ AutoJob 运行正常

📊 数据统计
职位: {jobs_count}
投递: {apps_count}

🕐 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def close(self):
        """关闭"""
        if self.browser:
            self.browser.close()


# 全局实例
_bot = None

def get_bot():
    """获取机器人实例"""
    global _bot
    if _bot is None:
        _bot = AutoJobBot()
    return _bot


def handle_autojob_command(message: str, user_id: str = None) -> str:
    """处理AutoJob命令"""
    bot = get_bot()
    try:
        return bot.handle_message(message, user_id)
    except Exception as e:
        return f"❌ 错误: {str(e)}"


if __name__ == '__main__':
    # 测试
    bot = get_bot()
    print(bot.handle_test())
    bot.close()
