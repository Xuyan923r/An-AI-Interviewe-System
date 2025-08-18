# -*- coding: utf-8 -*-
"""
深挖问题生成器

基于case.docx的深挖提问方式，生成专业的经历追问
"""

import ollama
import random
from typing import Dict, List, Optional
from .case_prompts import CaseBasedPrompts


class DeepDiveQuestionGenerator:
    """深挖问题生成器"""
    
    def __init__(self):
        self.case_prompts = CaseBasedPrompts()
        self.fallback_questions = self.case_prompts.get_fallback_questions()
        
    def generate_deep_dive_question(self, user_experience: str, question_history: List[Dict],
                                  technical_keywords: List[str], jd_data: Dict = None,
                                  question_number: int = 2, total_questions: int = 3) -> Dict:
        """
        生成深挖追问
        
        Args:
            user_experience: 用户经历描述
            question_history: 已提问历史
            technical_keywords: 技术关键词
            jd_data: 职位数据
            question_number: 当前问题编号
            total_questions: 总问题数
            
        Returns:
            深挖问题数据
        """
        try:
            # AI生成深挖问题
            ai_question = self._generate_ai_deep_dive_question(
                user_experience, question_history, technical_keywords, jd_data
            )
            
            if ai_question:
                return {
                    'question': ai_question,
                    'question_type': 'deep_dive',
                    'source': 'ai_generated_deep_dive',
                    'stage': '第二阶段：经历类问题',
                    'question_number': question_number,
                    'total_questions': total_questions,
                    'tech_keywords': technical_keywords,
                    'category': '深挖追问'
                }
        except Exception as e:
            print(f"AI深挖问题生成失败: {e}")
        
        # 备用方案：使用预定义问题
        fallback_question = self._get_fallback_deep_dive_question(
            user_experience, question_history, technical_keywords
        )
        
        return {
            'question': fallback_question,
            'question_type': 'deep_dive_fallback',
            'source': 'fallback',
            'stage': '第二阶段：经历类问题',
            'question_number': question_number,
            'total_questions': total_questions,
            'tech_keywords': technical_keywords,
            'category': '深挖追问'
        }
    
    def _generate_ai_deep_dive_question(self, user_experience: str, question_history: List[Dict],
                                      technical_keywords: List[str], jd_data: Dict = None) -> Optional[str]:
        """使用AI生成深挖问题"""
        prompt = self._build_deep_dive_prompt(user_experience, question_history, technical_keywords, jd_data)
        
        response = ollama.chat(
            model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        ai_question = response['message']['content'].strip()
        return self._clean_question_format(ai_question)
    
    def _build_deep_dive_prompt(self, user_experience: str, question_history: List[Dict],
                               technical_keywords: List[str], jd_data: Dict = None) -> str:
        """构建深挖问题的AI提示词"""
        # 获取case.docx的系统提示词
        system_prompt = self.case_prompts.get_system_prompt()
        
        prompt = f"""{system_prompt}

## 当前面试情况
候选人刚刚详细介绍了以下项目经历：

{user_experience}

## 已提问历史
{self._format_question_history(question_history)}

## 技术关键词
从候选人描述中识别到的技术关键词：{', '.join(technical_keywords) if technical_keywords else '无'}

## 职位要求信息
"""
        
        if jd_data:
            if jd_data.get('position'):
                prompt += f"- 目标职位: {jd_data['position']}\n"
            if jd_data.get('keywords'):
                prompt += f"- 技术要求: {', '.join(jd_data['keywords'][:5])}\n"
        
        prompt += """
## 任务要求
请根据上述经历深挖提问原则和示例，生成1个专业的深挖问题。注意：

1. **避免重复**：不要问已经问过的类似问题
2. **技术深度**：深入技术实现细节、参数选择、架构决策
3. **具体量化**：询问具体的数据、指标、性能表现
4. **方案对比**：为什么选择某种技术方案而非其他方案
5. **实际挑战**：遇到的具体技术难点和解决过程
6. **业务价值**：技术实现如何产生实际业务价值

参考case.docx中的提问风格，生成一个具体、专业、有深度的追问，问题应该能够有效评估候选人的技术水平和项目经验。

直接返回问题内容，不需要额外说明。
"""
        
        return prompt
    
    def _format_question_history(self, question_history: List[Dict]) -> str:
        """格式化提问历史"""
        if not question_history:
            return "暂无提问历史"
        
        history = []
        for record in question_history:
            history.append(f"问题{record.get('question_number', '?')}: {record.get('question', '')}")
        
        return "\n".join(history)
    
    def _clean_question_format(self, question: str) -> str:
        """清理问题格式"""
        # 移除多余的标点和格式
        question = question.strip()
        
        # 移除可能的前缀
        prefixes_to_remove = [
            "问题：", "追问：", "深挖问题：", "Q:", "Question:", 
            "下一个问题：", "接下来问：", "我想问："
        ]
        
        for prefix in prefixes_to_remove:
            if question.startswith(prefix):
                question = question[len(prefix):].strip()
        
        # 确保问题以问号结尾
        if not question.endswith('？') and not question.endswith('?'):
            question += '？'
        
        return question
    
    def _get_fallback_deep_dive_question(self, user_experience: str, question_history: List[Dict],
                                       technical_keywords: List[str]) -> str:
        """获取备用深挖问题"""
        # 根据技术关键词和经历内容选择合适的问题类别
        asked_types = set()
        for q in question_history:
            if q.get('question_type') != 'initial_experience_request':
                asked_types.add(self._categorize_question(q.get('question', '')))
        
        # 选择还没问过的问题类型
        available_categories = [cat for cat in self.case_prompts.get_question_categories() 
                              if cat not in asked_types]
        
        if not available_categories:
            available_categories = self.case_prompts.get_question_categories()
        
        # 根据技术关键词和经历内容智能选择问题类别
        if technical_keywords:
            if any(keyword in ['性能', '优化', '延迟', '吞吐量'] for keyword in technical_keywords):
                category = 'performance_metrics'
            elif any(keyword in ['架构', '设计', '微服务', '分布式'] for keyword in technical_keywords):
                category = 'architecture_design'
            else:
                category = 'technical_details'
        else:
            category = random.choice(available_categories)
        
        # 确保选择的类别存在
        if category not in self.fallback_questions:
            category = 'technical_details'
        
        questions = self.fallback_questions[category]
        return random.choice(questions)
    
    def _categorize_question(self, question: str) -> str:
        """对问题进行分类"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['性能', '指标', '延迟', '吞吐量', '响应时间']):
            return 'performance_metrics'
        elif any(word in question_lower for word in ['架构', '设计', '系统', '模块']):
            return 'architecture_design'
        elif any(word in question_lower for word in ['业务', '价值', '效果', 'roi', '用户']):
            return 'business_impact'
        elif any(word in question_lower for word in ['团队', '协作', '分工', '管理']):
            return 'team_collaboration'
        else:
            return 'technical_details'
