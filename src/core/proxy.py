#!/usr/bin/env python3
"""
代理池模块
"""

import random
import time
from typing import List, Dict, Optional


class ProxyPool:
    """代理池管理"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('proxy.enabled', False)
        self.proxies = config.get('proxy.pool', [])
        self.current_index = 0
        self.failed_proxies = []
    
    def get_proxy(self) -> Optional[Dict]:
        """获取一个代理"""
        if not self.enabled or not self.proxies:
            return None
        
        # 尝试获取可用代理
        available = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available:
            # 重置失败列表
            self.failed_proxies = []
            available = self.proxies
        
        # 随机选择
        proxy = random.choice(available)
        return proxy
    
    def mark_failed(self, proxy: Dict):
        """标记失败的代理"""
        if proxy:
            self.failed_proxies.append(proxy)
    
    def get_proxy_dict(self) -> Optional[Dict]:
        """获取代理格式（供Playwright使用）"""
        proxy = self.get_proxy()
        if not proxy:
            return None
        
        result = {
            'server': f"http://{proxy.get('host')}:{proxy.get('port')}"
        }
        
        if proxy.get('username') and proxy.get('password'):
            result['username'] = proxy['username']
            result['password'] = proxy['password']
        
        return result


class ProxyProvider:
    """代理服务商"""
    
    # 可用的代理服务商（需要API key）
    PROVIDERS = [
        ' luminati',      # luminati.io
        'oxylabs',        # oxylabs.io
        'smartproxy',     # smartproxy.com
        'brightdata',     # brightdata.com
        'kuaidaili',      # 快代理
        'zhimaip',        # 芝麻代理
    ]
    
    @staticmethod
    def fetch_from_provider(provider: str, api_key: str, count: int = 10) -> List[Dict]:
        """从代理服务商获取代理"""
        # 这是一个示例实现
        proxies = []
        
        if provider == 'kuaidaili':
            import requests
            try:
                url = f"http://api.kuaidaili.com/api/getproxy?orderid=YOUR_ORDERNO&num={count}&format=json"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if data.get('code') == 0:
                    for p in data.get('data', []):
                        proxies.append({
                            'host': p.get('ip'),
                            'port': p.get('port'),
                            'provider': 'kuaidaili'
                        })
            except Exception as e:
                print(f"获取代理失败: {e}")
        
        return proxies
    
    @staticmethod
    def test_proxy(proxy: Dict) -> bool:
        """测试代理是否可用"""
        import requests
        
        try:
            url = "http://httpbin.org/ip"
            proxies = {
                'http': f"http://{proxy.get('host')}:{proxy.get('port')}",
                'https': f"http://{proxy.get('host')}:{proxy.get('port')}"
            }
            response = requests.get(url, proxies=proxies, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
