# -*- coding: utf-8 -*-
"""
AI面试系统三阶段模块包

这个包包含了完整的三阶段面试系统：
- 第一阶段：非技术问题 (自我介绍、职业规划、公司岗位了解、工作态度)
- 第二阶段：经历类问题 (项目经历深挖，基于case.docx的专业提问方式)
- 第三阶段：技术类问题 (B1 < B2 < B3动态难度调整系统)

每个阶段都是独立的模块，具备完整的功能实现。
"""

from .stage1_non_technical import NonTechnicalQuestionEngine
from .stage2_experience import ExperienceQuestionEngine  
from .stage3_technical import TechnicalQuestionEngine
from .integrated_interview import IntegratedInterviewManager

__all__ = [
    'NonTechnicalQuestionEngine',
    'ExperienceQuestionEngine', 
    'TechnicalQuestionEngine',
    'IntegratedInterviewManager'
]
