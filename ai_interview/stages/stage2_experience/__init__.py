# -*- coding: utf-8 -*-
"""
第二阶段：经历类问题模块

这个模块负责AI面试系统的第二阶段，深入挖掘候选人的项目经历和工作经验。
基于case.docx的专业深挖提问方式，实现技术经历的深度探索。

主要功能：
- 经历介绍请求（第一个问题固定）
- 基于case.docx的深挖追问方式
- 技术关键词提取和分析
- 专业的经历评估和反馈
"""

from .experience_engine import ExperienceQuestionEngine
from .deep_dive_generator import DeepDiveQuestionGenerator
from .experience_evaluator import ExperienceEvaluator
from .case_prompts import CaseBasedPrompts

__all__ = [
    'ExperienceQuestionEngine',
    'DeepDiveQuestionGenerator',
    'ExperienceEvaluator',
    'CaseBasedPrompts'
]
