# -*- coding: utf-8 -*-
"""
第一阶段非技术问题评估器

负责评估非技术问题的回答质量，从沟通能力、逻辑性、
完整性等多个维度进行综合评估。
"""

import ollama
import re
from typing import Dict, List, Optional


class NonTechnicalEvaluator:
    """非技术问题评估器"""
    
    def __init__(self):
        self.evaluation_criteria = {
            "self_introduction": {
                "communication": 0.3,    # 表达清晰度
                "completeness": 0.3,     # 信息完整性
                "relevance": 0.2,        # 与岗位相关性
                "logic": 0.2            # 逻辑结构
            },
            "career_planning": {
                "clarity": 0.3,          # 目标清晰度
                "feasibility": 0.3,      # 规划可行性
                "match": 0.2,            # 与岗位匹配度
                "motivation": 0.2        # 动机合理性
            },
            "company_position": {
                "knowledge": 0.4,        # 了解程度
                "preparation": 0.3,      # 准备充分性
                "sincerity": 0.3        # 求职诚意
            },
            "work_attitude": {
                "values": 0.4,           # 价值观
                "teamwork": 0.3,         # 团队合作
                "problem_solving": 0.3   # 问题解决
            }
        }
    
    def evaluate_response(self, user_response: str, question_data: Dict, context: Dict) -> Dict:
        """
        评估用户回答
        
        Args:
            user_response: 用户回答
            question_data: 问题数据
            context: 上下文信息（简历、JD等）
            
        Returns:
            评估结果字典
        """
        question_type = question_data.get('question_type', 'general')
        
        try:
            # AI评估
            ai_evaluation = self._ai_evaluate(user_response, question_data, context)
            
            # 基础评估
            basic_evaluation = self._basic_evaluate(user_response, question_type)
            
            # 综合评分
            final_score = self._calculate_final_score(ai_evaluation, basic_evaluation, question_type)
            
            return {
                'score': final_score,
                'ai_evaluation': ai_evaluation,
                'basic_metrics': basic_evaluation,
                'question_type': question_type,
                'feedback': self._generate_feedback(ai_evaluation, basic_evaluation, question_type),
                'suggestions': self._generate_suggestions(ai_evaluation, basic_evaluation, question_type)
            }
            
        except Exception as e:
            print(f"评估过程出错: {e}")
            # 备用评估
            fallback_score = self._fallback_evaluate(user_response, question_type)
            return {
                'score': fallback_score,
                'ai_evaluation': None,
                'basic_metrics': None,
                'question_type': question_type,
                'feedback': "回答已记录，请继续下一个问题。",
                'suggestions': []
            }
    
    def _ai_evaluate(self, user_response: str, question_data: Dict, context: Dict) -> Dict:
        """AI智能评估"""
        prompt = self._build_evaluation_prompt(user_response, question_data, context)
        
        response = ollama.chat(
            model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        evaluation_text = response['message']['content'].strip()
        return self._parse_ai_evaluation(evaluation_text)
    
    def _build_evaluation_prompt(self, user_response: str, question_data: Dict, context: Dict) -> str:
        """构建AI评估提示词"""
        question_type = question_data.get('question_type', 'general')
        
        prompt = f"""
你是一位经验丰富的HR面试官，正在评估候选人在第一阶段非技术问题的回答质量。

## 问题信息
问题类型: {question_type}
问题内容: {question_data.get('question', '')}

## 候选人回答
{user_response}

## 评估标准
请从以下维度评估回答质量（每个维度0-1分）：

"""
        
        # 根据问题类型添加特定评估标准
        if question_type == "self_introduction":
            prompt += """
1. 表达清晰度 (0-1): 语言表达是否清晰、流畅、有条理
2. 信息完整性 (0-1): 是否包含教育背景、工作经历、技能等关键信息
3. 与岗位相关性 (0-1): 介绍内容与目标职位的相关程度
4. 逻辑结构 (0-1): 介绍是否有清晰的逻辑结构和层次
"""
        elif question_type == "career_planning":
            prompt += """
1. 目标清晰度 (0-1): 职业目标是否明确、具体
2. 规划可行性 (0-1): 规划是否现实、可执行
3. 与岗位匹配度 (0-1): 规划与目标职位的匹配程度
4. 动机合理性 (0-1): 选择这个发展方向的动机是否合理
"""
        elif question_type == "company_position":
            prompt += """
1. 了解程度 (0-1): 对公司和岗位的了解深度
2. 准备充分性 (0-1): 面试前的准备是否充分
3. 求职诚意 (0-1): 对这个职位的兴趣和诚意
"""
        elif question_type == "work_attitude":
            prompt += """
1. 价值观 (0-1): 工作价值观是否积极、合理
2. 团队合作 (0-1): 团队合作意识和能力
3. 问题解决 (0-1): 面对问题的态度和解决能力
"""
        
        prompt += """

## 输出格式
请按以下格式输出评估结果：

评分:
- 维度1: 0.X
- 维度2: 0.X
- 维度3: 0.X
- 维度4: 0.X (如果有)

总体评价: [简短的总体评价，50字以内]

改进建议: [具体的改进建议，100字以内]

请确保评分客观公正，符合非技术面试的评估标准。
"""
        
        return prompt
    
    def _parse_ai_evaluation(self, evaluation_text: str) -> Dict:
        """解析AI评估结果"""
        result = {
            'scores': {},
            'overall_comment': '',
            'improvement_suggestions': ''
        }
        
        try:
            # 提取评分
            score_pattern = r'- (.*?): (0\.\d+)'
            scores = re.findall(score_pattern, evaluation_text)
            for dimension, score in scores:
                result['scores'][dimension.strip()] = float(score)
            
            # 提取总体评价
            overall_match = re.search(r'总体评价[:：]\s*([^\n]+)', evaluation_text)
            if overall_match:
                result['overall_comment'] = overall_match.group(1).strip()
            
            # 提取改进建议
            suggestion_match = re.search(r'改进建议[:：]\s*([^\n]+)', evaluation_text)
            if suggestion_match:
                result['improvement_suggestions'] = suggestion_match.group(1).strip()
                
        except Exception as e:
            print(f"解析AI评估结果失败: {e}")
        
        return result
    
    def _basic_evaluate(self, user_response: str, question_type: str) -> Dict:
        """基础评估（基于规则）"""
        response_length = len(user_response.strip())
        word_count = len(user_response.split())
        
        # 长度评分
        if response_length < 50:
            length_score = 0.3
        elif response_length < 200:
            length_score = 0.6
        elif response_length < 500:
            length_score = 0.9
        else:
            length_score = 1.0
        
        # 词汇丰富度
        unique_words = len(set(user_response.split()))
        vocabulary_score = min(unique_words / max(word_count, 1) * 2, 1.0)
        
        # 结构性（是否包含常见结构词）
        structure_words = ['首先', '其次', '然后', '最后', '另外', '因为', '所以', '但是', '然而']
        structure_count = sum(1 for word in structure_words if word in user_response)
        structure_score = min(structure_count / 3, 1.0)
        
        return {
            'length_score': length_score,
            'vocabulary_score': vocabulary_score,
            'structure_score': structure_score,
            'response_length': response_length,
            'word_count': word_count
        }
    
    def _calculate_final_score(self, ai_evaluation: Dict, basic_evaluation: Dict, question_type: str) -> float:
        """计算最终评分"""
        if ai_evaluation and ai_evaluation.get('scores'):
            # 使用AI评估结果
            scores = list(ai_evaluation['scores'].values())
            ai_score = sum(scores) / len(scores) if scores else 0.5
            
            # 结合基础评估
            basic_score = (
                basic_evaluation['length_score'] * 0.3 +
                basic_evaluation['vocabulary_score'] * 0.3 +
                basic_evaluation['structure_score'] * 0.4
            )
            
            # AI评估权重更高
            final_score = ai_score * 0.8 + basic_score * 0.2
        else:
            # 仅使用基础评估
            final_score = (
                basic_evaluation['length_score'] * 0.4 +
                basic_evaluation['vocabulary_score'] * 0.3 +
                basic_evaluation['structure_score'] * 0.3
            )
        
        return round(min(max(final_score, 0.0), 1.0), 2)
    
    def _generate_feedback(self, ai_evaluation: Dict, basic_evaluation: Dict, question_type: str) -> str:
        """生成反馈"""
        if ai_evaluation and ai_evaluation.get('overall_comment'):
            return ai_evaluation['overall_comment']
        
        # 基于基础评估生成反馈
        feedback_parts = []
        
        if basic_evaluation['length_score'] < 0.5:
            feedback_parts.append("回答略显简短，建议更详细地展开")
        elif basic_evaluation['length_score'] > 0.8:
            feedback_parts.append("回答内容丰富")
        
        if basic_evaluation['structure_score'] < 0.3:
            feedback_parts.append("表达逻辑可以更清晰")
        
        if basic_evaluation['vocabulary_score'] > 0.7:
            feedback_parts.append("用词恰当")
        
        return "，".join(feedback_parts) if feedback_parts else "回答已记录"
    
    def _generate_suggestions(self, ai_evaluation: Dict, basic_evaluation: Dict, question_type: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if ai_evaluation and ai_evaluation.get('improvement_suggestions'):
            suggestions.append(ai_evaluation['improvement_suggestions'])
        
        # 基于基础评估生成建议
        if basic_evaluation['length_score'] < 0.5:
            suggestions.append("建议回答更加详细，提供具体的例子或经历")
        
        if basic_evaluation['structure_score'] < 0.5:
            suggestions.append("建议使用'首先'、'其次'等词语来组织回答结构")
        
        return suggestions
    
    def _fallback_evaluate(self, user_response: str, question_type: str) -> float:
        """备用评估方法"""
        response_length = len(user_response.strip())
        
        if response_length < 20:
            return 0.2
        elif response_length < 100:
            return 0.5
        elif response_length < 300:
            return 0.7
        else:
            return 0.8
