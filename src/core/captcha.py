#!/usr/bin/env python3
"""
验证码处理模块
"""

import time
import base64
from typing import Optional


class CaptchaHandler:
    """验证码处理器"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('captcha.enabled', False)
        self.provider = config.get('captcha.provider', 'manual')
        self.api_key = config.get('captcha.api_key', '')
    
    def solve_slider(self, image_url: str = None, image_bytes: bytes = None) -> Optional[float]:
        """
        解决滑块验证码
        返回滑动距离
        """
        if self.provider == 'manual':
            return self._manual_slider()
        elif self.provider == '2captcha':
            return self._solve_2captcha(image_url, image_bytes, 'Slider')
        elif self.provider == '打码平台':
            return self._solve_dama(image_url, image_bytes)
        
        return None
    
    def solve_image(self, image_url: str = None, image_bytes: bytes = None) -> str:
        """
        解决图片验证码
        返回识别文字
        """
        if self.provider == 'manual':
            return self._manual_input()
        elif self.provider == '2captcha':
            return self._solve_2captcha(image_url, image_bytes, 'Image')
        elif self.provider == 'dama':
            return self._solve_dama(image_url, image_bytes)
        
        return ""
    
    def solve_re captcha(self, site_url: str, site_key: str) -> str:
        """
        解决reCAPTCHA
        返回token
        """
        if self.provider == '2captcha':
            return self._solve_recaptcha_2captcha(site_url, site_key)
        
        # 手动模式：等待用户处理
        print("请手动完成验证码...")
        time.sleep(30)
        return ""
    
    def _manual_slider(self) -> Optional[float]:
        """手动滑动（暂停等待用户操作）"""
        print("⚠️ 请手动完成滑块验证，完成后程序将继续...")
        time.sleep(10)  # 等待用户
        return 0.5  # 假设完成
    
    def _manual_input(self) -> str:
        """手动输入"""
        print("⚠️ 请在网页中输入验证码...")
        time.sleep(10)
        return input("请输入验证码: ")
    
    def _solve_2captcha(self, image_url: str, image_bytes: bytes, captcha_type: str) -> str:
        """使用2Captcha服务"""
        try:
            import requests
            
            # 上传验证码
            url = "http://2captcha.com/in.php"
            
            files = {}
            if image_bytes:
                files['file'] = ('captcha.jpg', image_bytes)
            elif image_url:
                files['urlic'] = image_url
            
            data = {
                'key': self.api_key,
                'method': 'post' if image_bytes else 'urlic',
                'json': 1,
                'type': captcha_type
            }
            
            response = requests.post(url, files=files, data=data, timeout=10)
            result = response.json()
            
            if result.get('status') == 1:
                captcha_id = result.get('request')
                
                # 等待识别结果
                for _ in range(20):
                    time.sleep(3)
                    result_url = f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}&json=1"
                    resp = requests.get(result_url, timeout=10)
                    result = resp.json()
                    
                    if result.get('status') == 1:
                        return result.get('request')
                
            return ""
            
        except Exception as e:
            print(f"2Captcha识别失败: {e}")
            return ""
    
    def _solve_dama(self, image_url: str, image_bytes: bytes) -> str:
        """使用打码平台"""
        # 类似2Captcha实现
        print("打码平台待集成...")
        return ""
    
    def _solve_recaptcha_2captcha(self, site_url: str, site_key: str) -> str:
        """解决reCAPTCHA"""
        try:
            import requests
            
            url = "http://2captcha.com/in.php"
            data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': site_url,
                'json': 1
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('status') == 1:
                captcha_id = result.get('request')
                
                for _ in range(40):
                    time.sleep(3)
                    result_url = f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}&json=1"
                    resp = requests.get(result_url, timeout=10)
                    result = resp.json()
                    
                    if result.get('status') == 1:
                        return result.get('request')
            
            return ""
            
        except Exception as e:
            print(f"reCAPTCHA识别失败: {e}")
            return ""


class CaptchaDetector:
    """验证码检测器"""
    
    @staticmethod
    def detect(page) -> str:
        """检测页面中的验证码类型"""
        captcha_types = []
        
        try:
            # 滑块验证码
            if page.locator('.geetest_slider').count() > 0:
                captcha_types.append('slider_geetest')
            if page.locator('.nc_wrapper').count() > 0:
                captcha_types.append('slider_ali')
            
            # 图片验证码
            if page.locator('#captcha_image').count() > 0:
                captcha_types.append('image')
            
            # reCAPTCHA
            if page.locator('.g-recaptcha').count() > 0:
                captcha_types.append('recaptcha')
            if page.locator('[data-sitekey]').count() > 0:
                captcha_types.append('recaptcha')
            
            # 极点验证码
            if page.locator('.tcaptcha').count() > 0:
                captcha_types.append('tcaptcha')
                
        except Exception:
            pass
        
        return captcha_types[0] if captcha_types else None
