# -*- coding: utf-8 -*-
"""
第二阶段经历类问题评估器

负责评估经历类问题的回答质量，重点关注技术深度、
项目经验和实际能力的展现。
"""

import ollama
import re
from typing import Dict, List, Optional


class ExperienceEvaluator:
    """经历类问题评估器"""
    
    def __init__(self):
        self.evaluation_criteria = {
            "initial_experience_request": {
                "technical_depth": 0.3,      # 技术深度
                "project_complexity": 0.25,  # 项目复杂度
                "personal_contribution": 0.2, # 个人贡献
                "problem_solving": 0.15,     # 问题解决能力
                "communication": 0.1         # 表达清晰度
            },
            "deep_dive": {
                "technical_accuracy": 0.4,   # 技术准确性
                "detail_richness": 0.3,      # 细节丰富度
                "real_experience": 0.2,      # 真实经验体现
                "logical_thinking": 0.1      # 逻辑思维
            }
        }
    
    def evaluate_response(self, user_response: str, question_data: Dict, context: Dict) -> Dict:
        """
        评估用户回答
        
        Args:
            user_response: 用户回答
            question_data: 问题数据
            context: 上下文信息
            
        Returns:
            评估结果字典
        """
        question_type = question_data.get('question_type', 'general')
        
        try:
            # AI评估
            ai_evaluation = self._ai_evaluate(user_response, question_data, context)
            
            # 技术关键词分析
            tech_analysis = self._analyze_technical_content(user_response, context.get('technical_keywords', []))
            
            # 项目经验分析
            experience_analysis = self._analyze_project_experience(user_response, question_type)
            
            # 综合评分
            final_score = self._calculate_final_score(ai_evaluation, tech_analysis, experience_analysis, question_type)
            
            return {
                'score': final_score,
                'ai_evaluation': ai_evaluation,
                'technical_analysis': tech_analysis,
                'experience_analysis': experience_analysis,
                'question_type': question_type,
                'feedback': self._generate_feedback(ai_evaluation, tech_analysis, experience_analysis, question_type),
                'suggestions': self._generate_suggestions(ai_evaluation, tech_analysis, experience_analysis, question_type)
            }
            
        except Exception as e:
            print(f"评估过程出错: {e}")
            # 备用评估
            fallback_score = self._fallback_evaluate(user_response, question_type)
            return {
                'score': fallback_score,
                'ai_evaluation': None,
                'technical_analysis': None,
                'experience_analysis': None,
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
你是一位资深的技术面试官，正在评估候选人在第二阶段经历类问题的回答质量。

## 问题信息
问题类型: {question_type}
问题内容: {question_data.get('question', '')}

## 候选人回答
{user_response}

## 评估背景
"""
        
        if context.get('technical_keywords'):
            prompt += f"识别的技术关键词: {', '.join(context['technical_keywords'])}\n"
        
        if context.get('jd_data') and context['jd_data'].get('position'):
            prompt += f"目标职位: {context['jd_data']['position']}\n"
        
        prompt += """
## 评估标准
请从以下维度评估回答质量（每个维度0-1分）：

"""
        
        if question_type == "initial_experience_request":
            prompt += """
1. 技术深度 (0-1): 技术描述的深度和专业性
2. 项目复杂度 (0-1): 项目的技术复杂度和挑战性
3. 个人贡献 (0-1): 个人在项目中的具体贡献和角色
4. 问题解决能力 (0-1): 遇到问题时的分析和解决能力
5. 表达清晰度 (0-1): 表达是否清晰、逻辑性强
"""
        else:  # deep_dive
            prompt += """
1. 技术准确性 (0-1): 技术回答的准确性和专业性
2. 细节丰富度 (0-1): 回答中技术细节的丰富程度
3. 真实经验体现 (0-1): 是否体现出真实的项目经验
4. 逻辑思维 (0-1): 回答的逻辑性和条理性
"""
        
        prompt += """

## 特别关注点
- 技术实现的具体细节
- 数据和指标的准确性
- 架构设计的合理性
- 问题解决的思路和方法
- 团队协作和个人贡献

## 输出格式
请按以下格式输出评估结果：

评分:
- 维度1: 0.X
- 维度2: 0.X
- 维度3: 0.X
- 维度4: 0.X
- 维度5: 0.X (如果有)

技术亮点: [回答中的技术亮点，50字以内]

改进建议: [具体的改进建议，100字以内]

整体评价: [对回答的整体评价，80字以内]

请确保评分客观公正，重点关注技术能力和项目经验的真实性。
"""
        
        return prompt
    
    def _parse_ai_evaluation(self, evaluation_text: str) -> Dict:
        """解析AI评估结果"""
        result = {
            'scores': {},
            'technical_highlights': '',
            'improvement_suggestions': '',
            'overall_comment': ''
        }
        
        try:
            # 提取评分
            score_pattern = r'- (.*?): (0\.\d+)'
            scores = re.findall(score_pattern, evaluation_text)
            for dimension, score in scores:
                result['scores'][dimension.strip()] = float(score)
            
            # 提取技术亮点
            highlight_match = re.search(r'技术亮点[:：]\s*([^\n]+)', evaluation_text)
            if highlight_match:
                result['technical_highlights'] = highlight_match.group(1).strip()
            
            # 提取改进建议
            suggestion_match = re.search(r'改进建议[:：]\s*([^\n]+)', evaluation_text)
            if suggestion_match:
                result['improvement_suggestions'] = suggestion_match.group(1).strip()
            
            # 提取整体评价
            overall_match = re.search(r'整体评价[:：]\s*([^\n]+)', evaluation_text)
            if overall_match:
                result['overall_comment'] = overall_match.group(1).strip()
                
        except Exception as e:
            print(f"解析AI评估结果失败: {e}")
        
        return result
    
    def _analyze_technical_content(self, user_response: str, technical_keywords: List[str]) -> Dict:
        """分析技术内容"""
        response_lower = user_response.lower()
        
        # 技术关键词覆盖度
        mentioned_keywords = [kw for kw in technical_keywords if kw.lower() in response_lower]
        keyword_coverage = len(mentioned_keywords) / max(len(technical_keywords), 1)
        
        # 技术细节指标
        detail_indicators = [
            '具体', '实现', '优化', '性能', '架构', '设计', '算法', '数据结构',
            '并发', '分布式', '缓存', '数据库', '接口', 'API', '框架', '库'
        ]
        detail_count = sum(1 for indicator in detail_indicators if indicator in response_lower)
        detail_score = min(detail_count / 8, 1.0)
        
        # 数量指标（具体数字）
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?(?:%|万|千|亿|MB|GB|TB|ms|s|分钟|小时|天)?', user_response)
        number_score = min(len(numbers) / 5, 1.0)
        
        return {
            'keyword_coverage': keyword_coverage,
            'mentioned_keywords': mentioned_keywords,
            'detail_score': detail_score,
            'number_score': number_score,
            'technical_numbers': numbers[:10]  # 限制显示数量
        }
    
    def _analyze_project_experience(self, user_response: str, question_type: str) -> Dict:
        """分析项目经验"""
        response_length = len(user_response.strip())
        
        # 经验指标词
        experience_indicators = [
            '负责', '主导', '设计', '开发', '实现', '优化', '解决', '处理',
            '团队', '合作', '协调', '管理', '维护', '部署', '测试'
        ]
        
        experience_count = sum(1 for indicator in experience_indicators if indicator in user_response)
        experience_score = min(experience_count / 6, 1.0)
        
        # 项目规模指标
        scale_indicators = [
            '用户', '数据', '请求', '并发', '集群', '节点', '服务器',
            '万', '千', '亿', '千万', '百万'
        ]
        
        scale_count = sum(1 for indicator in scale_indicators if indicator in user_response)
        scale_score = min(scale_count / 3, 1.0)
        
        # 长度评分
        if question_type == "initial_experience_request":
            # 第一个问题期望更详细的回答
            if response_length < 200:
                length_score = 0.3
            elif response_length < 500:
                length_score = 0.7
            elif response_length < 1000:
                length_score = 1.0
            else:
                length_score = 0.9  # 过长扣分
        else:
            # 深挖问题可以相对简短但要有深度
            if response_length < 50:
                length_score = 0.2
            elif response_length < 200:
                length_score = 0.8
            elif response_length < 500:
                length_score = 1.0
            else:
                length_score = 0.9
        
        return {
            'experience_score': experience_score,
            'scale_score': scale_score,
            'length_score': length_score,
            'response_length': response_length
        }
    
    def _calculate_final_score(self, ai_evaluation: Dict, tech_analysis: Dict, 
                             experience_analysis: Dict, question_type: str) -> float:
        """计算最终评分"""
        scores = []
        
        # AI评估权重
        if ai_evaluation and ai_evaluation.get('scores'):
            ai_scores = list(ai_evaluation['scores'].values())
            ai_score = sum(ai_scores) / len(ai_scores) if ai_scores else 0.5
            scores.append(('ai', ai_score, 0.5))
        
        # 技术分析权重
        if tech_analysis:
            tech_score = (
                tech_analysis['keyword_coverage'] * 0.4 +
                tech_analysis['detail_score'] * 0.4 +
                tech_analysis['number_score'] * 0.2
            )
            scores.append(('tech', tech_score, 0.3))
        
        # 经验分析权重
        if experience_analysis:
            exp_score = (
                experience_analysis['experience_score'] * 0.4 +
                experience_analysis['scale_score'] * 0.3 +
                experience_analysis['length_score'] * 0.3
            )
            scores.append(('exp', exp_score, 0.2))
        
        if not scores:
            return 0.5
        
        # 加权计算
        total_weight = sum(weight for _, _, weight in scores)
        weighted_sum = sum(score * weight for _, score, weight in scores)
        
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        return round(min(max(final_score, 0.0), 1.0), 2)
    
    def _generate_feedback(self, ai_evaluation: Dict, tech_analysis: Dict, 
                         experience_analysis: Dict, question_type: str) -> str:
        """生成反馈"""
        feedback_parts = []
        
        # 优先使用AI评估的整体评价
        if ai_evaluation and ai_evaluation.get('overall_comment'):
            feedback_parts.append(ai_evaluation['overall_comment'])
        
        # 添加技术亮点
        if ai_evaluation and ai_evaluation.get('technical_highlights'):
            feedback_parts.append(f"技术亮点：{ai_evaluation['technical_highlights']}")
        
        # 基于分析添加反馈
        if tech_analysis:
            if tech_analysis['keyword_coverage'] > 0.7:
                feedback_parts.append("技术关键词覆盖度良好")
            elif tech_analysis['keyword_coverage'] < 0.3:
                feedback_parts.append("建议增加更多技术细节描述")
        
        if experience_analysis:
            if experience_analysis['experience_score'] > 0.7:
                feedback_parts.append("项目经验描述丰富")
            elif experience_analysis['response_length'] < 100:
                feedback_parts.append("回答可以更详细一些")
        
        return "；".join(feedback_parts) if feedback_parts else "回答已记录"
    
    def _generate_suggestions(self, ai_evaluation: Dict, tech_analysis: Dict, 
                            experience_analysis: Dict, question_type: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 使用AI评估的建议
        if ai_evaluation and ai_evaluation.get('improvement_suggestions'):
            suggestions.append(ai_evaluation['improvement_suggestions'])
        
        # 基于技术分析的建议
        if tech_analysis:
            if tech_analysis['detail_score'] < 0.5:
                suggestions.append("建议增加技术实现的具体细节描述")
            if tech_analysis['number_score'] < 0.3:
                suggestions.append("建议提供具体的数据指标和量化结果")
        
        # 基于经验分析的建议
        if experience_analysis:
            if experience_analysis['experience_score'] < 0.5:
                suggestions.append("建议突出个人在项目中的具体贡献和角色")
            if experience_analysis['scale_score'] < 0.3:
                suggestions.append("建议描述项目的规模和影响范围")
        
        return suggestions
    
    def _fallback_evaluate(self, user_response: str, question_type: str) -> float:
        """备用评估方法"""
        response_length = len(user_response.strip())
        
        if question_type == "initial_experience_request":
            # 第一个问题重视详细程度
            if response_length < 100:
                return 0.3
            elif response_length < 300:
                return 0.6
            elif response_length < 600:
                return 0.8
            else:
                return 0.85
        else:
            # 深挖问题重视深度
            if response_length < 50:
                return 0.2
            elif response_length < 150:
                return 0.6
            elif response_length < 300:
                return 0.8
            else:
                return 0.85
