# -*- coding: utf-8 -*-
"""
技术问题库管理器

管理技术类问题的获取、筛选和生成，支持B1/B2/B3难度级别。
"""

import pandas as pd
import random
import ollama
from typing import Dict, List, Optional


class TechnicalQuestionBank:
    """技术问题库管理器"""
    
    def __init__(self):
        self.question_pool = self._load_question_pool()
        self.used_questions = set()
    
    def _load_question_pool(self):
        """加载问题池"""
        try:
            df = pd.read_csv('Data/data.csv', encoding='utf-8')
            question_pool = {'B1': [], 'B2': [], 'B3': []}
            
            for _, row in df.iterrows():
                level = row['建议等级']
                if level in question_pool:
                    question_data = {
                        'question': row['问题（GPT风格，合成）'],
                        'position': row['岗位'],
                        'capability': row['能力项'],
                        'level': level,
                        'id': f"{level}_{len(question_pool[level])}"
                    }
                    question_pool[level].append(question_data)
            
            return question_pool
        except Exception as e:
            print(f"加载题库失败: {e}")
            return {'B1': [], 'B2': [], 'B3': []}
    
    def get_question(self, difficulty: str, jd_data: Dict = None, 
                    asked_questions: List = None, question_number: int = 1,
                    total_questions: int = 3) -> Dict:
        """获取指定难度的技术问题"""
        
        # 尝试从题库选择
        pool_question = self._select_from_pool(difficulty, jd_data, asked_questions)
        if pool_question:
            return {
                **pool_question,
                'question_number': question_number,
                'total_questions': total_questions,
                'stage': '第三阶段：技术类问题'
            }
        
        # 备用：生成简单问题
        fallback_question = self._get_fallback_question(difficulty)
        return {
            'question': fallback_question,
            'difficulty': difficulty,
            'question_type': 'technical',
            'source': 'fallback',
            'question_number': question_number,
            'total_questions': total_questions,
            'stage': '第三阶段：技术类问题',
            'category': '技术能力'
        }
    
    def _select_from_pool(self, difficulty: str, jd_data: Dict = None, 
                         asked_questions: List = None) -> Optional[Dict]:
        """从题库中选择问题"""
        available_questions = [
            q for q in self.question_pool.get(difficulty, [])
            if q['id'] not in self.used_questions
        ]
        
        if not available_questions:
            return None
        
        selected = random.choice(available_questions)
        self.used_questions.add(selected['id'])
        
        return {
            'question': selected['question'],
            'difficulty': difficulty,
            'question_type': 'technical',
            'source': 'question_pool',
            'category': selected['capability'],
            'position_type': selected['position']
        }
    
    def _get_fallback_question(self, difficulty: str) -> str:
        """获取备用问题"""
        fallback_questions = {
            'B1': [
                "请简单介绍一下面向对象编程的基本概念。",
                "什么是数据库索引？它有什么作用？",
                "请解释HTTP和HTTPS的区别。"
            ],
            'B2': [
                "请描述一个你熟悉的设计模式及其应用场景。",
                "如何优化数据库查询性能？",
                "请设计一个简单的缓存策略。"
            ],
            'B3': [
                "请设计一个高并发的分布式系统架构。",
                "如何解决分布式系统的一致性问题？",
                "请描述微服务架构的优缺点和实施策略。"
            ]
        }
        
        questions = fallback_questions.get(difficulty, fallback_questions['B2'])
        return random.choice(questions)
