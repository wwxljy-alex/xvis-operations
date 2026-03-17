#!/usr/bin/env python3
"""
Cover Letter生成模块
基于LLM生成个性化求职信
"""

import re
import json
from typing import Dict, List


class CoverLetterGenerator:
    """Cover Letter生成器"""
    
    def __init__(self, config):
        self.config = config
        self.provider = config.get('llm.provider', 'minimax')
        self.model = config.get('llm.model', 'MiniMax-M2.5')
        self.temperature = config.get('llm.temperature', 0.7)
        self._init_client()
    
    def _init_client(self):
        """初始化LLM客户端"""
        if self.provider == 'openai':
            import openai
            self.client = openai
            self.client.api_key = self.config.get('llm.api_key')
        elif self.provider == 'minimax':
            # Minimax API
            self.api_key = self.config.get('llm.api_key', '')
    
    def generate(self, job_description: str = "", 
                 job_requirements: List[str] = None,
                 resume_summary: str = None,
                 tone: str = "professional") -> str:
        """生成Cover Letter"""
        
        # 解析JD
        parsed_jd = self._parse_jd(job_description, job_requirements or [])
        
        # 构建prompt
        prompt = self._build_prompt(parsed_jd, resume_summary, tone)
        
        # 调用LLM
        content = self._call_llm(prompt)
        
        return content
    
    def _parse_jd(self, description: str, requirements: List[str]) -> Dict:
        """解析JD"""
        # 提取关键信息
        result = {
            'title': '',
            'company': '',
            'requirements': [],
            'benefits': [],
            'skills': [],
            'experience': '',
            'education': ''
        }
        
        # 提取职位要求
        if requirements:
            result['requirements'] = requirements
        
        # 从描述中提取
        if description:
            # 提取技能关键词
            skills_pattern = r'(Python|Java|Go|React|Vue|Node\.js|SQL|AWS|Docker|K8s|AI|ML|LLM|Data|Analytics)'
            skills = re.findall(skills_pattern, description, re.IGNORECASE)
            result['skills'] = list(set(skills))
            
            # 提取经验要求
            exp_pattern = r'(\d+)\+?\s*(?:年|years?).*经验|经验(\d+)\+?\s*(?:年|years?)'
            exp_match = re.search(exp_pattern, description)
            if exp_match:
                result['experience'] = exp_match.group(0)
            
            # 提取学历要求
            edu_pattern = r'(本科|硕士|博士| Bachelor| Master| PhD)'
            edu_match = re.search(edu_pattern, description)
            if edu_match:
                result['education'] = edu_match.group(0)
        
        return result
    
    def _build_prompt(self, jd: Dict, resume_summary: str, tone: str) -> str:
        """构建Prompt"""
        
        resume_info = resume_summary or "暂无简历摘要"
        
        prompt = f"""你是一位专业的求职信写作助手。请根据以下信息生成一封专业的Cover Letter。

## 职位信息
- 职位要求: {', '.join(jd.get('requirements', []))}
- 技能要求: {', '.join(jd.get('skills', []))}
- 经验要求: {jd.get('experience', '不限')}
- 学历要求: {jd.get('education', '不限')}

## 候选人简历摘要
{resume_info}

## 风格要求
- 语气: {tone}
- 语言: 中文（如果职位要求英文则用英文）
- 长度: 300-500字

## 要求
1. 开头：表明求职意向
2. 主体：匹配JD要求，展示相关经验和技能
3. 结尾：表达热情，请求面试机会

请生成一封专业、简洁、有针对性的Cover Letter：
"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        
        if self.provider == 'openai':
            return self._call_openai(prompt)
        elif self.provider == 'minimax':
            return self._call_minimax(prompt)
        else:
            return self._fallback_generate(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI调用失败: {e}")
            return self._fallback_generate(prompt)
    
    def _call_minimax(self, prompt: str) -> str:
        """调用Minimax API"""
        try:
            import requests
            
            url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return self._fallback_generate(prompt)
                
        except Exception as e:
            print(f"Minimax调用失败: {e}")
            return self._fallback_generate(prompt)
    
    def _fallback_generate(self, prompt: str) -> str:
        """备选生成方案（模板）"""
        
        return f"""尊敬的招聘经理：

您好！我对贵公司的职位非常感兴趣，特此申请。

通过仔细阅读职位描述，我发现自己与该岗位的要求高度匹配：
- 具备扎实的专业技能
- 有良好的团队协作能力
- 热爱行业，积极进取

我期待能够加入贵公司，为团队贡献自己的力量。

恳请给予面试机会，期待与您进一步交流。

此致
敬礼

申请人
{self.config.get('user.name', '应聘者')}
"""
    
    def generate_batch(self, jobs: List[Dict]) -> List[str]:
        """批量生成"""
        results = []
        
        for job in jobs:
            cover_letter = self.generate(
                job_description=job.get('description', ''),
                job_requirements=job.get('requirements', []),
                resume_summary=job.get('resume_summary')
            )
            results.append(cover_letter)
        
        return results
