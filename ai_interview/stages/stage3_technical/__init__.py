# -*- coding: utf-8 -*-
"""
第三阶段：技术类问题模块

这个模块负责AI面试系统的第三阶段，专注于评估候选人的专业技术能力。
实现了B1 < B2 < B3的动态难度调整系统，根据回答质量实时调整问题难度。

主要功能：
- B1/B2/B3三级难度系统
- 基于回答质量的动态难度调整
- 结合JD要求的个性化技术问题
- 智能评分和详细反馈
- 完整的难度调整轨迹记录
"""

from .technical_engine import TechnicalQuestionEngine
from .adaptive_difficulty import AdaptiveDifficultyManager
from .question_bank import TechnicalQuestionBank
from .technical_evaluator import TechnicalEvaluator

__all__ = [
    'TechnicalQuestionEngine',
    'AdaptiveDifficultyManager',
    'TechnicalQuestionBank',
    'TechnicalEvaluator'
]
