#!/usr/bin/env python3
"""
通知模块 - Telegram/邮件推送
"""

import os
import requests
from typing import List, Dict, Optional


class Notifier:
    """通知管理器"""
    
    def __init__(self, config):
        self.config = config
        self.telegram_enabled = config.get('notification.telegram.enabled', False)
        self.telegram_token = config.get('notification.telegram.token', '')
        self.telegram_chat_id = config.get('notification.telegram.chat_id', '')
        self.email_enabled = config.get('notification.email.enabled', False)
    
    def send_job_alert(self, jobs: List[Dict]):
        """发送职位提醒"""
        if not jobs:
            return
        
        message = self._format_job_alert(jobs)
        
        if self.telegram_enabled:
            self._send_telegram(message)
        
        if self.email_enabled:
            self._send_email("新职位提醒", message)
    
    def send_apply_result(self, job: Dict, result: bool):
        """发送投递结果"""
        message = self._format_apply_result(job, result)
        
        if self.telegram_enabled:
            self._send_telegram(message)
    
    def send_daily_summary(self, stats: Dict):
        """发送每日汇总"""
        message = self._format_daily_summary(stats)
        
        if self.telegram_enabled:
            self._send_telegram(message)
    
    def _format_job_alert(self, jobs: List[Dict]) -> str:
        """格式化职位提醒"""
        lines = ["📢 新职位提醒", ""]
        
        for job in jobs[:10]:
            title = job.get('title', '未知职位')
            company = job.get('company', '未知公司')
            location = job.get('location', '')
            salary = job.get('salary', '')
            
            lines.append(f"• {title}")
            lines.append(f"  {company} | {location} {salary}")
            lines.append("")
        
        if len(jobs) > 10:
            lines.append(f"... 还有 {len(jobs) - 10} 个职位")
        
        return "\n".join(lines)
    
    def _format_apply_result(self, job: Dict, result: bool) -> str:
        """格式化投递结果"""
        status = "✅ 投递成功" if result else "❌ 投递失败"
        
        title = job.get('title', '未知职位')
        company = job.get('company', '未知公司')
        
        return f"""
{status}

职位: {title}
公司: {company}
平台: {job.get('platform', '')}
"""
    
    def _format_daily_summary(self, stats: Dict) -> str:
        """格式化每日汇总"""
        return f"""
📊 每日投递汇总

总计: {stats.get('total', 0)}
成功: {stats.get('success', 0)}
失败: {stats.get('failed', 0)}
待处理: {stats.get('pending', 0)}
"""
    
    def _send_telegram(self, message: str) -> bool:
        """发送Telegram消息"""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        data = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram发送失败: {e}")
            return False
    
    def _send_email(self, subject: str, message: str) -> bool:
        """发送邮件"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            smtp = self.config.get('notification.email.smtp')
            port = self.config.get('notification.email.port', 587)
            username = self.config.get('notification.email.username')
            password = self.config.get('notification.email.password')
            to = self.config.get('notification.email.to')
            
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp, port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False


class TelegramBot:
    """Telegram机器人"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """发送消息"""
        url = f"{self.api_url}/sendMessage"
        
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def send_photo(self, photo_path: str, caption: str = None) -> bool:
        """发送图片"""
        url = f"{self.api_url}/sendPhoto"
        
        data = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        
        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                response = requests.post(url, data=data, files=files, timeout=30)
            return response.status_code == 200
        except Exception:
            return False
    
    def send_document(self, file_path: str, caption: str = None) -> bool:
        """发送文件"""
        url = f"{self.api_url}/sendDocument"
        
        data = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        
        try:
            with open(file_path, 'rb') as file:
                files = {'document': file}
                response = requests.post(url, data=data, files=files, timeout=30)
            return response.status_code == 200
        except Exception:
            return False
