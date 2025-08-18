# -*- coding: utf-8 -*-
"""
第一阶段非技术问题引擎

负责生成和管理非技术类面试问题，包括自我介绍、职业规划、
公司岗位了解等方面的问题。
"""

import random
from typing import Dict, List, Optional
from .question_generator import NonTechnicalQuestionGenerator
from .evaluator import NonTechnicalEvaluator


class NonTechnicalQuestionEngine:
    """
    第一阶段非技术问题引擎
    
    负责管理非技术问题的生成、评估和进度跟踪
    """
    
    def __init__(self):
        self.question_generator = NonTechnicalQuestionGenerator()
        self.evaluator = NonTechnicalEvaluator()
        
        # 问题类型和顺序
        self.question_types = [
            "self_introduction",    # 自我介绍
            "career_planning",      # 职业规划
            "company_position",     # 公司岗位了解
            "work_attitude"         # 工作态度
        ]
        
        # 状态跟踪
        self.current_question_index = 0
        self.max_questions = 2  # 第一阶段默认2题
        self.asked_questions = []
        self.question_responses = []
        self.question_scores = []
        
    def start_stage(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """
        开始第一阶段面试
        
        Args:
            resume_data: 简历数据
            jd_data: 职位描述数据
            
        Returns:
            第一个问题的数据
        """
        self.resume_data = resume_data
        self.jd_data = jd_data
        
        # 重置状态
        self.current_question_index = 0
        self.asked_questions.clear()
        self.question_responses.clear()
        self.question_scores.clear()
        
        # 生成第一个问题
        return self.generate_next_question()
    
    def generate_next_question(self) -> Dict:
        """
        生成下一个问题
        
        Returns:
            问题数据字典
        """
        if self.current_question_index >= self.max_questions:
            return {
                'question': None,
                'stage_completed': True,
                'message': '第一阶段非技术问题已完成'
            }
        
        # 选择问题类型
        question_type = self.question_types[self.current_question_index % len(self.question_types)]
        
        # 生成问题
        question_data = self.question_generator.generate_question(
            question_type=question_type,
            resume_data=self.resume_data,
            jd_data=self.jd_data,
            previous_questions=self.asked_questions
        )
        
        # 更新状态
        question_data['question_number'] = self.current_question_index + 1
        question_data['total_questions'] = self.max_questions
        question_data['stage'] = '第一阶段：非技术问题'
        
        self.asked_questions.append(question_data)
        self.current_question_index += 1
        
        return question_data
    
    def process_answer(self, user_response: str, question_data: Dict) -> Dict:
        """
        处理用户回答
        
        Args:
            user_response: 用户的回答
            question_data: 当前问题的数据
            
        Returns:
            评估结果
        """
        # 记录回答
        self.question_responses.append({
            'question': question_data['question'],
            'response': user_response,
            'question_type': question_data['question_type'],
            'question_number': question_data['question_number']
        })
        
        # 评估回答
        evaluation = self.evaluator.evaluate_response(
            user_response=user_response,
            question_data=question_data,
            context={
                'resume_data': self.resume_data,
                'jd_data': self.jd_data
            }
        )
        
        # 记录评分
        self.question_scores.append(evaluation['score'])
        
        return evaluation
    
    def should_continue(self) -> bool:
        """检查是否应该继续提问"""
        return self.current_question_index < self.max_questions
    
    def get_stage_summary(self) -> Dict:
        """
        获取第一阶段总结
        
        Returns:
            阶段总结数据
        """
        if not self.question_scores:
            average_score = 0
        else:
            average_score = sum(self.question_scores) / len(self.question_scores)
        
        return {
            'stage_name': '第一阶段：非技术问题',
            'questions_asked': len(self.asked_questions),
            'total_questions': self.max_questions,
            'average_score': round(average_score, 2),
            'question_responses': self.question_responses,
            'detailed_scores': self.question_scores,
            'stage_completed': self.current_question_index >= self.max_questions,
            'next_stage': '第二阶段：经历类问题' if self.current_question_index >= self.max_questions else None
        }
    
    def get_progress_info(self) -> Dict:
        """获取当前进度信息"""
        return {
            'current_question': self.current_question_index,
            'total_questions': self.max_questions,
            'progress_percentage': (self.current_question_index / self.max_questions) * 100,
            'remaining_questions': self.max_questions - self.current_question_index
        }
    
    def reset(self):
        """重置引擎状态"""
        self.current_question_index = 0
        self.asked_questions.clear()
        self.question_responses.clear()
        self.question_scores.clear()
        self.resume_data = None
        self.jd_data = None
