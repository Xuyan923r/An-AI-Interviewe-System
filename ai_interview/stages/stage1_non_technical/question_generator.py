# -*- coding: utf-8 -*-
"""
第一阶段非技术问题生成器

负责根据简历和JD信息生成个性化的非技术问题
"""

import random
import ollama
from typing import Dict, List, Optional


class NonTechnicalQuestionGenerator:
    """非技术问题生成器"""
    
    def __init__(self):
        # 预定义问题模板
        self.question_templates = {
            "self_introduction": [
                "请简单介绍一下您自己，包括您的教育背景、工作经历和主要技能。",
                "能否用几分钟时间介绍一下您的个人背景和职业经历？",
                "请谈谈您的基本情况，包括专业背景和工作经验。"
            ],
            "career_planning": [
                "请谈谈您的职业规划，您希望在未来3-5年内达到什么样的职业目标？",
                "您对自己的职业发展有什么规划？为什么选择这个发展方向？",
                "请描述一下您理想的职业发展路径。"
            ],
            "company_position": [
                "您为什么对我们公司感兴趣？您了解我们公司的主要业务吗？",
                "您对这个职位有什么了解？为什么觉得自己适合这个岗位？",
                "您认为这个职位的主要职责是什么？您有哪些相关经验？"
            ],
            "work_attitude": [
                "您认为在团队合作中最重要的是什么？请结合您的经历谈谈。",
                "当您遇到工作中的挫折时，您通常是如何处理的？",
                "您如何平衡工作效率和工作质量？请举例说明。"
            ]
        }
        
    def generate_question(self, question_type: str, resume_data: Dict, 
                         jd_data: Dict, previous_questions: List = None) -> Dict:
        """
        生成非技术问题
        
        Args:
            question_type: 问题类型
            resume_data: 简历数据
            jd_data: 职位描述数据
            previous_questions: 之前已问的问题
            
        Returns:
            问题数据字典
        """
        try:
            # 尝试AI生成个性化问题
            ai_question = self._generate_ai_question(question_type, resume_data, jd_data)
            if ai_question:
                return {
                    'question': ai_question,
                    'question_type': question_type,
                    'source': 'ai_generated',
                    'category': self._get_question_category(question_type)
                }
        except Exception as e:
            print(f"AI问题生成失败: {e}")
        
        # 备用：使用预定义模板
        template_question = self._get_template_question(question_type, resume_data, jd_data)
        return {
            'question': template_question,
            'question_type': question_type,
            'source': 'template',
            'category': self._get_question_category(question_type)
        }
    
    def _generate_ai_question(self, question_type: str, resume_data: Dict, jd_data: Dict) -> Optional[str]:
        """使用AI生成个性化问题"""
        prompt = self._build_ai_prompt(question_type, resume_data, jd_data)
        
        try:
            response = ollama.chat(
                model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
        except Exception:
            return None
    
    def _build_ai_prompt(self, question_type: str, resume_data: Dict, jd_data: Dict) -> str:
        """构建AI生成问题的提示词"""
        base_prompt = """
你是一位专业的HR面试官，正在进行面试的第一阶段：非技术问题环节。
请根据候选人的简历信息和目标职位要求，生成一个个性化的非技术问题。

## 面试阶段说明
第一阶段主要考察：
1. 基本情况和沟通能力
2. 职业规划和发展目标
3. 对公司和岗位的了解程度
4. 工作态度和价值观

## 候选人信息
"""
        
        # 添加简历信息
        if resume_data:
            if resume_data.get('name'):
                base_prompt += f"- 姓名: {resume_data['name']}\n"
            if resume_data.get('experience'):
                base_prompt += f"- 工作经历: {len(resume_data['experience'])}项\n"
                for exp in resume_data['experience'][:2]:
                    base_prompt += f"  * {exp}\n"
            if resume_data.get('skills'):
                base_prompt += f"- 主要技能: {', '.join(resume_data['skills'][:5])}\n"
            if resume_data.get('education'):
                base_prompt += f"- 教育背景: {resume_data['education']}\n"
        
        # 添加职位信息
        if jd_data:
            if jd_data.get('position'):
                base_prompt += f"\n## 目标职位\n- 职位名称: {jd_data['position']}\n"
            if jd_data.get('company'):
                base_prompt += f"- 公司: {jd_data['company']}\n"
            if jd_data.get('requirements'):
                base_prompt += f"- 主要要求: {', '.join(jd_data['requirements'][:3])}\n"
        
        # 根据问题类型添加特定要求
        type_prompts = {
            "self_introduction": """
## 问题要求
请生成一个自我介绍类问题，要求候选人介绍个人背景、工作经历和主要技能。
问题应该：
- 引导候选人系统性地介绍自己
- 结合目标职位的相关性
- 便于后续深入了解
""",
            "career_planning": """
## 问题要求
请生成一个职业规划类问题，了解候选人的职业发展目标和规划。
问题应该：
- 了解候选人的长期职业目标
- 评估职业规划的合理性
- 判断与公司发展的匹配度
""",
            "company_position": """
## 问题要求
请生成一个关于公司和岗位了解的问题，评估候选人的求职诚意和准备程度。
问题应该：
- 了解候选人对公司的认知
- 评估对岗位职责的理解
- 判断求职动机的真实性
""",
            "work_attitude": """
## 问题要求
请生成一个工作态度类问题，了解候选人的工作价值观和团队合作能力。
问题应该：
- 了解候选人的工作态度
- 评估团队合作能力
- 判断价值观匹配度
"""
        }
        
        base_prompt += type_prompts.get(question_type, "")
        base_prompt += "\n请直接返回问题内容，不需要额外说明。"
        
        return base_prompt
    
    def _get_template_question(self, question_type: str, resume_data: Dict, jd_data: Dict) -> str:
        """获取模板问题并进行个性化调整"""
        templates = self.question_templates.get(question_type, [])
        if not templates:
            return "请简单介绍一下您自己。"
        
        base_question = random.choice(templates)
        
        # 根据简历和JD信息进行个性化调整
        if question_type == "company_position" and jd_data:
            if jd_data.get('position'):
                base_question = f"您为什么对{jd_data['position']}这个职位感兴趣？您觉得自己哪些经验与这个岗位最匹配？"
        
        elif question_type == "career_planning" and resume_data:
            if resume_data.get('experience'):
                years = len(resume_data['experience'])
                if years >= 3:
                    base_question = "基于您已有的工作经验，请谈谈您未来3-5年的职业发展规划。"
                else:
                    base_question = "作为职场新人，您对自己的职业发展有什么规划和期望？"
        
        return base_question
    
    def _get_question_category(self, question_type: str) -> str:
        """获取问题分类"""
        categories = {
            "self_introduction": "个人背景",
            "career_planning": "职业规划", 
            "company_position": "岗位认知",
            "work_attitude": "工作态度"
        }
        return categories.get(question_type, "综合素质")
