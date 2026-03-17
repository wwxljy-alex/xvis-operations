#!/usr/bin/env python3
"""
配置管理模块
"""

import os
import yaml
from typing import Any, Dict


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            return self._default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'database': {'path': 'data/autojob.db'},
            'logging': {'level': 'INFO', 'file': 'logs/autojob.log'},
            'browser': {
                'headless': False,
                'timeout': 30000,
                'implicit_wait': 10
            },
            'application': {
                'delay_min': 3000,
                'delay_max': 8000,
                'max_retries': 3
            },
            'platforms': {}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True)
    
    def get_all(self) -> Dict:
        """获取所有配置"""
        return self.config
