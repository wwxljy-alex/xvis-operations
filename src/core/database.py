#!/usr/bin/env python3
"""
数据库模块 - SQLite存储
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional


class Database:
    """SQLite数据库管理"""
    
    def __init__(self, db_path: str = "data/autojob.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 职位表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                company TEXT,
                location TEXT,
                salary TEXT,
                description TEXT,
                requirements TEXT,
                url TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, job_id)
            )
        """)
        
        # 投递记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                cover_letter TEXT,
                applied_at TIMESTAMP,
                response_at TIMESTAMP,
                notes TEXT,
                UNIQUE(job_id, platform)
            )
        """)
        
        # 账号表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                username TEXT,
                password TEXT,
                cookies TEXT,
                token TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # 用户简历表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                file_path TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_job(self, job: Dict) -> int:
        """保存职位"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO jobs 
            (job_id, platform, title, company, location, salary, 
             description, requirements, url, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.get('job_id'),
            job.get('platform'),
            job.get('title'),
            job.get('company'),
            job.get('location'),
            job.get('salary'),
            job.get('description'),
            job.get('requirements'),
            job.get('url'),
            job.get('source')
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def get_job(self, platform: str, job_id: str) -> Optional[Dict]:
        """获取职位"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs WHERE platform = ? AND job_id = ?
        """, (platform, job_id))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_jobs(self, platform: str = None, keywords: list = None, 
                 limit: int = 100) -> List[Dict]:
        """获取职位列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if keywords:
            for kw in keywords:
                query += " AND (title LIKE ? OR company LIKE ?)"
                params.extend([f'%{kw}%', f'%{kw}%'])
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_application(self, app: Dict):
        """保存投递记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO applications
            (job_id, platform, status, cover_letter, applied_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            app.get('job_id'),
            app.get('platform'),
            app.get('status', 'pending'),
            app.get('cover_letter'),
            app.get('applied_at') or datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def is_applied(self, job_id: str) -> bool:
        """检查是否已投递"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM applications 
            WHERE job_id = ? AND status = 'success'
        """, (job_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_applications(self, platform: str = None, status: str = None) -> List[Dict]:
        """获取投递记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM applications WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY applied_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_application_status(self, job_id: str, status: str, notes: str = None):
        """更新投递状态"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE applications 
            SET status = ?, response_at = ?, notes = ?
            WHERE job_id = ?
        """, (status, datetime.now().isoformat(), notes, job_id))
        
        conn.commit()
        conn.close()
    
    def save_account(self, account: Dict):
        """保存账号"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO accounts
            (platform, username, password, cookies, token, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            account.get('platform'),
            account.get('username'),
            account.get('password'),
            account.get('cookies'),
            account.get('token'),
            account.get('status', 'active'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_account(self, platform: str) -> Optional[Dict]:
        """获取账号"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM accounts WHERE platform = ? AND status = 'active'
            ORDER BY updated_at DESC LIMIT 1
        """, (platform,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
