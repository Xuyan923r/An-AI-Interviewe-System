# -*- coding: utf-8 -*-
"""
技术问题评估器

负责评估技术类问题的回答质量，支持多维度评估和智能反馈。
"""

import ollama
import re
from typing import Dict, List, Optional


class TechnicalEvaluator:
    """技术问题评估器"""
    
    def __init__(self):
        self.evaluation_criteria = {
            'technical_accuracy': 0.4,    # 技术准确性
            'depth_understanding': 0.3,   # 深度理解
            'practical_experience': 0.2,  # 实践经验
            'clarity': 0.1                # 表达清晰度
        }
    
    def evaluate_response(self, user_response: str, question_data: Dict, 
                         context: Dict) -> Dict:
        """
        评估技术回答
        
        Args:
            user_response: 用户回答
            question_data: 问题数据
            context: 上下文信息
            
        Returns:
            评估结果
        """
        try:
            # AI评估
            ai_evaluation = self._ai_evaluate(user_response, question_data, context)
            
            # 基础评估
            basic_evaluation = self._basic_evaluate(user_response, question_data)
            
            # 综合评分
            final_score = self._calculate_final_score(ai_evaluation, basic_evaluation)
            
            return {
                'score': final_score,
                'ai_evaluation': ai_evaluation,
                'basic_metrics': basic_evaluation,
                'feedback': self._generate_feedback(ai_evaluation, basic_evaluation),
                'suggestions': self._generate_suggestions(ai_evaluation, basic_evaluation)
            }
            
        except Exception as e:
            print(f"评估出错: {e}")
            return self._fallback_evaluate(user_response, question_data)
    
    def _ai_evaluate(self, user_response: str, question_data: Dict, 
                    context: Dict) -> Dict:
        """AI智能评估"""
        try:
            prompt = f"""
你是一位资深的技术面试官，请评估候选人对技术问题的回答质量。

问题: {question_data.get('question', '')}
难度: {question_data.get('difficulty', 'B2')}
候选人回答: {user_response}

请从以下维度评估（0-1分）：
1. 技术准确性 (0-1): 回答的技术正确性
2. 深度理解 (0-1): 对技术原理的理解深度
3. 实践经验 (0-1): 是否体现实际项目经验
4. 表达清晰度 (0-1): 回答的逻辑性和清晰度

输出格式：
评分:
- 技术准确性: 0.X
- 深度理解: 0.X
- 实践经验: 0.X
- 表达清晰度: 0.X

反馈: [简短反馈，50字以内]
"""
            
            response = ollama.chat(
                model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_ai_evaluation(response['message']['content'])
            
        except Exception:
            return {}
    
    def _parse_ai_evaluation(self, evaluation_text: str) -> Dict:
        """解析AI评估结果"""
        result = {'scores': {}, 'feedback': ''}
        
        try:
            # 提取评分
            score_pattern = r'- (.*?): (0\.\d+)'
            scores = re.findall(score_pattern, evaluation_text)
            for dimension, score in scores:
                result['scores'][dimension.strip()] = float(score)
            
            # 提取反馈
            feedback_match = re.search(r'反馈[:：]\s*([^\n]+)', evaluation_text)
            if feedback_match:
                result['feedback'] = feedback_match.group(1).strip()
                
        except Exception:
            pass
        
        return result
    
    def _basic_evaluate(self, user_response: str, question_data: Dict) -> Dict:
        """基础评估"""
        response_length = len(user_response.strip())
        word_count = len(user_response.split())
        
        # 长度评分
        if response_length < 50:
            length_score = 0.3
        elif response_length < 200:
            length_score = 0.7
        elif response_length < 500:
            length_score = 1.0
        else:
            length_score = 0.9
        
        # 技术词汇评分
        tech_words = ['系统', '架构', '算法', '数据库', '网络', '安全', '优化', '设计']
        tech_count = sum(1 for word in tech_words if word in user_response)
        tech_score = min(tech_count / 3, 1.0)
        
        return {
            'length_score': length_score,
            'tech_score': tech_score,
            'response_length': response_length,
            'word_count': word_count
        }
    
    def _calculate_final_score(self, ai_evaluation: Dict, basic_evaluation: Dict) -> float:
        """计算最终评分"""
        if ai_evaluation and ai_evaluation.get('scores'):
            scores = list(ai_evaluation['scores'].values())
            ai_score = sum(scores) / len(scores) if scores else 0.5
            
            basic_score = (
                basic_evaluation['length_score'] * 0.4 +
                basic_evaluation['tech_score'] * 0.6
            )
            
            final_score = ai_score * 0.8 + basic_score * 0.2
        else:
            final_score = (
                basic_evaluation['length_score'] * 0.5 +
                basic_evaluation['tech_score'] * 0.5
            )
        
        return round(min(max(final_score, 0.0), 1.0), 2)
    
    def _generate_feedback(self, ai_evaluation: Dict, basic_evaluation: Dict) -> str:
        """生成反馈"""
        if ai_evaluation and ai_evaluation.get('feedback'):
            return ai_evaluation['feedback']
        
        feedback_parts = []
        if basic_evaluation['length_score'] > 0.7:
            feedback_parts.append("回答详细")
        if basic_evaluation['tech_score'] > 0.7:
            feedback_parts.append("技术术语使用恰当")
        
        return "，".join(feedback_parts) if feedback_parts else "回答已记录"
    
    def _generate_suggestions(self, ai_evaluation: Dict, basic_evaluation: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if basic_evaluation['length_score'] < 0.5:
            suggestions.append("建议提供更详细的技术说明")
        if basic_evaluation['tech_score'] < 0.5:
            suggestions.append("建议增加具体的技术实现细节")
        
        return suggestions
    
    def _fallback_evaluate(self, user_response: str, question_data: Dict) -> Dict:
        """备用评估"""
        response_length = len(user_response.strip())
        
        if response_length < 30:
            score = 0.3
        elif response_length < 100:
            score = 0.6
        elif response_length < 300:
            score = 0.8
        else:
            score = 0.85
        
        return {
            'score': score,
            'ai_evaluation': None,
            'basic_metrics': {'response_length': response_length},
            'feedback': "回答已记录",
            'suggestions': []
        }
