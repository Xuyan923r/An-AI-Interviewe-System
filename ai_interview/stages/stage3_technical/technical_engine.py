# -*- coding: utf-8 -*-
"""
第三阶段技术类问题引擎

负责管理技术类问题的完整流程，实现B1 < B2 < B3的动态难度调整系统。
根据用户回答质量实时调整问题难度，提供个性化的技术能力评估。
"""

from typing import Dict, List, Optional
from .adaptive_difficulty import AdaptiveDifficultyManager
from .question_bank import TechnicalQuestionBank
from .technical_evaluator import TechnicalEvaluator


class TechnicalQuestionEngine:
    """
    第三阶段技术类问题引擎
    
    实现B1 < B2 < B3动态难度调整系统
    """
    
    def __init__(self):
        self.difficulty_manager = AdaptiveDifficultyManager()
        self.question_bank = TechnicalQuestionBank()
        self.evaluator = TechnicalEvaluator()
        
        # 状态跟踪
        self.current_question_index = 0
        self.max_questions = 3  # 第三阶段默认3题
        self.stage_started = False
        
        # 问答记录
        self.asked_questions = []
        self.question_responses = []
        self.question_scores = []
        self.difficulty_progression = []
        
    def start_stage(self, jd_data: Dict, resume_data: Dict = None, 
                   stage2_summary: Dict = None) -> Dict:
        """
        开始第三阶段面试
        
        Args:
            jd_data: 职位描述数据
            resume_data: 简历数据
            stage2_summary: 第二阶段总结（用于调整难度和题数）
            
        Returns:
            第一个技术问题
        """
        self.jd_data = jd_data
        self.resume_data = resume_data
        
        # 重置状态
        self.current_question_index = 0
        self.stage_started = True
        self.asked_questions.clear()
        self.question_responses.clear()
        self.question_scores.clear()
        self.difficulty_progression.clear()
        
        # 根据第二阶段表现调整题数和初始难度
        self._adjust_based_on_stage2(stage2_summary)
        
        # 生成第一个技术问题
        return self.generate_next_question()
    
    def generate_next_question(self) -> Dict:
        """
        生成下一个技术问题
        
        Returns:
            技术问题数据
        """
        if self.current_question_index >= self.max_questions:
            return {
                'question': None,
                'stage_completed': True,
                'message': '第三阶段技术类问题已完成',
                'final_summary': self.get_stage_summary()
            }
        
        # 获取当前难度级别
        current_difficulty = self.difficulty_manager.get_current_difficulty()
        
        # 从题库选择问题或AI生成
        question_data = self.question_bank.get_question(
            difficulty=current_difficulty,
            jd_data=self.jd_data,
            asked_questions=self.asked_questions,
            question_number=self.current_question_index + 1,
            total_questions=self.max_questions
        )
        
        # 记录难度信息
        self.difficulty_progression.append({
            'question_number': self.current_question_index + 1,
            'difficulty': current_difficulty,
            'difficulty_analysis': self.difficulty_manager.get_difficulty_analysis()
        })
        
        self.asked_questions.append(question_data)
        self.current_question_index += 1
        
        return question_data
    
    def process_answer(self, user_response: str, question_data: Dict) -> Dict:
        """
        处理用户回答并动态调整难度
        
        Args:
            user_response: 用户回答
            question_data: 当前问题数据
            
        Returns:
            评估结果和难度调整信息
        """
        # 记录回答
        self.question_responses.append({
            'question': question_data['question'],
            'response': user_response,
            'difficulty': question_data.get('difficulty', 'B2'),
            'question_number': question_data['question_number']
        })
        
        # 评估回答
        evaluation = self.evaluator.evaluate_response(
            user_response=user_response,
            question_data=question_data,
            context={
                'jd_data': self.jd_data,
                'resume_data': self.resume_data,
                'current_difficulty': question_data.get('difficulty', 'B2')
            }
        )
        
        # 记录评分
        self.question_scores.append(evaluation['score'])
        
        # 动态调整难度
        difficulty_adjustment = self.difficulty_manager.adjust_difficulty(
            score=evaluation['score'],
            question_context=question_data,
            response_analysis=evaluation
        )
        
        # 更新评估结果，包含难度调整信息
        evaluation.update({
            'difficulty_adjustment': difficulty_adjustment,
            'next_difficulty': self.difficulty_manager.get_current_difficulty()
        })
        
        return evaluation
    
    def should_continue(self) -> bool:
        """检查是否应该继续提问"""
        return self.current_question_index < self.max_questions
    
    def get_stage_summary(self) -> Dict:
        """
        获取第三阶段总结
        
        Returns:
            阶段总结数据
        """
        if not self.question_scores:
            average_score = 0
        else:
            average_score = sum(self.question_scores) / len(self.question_scores)
        
        # 难度分布统计
        difficulty_stats = {}
        for record in self.difficulty_progression:
            diff = record['difficulty']
            difficulty_stats[diff] = difficulty_stats.get(diff, 0) + 1
        
        return {
            'stage_name': '第三阶段：技术类问题',
            'questions_asked': len(self.asked_questions),
            'total_questions': self.max_questions,
            'average_score': round(average_score, 2),
            'question_responses': self.question_responses,
            'detailed_scores': self.question_scores,
            'difficulty_progression': self.difficulty_progression,
            'difficulty_distribution': difficulty_stats,
            'final_difficulty': self.difficulty_manager.get_current_difficulty(),
            'stage_completed': self.current_question_index >= self.max_questions,
            'technical_assessment': self._generate_technical_assessment()
        }
    
    def get_progress_info(self) -> Dict:
        """获取当前进度信息"""
        return {
            'current_question': self.current_question_index,
            'total_questions': self.max_questions,
            'progress_percentage': (self.current_question_index / self.max_questions) * 100,
            'remaining_questions': self.max_questions - self.current_question_index,
            'current_difficulty': self.difficulty_manager.get_current_difficulty(),
            'difficulty_trend': self._get_difficulty_trend()
        }
    
    def _adjust_based_on_stage2(self, stage2_summary: Dict):
        """根据第二阶段表现调整第三阶段配置"""
        if not stage2_summary:
            return
        
        stage2_avg_score = stage2_summary.get('average_score', 0.6)
        
        # 根据第二阶段表现调整题数
        if stage2_avg_score >= 0.75:
            # 表现优秀，增加技术问题数量
            self.max_questions = min(5, self.max_questions + 1)
            # 提高初始难度
            self.difficulty_manager.set_initial_difficulty('B2')
        elif stage2_avg_score < 0.5:
            # 表现不佳，减少技术问题，降低初始难度
            self.max_questions = max(2, self.max_questions - 1)
            self.difficulty_manager.set_initial_difficulty('B1')
        else:
            # 表现一般，保持默认配置
            self.difficulty_manager.set_initial_difficulty('B2')
    
    def _generate_technical_assessment(self) -> Dict:
        """生成技术能力评估"""
        if not self.question_scores:
            return {'overall_level': '无法评估', 'recommendations': []}
        
        avg_score = sum(self.question_scores) / len(self.question_scores)
        final_difficulty = self.difficulty_manager.get_current_difficulty()
        
        # 综合评估技术水平
        if avg_score >= 0.8 and final_difficulty == 'B3':
            level = '高级'
            recommendations = ['适合高级技术岗位', '可以承担架构设计工作', '技术深度和广度都很不错']
        elif avg_score >= 0.7 and final_difficulty in ['B2', 'B3']:
            level = '中高级'
            recommendations = ['适合中高级技术岗位', '技术能力较强', '建议继续深化某个专业方向']
        elif avg_score >= 0.6:
            level = '中级'
            recommendations = ['适合中级技术岗位', '基础扎实', '建议加强实战项目经验']
        elif avg_score >= 0.4:
            level = '初中级'
            recommendations = ['适合初中级技术岗位', '需要加强技术深度', '建议多做实际项目练习']
        else:
            level = '初级'
            recommendations = ['适合初级技术岗位', '需要系统学习基础知识', '建议先从简单项目开始']
        
        return {
            'overall_level': level,
            'average_score': round(avg_score, 2),
            'final_difficulty': final_difficulty,
            'recommendations': recommendations,
            'technical_strengths': self._analyze_technical_strengths(),
            'improvement_areas': self._analyze_improvement_areas()
        }
    
    def _analyze_technical_strengths(self) -> List[str]:
        """分析技术优势"""
        strengths = []
        
        if self.question_scores:
            high_scores = [i for i, score in enumerate(self.question_scores) if score >= 0.75]
            for i in high_scores:
                if i < len(self.asked_questions):
                    question = self.asked_questions[i]
                    if 'category' in question:
                        strengths.append(f"{question['category']}方面表现优秀")
        
        return strengths[:3]  # 限制数量
    
    def _analyze_improvement_areas(self) -> List[str]:
        """分析需要改进的领域"""
        improvements = []
        
        if self.question_scores:
            low_scores = [i for i, score in enumerate(self.question_scores) if score < 0.5]
            for i in low_scores:
                if i < len(self.asked_questions):
                    question = self.asked_questions[i]
                    if 'category' in question:
                        improvements.append(f"{question['category']}方面需要加强")
        
        return improvements[:3]  # 限制数量
    
    def _get_difficulty_trend(self) -> str:
        """获取难度变化趋势"""
        if len(self.difficulty_progression) < 2:
            return "稳定"
        
        difficulties = [record['difficulty'] for record in self.difficulty_progression]
        difficulty_levels = {'B1': 1, 'B2': 2, 'B3': 3}
        
        levels = [difficulty_levels[d] for d in difficulties]
        
        if levels[-1] > levels[0]:
            return "上升"
        elif levels[-1] < levels[0]:
            return "下降"
        else:
            return "稳定"
    
    def reset(self):
        """重置引擎状态"""
        self.current_question_index = 0
        self.stage_started = False
        self.asked_questions.clear()
        self.question_responses.clear()
        self.question_scores.clear()
        self.difficulty_progression.clear()
        self.difficulty_manager.reset()
        self.jd_data = None
        self.resume_data = None
