# -*- coding: utf-8 -*-
"""
第一阶段：非技术问题模块

这个模块负责AI面试系统的第一阶段，主要考察候选人的基本情况、
沟通能力、职业规划和对公司岗位的了解。

主要功能：
- 自我介绍类问题生成
- 职业发展规划询问
- 公司岗位了解评估
- 基本工作态度和价值观考察
"""

from .non_technical_engine import NonTechnicalQuestionEngine
from .question_generator import NonTechnicalQuestionGenerator
from .evaluator import NonTechnicalEvaluator

__all__ = [
    'NonTechnicalQuestionEngine',
    'NonTechnicalQuestionGenerator', 
    'NonTechnicalEvaluator'
]
