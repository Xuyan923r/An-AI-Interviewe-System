# -*- coding: utf-8 -*-
"""
集成面试管理器

统一管理三个阶段的面试流程，提供简洁的接口和完整的面试体验。
整合了所有阶段的功能，支持流程控制、数据传递和综合评估。
"""

from typing import Dict, List, Optional, Tuple
from .stage1_non_technical import NonTechnicalQuestionEngine
from .stage2_experience import ExperienceQuestionEngine
from .stage3_technical import TechnicalQuestionEngine


class IntegratedInterviewManager:
    """
    集成面试管理器
    
    统一管理三阶段面试流程，提供完整的面试体验
    """
    
    def __init__(self):
        # 初始化三个阶段的引擎
        self.stage1_engine = NonTechnicalQuestionEngine()
        self.stage2_engine = ExperienceQuestionEngine()
        self.stage3_engine = TechnicalQuestionEngine()
        
        # 当前状态
        self.current_stage = 0  # 0: 未开始, 1-3: 对应三个阶段, 4: 完成
        self.stage_names = [
            "面试准备",
            "第一阶段：非技术问题", 
            "第二阶段：经历类问题",
            "第三阶段：技术类问题",
            "面试完成"
        ]
        
        # 面试数据
        self.resume_data = None
        self.jd_data = None
        self.stage_summaries = {}
        self.overall_scores = []
        
    def start_interview(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """
        开始完整的三阶段面试
        
        Args:
            resume_data: 简历数据
            jd_data: 职位描述数据
            
        Returns:
            第一阶段的第一个问题
        """
        self.resume_data = resume_data
        self.jd_data = jd_data
        self.current_stage = 1
        
        # 重置所有状态
        self.stage_summaries.clear()
        self.overall_scores.clear()
        
        # 开始第一阶段
        first_question = self.stage1_engine.start_stage(resume_data, jd_data)
        
        return {
            **first_question,
            'interview_progress': self.get_progress_info(),
            'stage_info': self.get_current_stage_info()
        }
    
    def process_answer_and_get_next_question(self, user_response: str, 
                                           current_question: Dict) -> Dict:
        """
        处理当前回答并获取下一个问题
        
        Args:
            user_response: 用户回答
            current_question: 当前问题数据
            
        Returns:
            下一个问题或阶段转换信息
        """
        # 根据当前阶段处理回答
        if self.current_stage == 1:
            return self._handle_stage1_answer(user_response, current_question)
        elif self.current_stage == 2:
            return self._handle_stage2_answer(user_response, current_question)
        elif self.current_stage == 3:
            return self._handle_stage3_answer(user_response, current_question)
        else:
            return {
                'error': '面试状态异常',
                'current_stage': self.current_stage
            }
    
    def _handle_stage1_answer(self, user_response: str, current_question: Dict) -> Dict:
        """处理第一阶段回答"""
        # 评估回答
        evaluation = self.stage1_engine.process_answer(user_response, current_question)
        
        # 检查是否继续第一阶段
        if self.stage1_engine.should_continue():
            # 生成下一个第一阶段问题
            next_question = self.stage1_engine.generate_next_question()
            return {
                **next_question,
                'evaluation': evaluation,
                'interview_progress': self.get_progress_info(),
                'stage_info': self.get_current_stage_info()
            }
        else:
            # 第一阶段结束，准备进入第二阶段
            stage1_summary = self.stage1_engine.get_stage_summary()
            self.stage_summaries['stage1'] = stage1_summary
            self.overall_scores.extend(stage1_summary['detailed_scores'])
            
            # 进入第二阶段
            self.current_stage = 2
            stage2_first_question = self.stage2_engine.start_stage(self.resume_data, self.jd_data)
            
            return {
                **stage2_first_question,
                'evaluation': evaluation,
                'stage_transition': {
                    'from_stage': 1,
                    'to_stage': 2,
                    'stage1_summary': stage1_summary
                },
                'interview_progress': self.get_progress_info(),
                'stage_info': self.get_current_stage_info()
            }
    
    def _handle_stage2_answer(self, user_response: str, current_question: Dict) -> Dict:
        """处理第二阶段回答"""
        # 评估回答
        evaluation = self.stage2_engine.process_answer(user_response, current_question)
        
        # 检查是否继续第二阶段
        if self.stage2_engine.should_continue():
            # 生成深挖追问
            if current_question.get('question_type') == 'initial_experience_request':
                # 第一个问题的回答，生成深挖追问
                next_question = self.stage2_engine.generate_follow_up_question(user_response)
            else:
                # 后续追问的回答，继续深挖
                next_question = self.stage2_engine.generate_follow_up_question(user_response)
            
            return {
                **next_question,
                'evaluation': evaluation,
                'interview_progress': self.get_progress_info(),
                'stage_info': self.get_current_stage_info()
            }
        else:
            # 第二阶段结束，准备进入第三阶段
            stage2_summary = self.stage2_engine.get_stage_summary()
            self.stage_summaries['stage2'] = stage2_summary
            self.overall_scores.extend(stage2_summary['detailed_scores'])
            
            # 进入第三阶段
            self.current_stage = 3
            stage3_first_question = self.stage3_engine.start_stage(
                jd_data=self.jd_data,
                resume_data=self.resume_data,
                stage2_summary=stage2_summary
            )
            
            return {
                **stage3_first_question,
                'evaluation': evaluation,
                'stage_transition': {
                    'from_stage': 2,
                    'to_stage': 3,
                    'stage2_summary': stage2_summary
                },
                'interview_progress': self.get_progress_info(),
                'stage_info': self.get_current_stage_info()
            }
    
    def _handle_stage3_answer(self, user_response: str, current_question: Dict) -> Dict:
        """处理第三阶段回答"""
        # 评估回答并调整难度
        evaluation = self.stage3_engine.process_answer(user_response, current_question)
        
        # 检查是否继续第三阶段
        if self.stage3_engine.should_continue():
            # 生成下一个技术问题（可能调整了难度）
            next_question = self.stage3_engine.generate_next_question()
            return {
                **next_question,
                'evaluation': evaluation,
                'interview_progress': self.get_progress_info(),
                'stage_info': self.get_current_stage_info()
            }
        else:
            # 第三阶段结束，面试完成
            stage3_summary = self.stage3_engine.get_stage_summary()
            self.stage_summaries['stage3'] = stage3_summary
            self.overall_scores.extend(stage3_summary['detailed_scores'])
            
            # 面试完成
            self.current_stage = 4
            final_assessment = self.generate_final_assessment()
            
            return {
                'interview_completed': True,
                'evaluation': evaluation,
                'stage3_summary': stage3_summary,
                'final_assessment': final_assessment,
                'interview_progress': self.get_progress_info(),
                'stage_info': self.get_current_stage_info()
            }
    
    def get_progress_info(self) -> Dict:
        """获取面试进度信息"""
        total_stages = 3
        
        if self.current_stage == 0:
            progress_percentage = 0
        elif self.current_stage <= 3:
            # 计算当前阶段内部进度
            if self.current_stage == 1:
                stage_progress = self.stage1_engine.get_progress_info()
            elif self.current_stage == 2:
                stage_progress = self.stage2_engine.get_progress_info()
            elif self.current_stage == 3:
                stage_progress = self.stage3_engine.get_progress_info()
            
            # 总进度 = (已完成阶段 + 当前阶段进度) / 总阶段数
            completed_stages = self.current_stage - 1
            current_stage_progress = stage_progress['progress_percentage'] / 100
            progress_percentage = (completed_stages + current_stage_progress) / total_stages * 100
        else:
            progress_percentage = 100
        
        return {
            'current_stage': self.current_stage,
            'total_stages': total_stages,
            'current_stage_name': self.stage_names[self.current_stage],
            'progress_percentage': round(progress_percentage, 1),
            'completed_stages': max(0, self.current_stage - 1),
            'is_completed': self.current_stage >= 4
        }
    
    def get_current_stage_info(self) -> Dict:
        """获取当前阶段详细信息"""
        if self.current_stage == 1:
            return {
                'stage_number': 1,
                'stage_name': '非技术问题',
                'description': '考察基本情况、沟通能力和职业规划',
                'progress': self.stage1_engine.get_progress_info()
            }
        elif self.current_stage == 2:
            return {
                'stage_number': 2,
                'stage_name': '经历类问题',
                'description': '深挖项目经历和技术实现',
                'progress': self.stage2_engine.get_progress_info()
            }
        elif self.current_stage == 3:
            return {
                'stage_number': 3,
                'stage_name': '技术类问题',
                'description': 'B1 < B2 < B3动态难度调整技术评估',
                'progress': self.stage3_engine.get_progress_info()
            }
        else:
            return {
                'stage_number': self.current_stage,
                'stage_name': self.stage_names[self.current_stage],
                'description': '面试流程控制状态',
                'progress': {'message': '无进度信息'}
            }
    
    def generate_final_assessment(self) -> Dict:
        """生成最终评估报告"""
        if not self.overall_scores:
            return {'error': '无评分数据'}
        
        overall_average = sum(self.overall_scores) / len(self.overall_scores)
        
        # 各阶段表现分析
        stage_performance = {}
        for stage_name, summary in self.stage_summaries.items():
            stage_performance[stage_name] = {
                'average_score': summary.get('average_score', 0),
                'questions_count': summary.get('questions_asked', 0),
                'stage_completed': summary.get('stage_completed', False)
            }
        
        # 综合评级
        if overall_average >= 0.8:
            overall_rating = '优秀'
            recommendation = '强烈推荐录用，技术能力和综合素质都很出色'
        elif overall_average >= 0.7:
            overall_rating = '良好'
            recommendation = '推荐录用，具备良好的技术能力和发展潜力'
        elif overall_average >= 0.6:
            overall_rating = '一般'
            recommendation = '可以考虑录用，需要加强技术深度和实践经验'
        elif overall_average >= 0.5:
            overall_rating = '待提升'
            recommendation = '暂不推荐，建议候选人提升技术能力后再申请'
        else:
            overall_rating = '不合格'
            recommendation = '不推荐录用，技术能力与岗位要求差距较大'
        
        # 技术能力评估（从第三阶段获取）
        technical_assessment = {}
        if 'stage3' in self.stage_summaries:
            technical_assessment = self.stage_summaries['stage3'].get('technical_assessment', {})
        
        return {
            'overall_score': round(overall_average, 2),
            'overall_rating': overall_rating,
            'recommendation': recommendation,
            'stage_performance': stage_performance,
            'technical_assessment': technical_assessment,
            'total_questions': len(self.overall_scores),
            'interview_duration_stages': len(self.stage_summaries),
            'strengths': self._identify_strengths(),
            'improvement_areas': self._identify_improvement_areas()
        }
    
    def _identify_strengths(self) -> List[str]:
        """识别候选人优势"""
        strengths = []
        
        # 分析各阶段表现
        for stage_name, summary in self.stage_summaries.items():
            avg_score = summary.get('average_score', 0)
            if avg_score >= 0.75:
                if stage_name == 'stage1':
                    strengths.append('沟通表达能力强，职业规划清晰')
                elif stage_name == 'stage2':
                    strengths.append('项目经验丰富，技术实现能力强')
                elif stage_name == 'stage3':
                    strengths.append('技术能力扎实，理论基础深厚')
        
        # 从第三阶段获取具体技术优势
        if 'stage3' in self.stage_summaries:
            tech_strengths = self.stage_summaries['stage3'].get('technical_assessment', {}).get('technical_strengths', [])
            strengths.extend(tech_strengths)
        
        return strengths[:5]  # 限制数量
    
    def _identify_improvement_areas(self) -> List[str]:
        """识别需要改进的领域"""
        improvements = []
        
        # 分析各阶段表现
        for stage_name, summary in self.stage_summaries.items():
            avg_score = summary.get('average_score', 0)
            if avg_score < 0.6:
                if stage_name == 'stage1':
                    improvements.append('建议加强沟通表达和职业规划能力')
                elif stage_name == 'stage2':
                    improvements.append('建议积累更多实际项目经验')
                elif stage_name == 'stage3':
                    improvements.append('建议深化技术理论学习和实践')
        
        # 从第三阶段获取具体改进建议
        if 'stage3' in self.stage_summaries:
            tech_improvements = self.stage_summaries['stage3'].get('technical_assessment', {}).get('improvement_areas', [])
            improvements.extend(tech_improvements)
        
        return improvements[:5]  # 限制数量
    
    def get_complete_interview_data(self) -> Dict:
        """获取完整的面试数据"""
        return {
            'interview_metadata': {
                'current_stage': self.current_stage,
                'total_questions': len(self.overall_scores),
                'overall_average_score': sum(self.overall_scores) / len(self.overall_scores) if self.overall_scores else 0
            },
            'candidate_data': {
                'resume_data': self.resume_data,
                'jd_data': self.jd_data
            },
            'stage_summaries': self.stage_summaries,
            'final_assessment': self.generate_final_assessment() if self.current_stage >= 4 else None,
            'progress_info': self.get_progress_info()
        }
    
    def reset_interview(self):
        """重置面试状态"""
        self.current_stage = 0
        self.resume_data = None
        self.jd_data = None
        self.stage_summaries.clear()
        self.overall_scores.clear()
        
        # 重置各阶段引擎
        self.stage1_engine.reset()
        self.stage2_engine.reset()
        self.stage3_engine.reset()
