# -*- coding: utf-8 -*-
"""
第二阶段经历类问题引擎

负责管理经历类问题的完整流程，包括第一个固定问题（经历介绍请求）
和后续基于case.docx的深挖追问。
"""

from typing import Dict, List, Optional
from .deep_dive_generator import DeepDiveQuestionGenerator
from .experience_evaluator import ExperienceEvaluator


class ExperienceQuestionEngine:
    """
    第二阶段经历类问题引擎
    
    负责管理经历类问题的生成、评估和进度跟踪
    特点：第一个问题固定为经历介绍请求，后续为深挖追问
    """
    
    def __init__(self):
        self.deep_dive_generator = DeepDiveQuestionGenerator()
        self.evaluator = ExperienceEvaluator()
        
        # 状态跟踪
        self.current_question_index = 0
        self.max_questions = 3  # 第二阶段默认3题
        self.stage_started = False
        
        # 经历相关数据
        self.current_experience = None  # 当前讨论的经历
        self.experience_context = {}
        self.technical_keywords = []
        
        # 问答记录
        self.asked_questions = []
        self.question_responses = []
        self.question_scores = []
        
    def start_stage(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """
        开始第二阶段面试
        
        Args:
            resume_data: 简历数据
            jd_data: 职位描述数据
            
        Returns:
            第一个问题（经历介绍请求）
        """
        self.resume_data = resume_data
        self.jd_data = jd_data
        
        # 重置状态
        self.current_question_index = 0
        self.stage_started = True
        self.current_experience = None
        self.experience_context = {}
        self.technical_keywords = []
        self.asked_questions.clear()
        self.question_responses.clear()
        self.question_scores.clear()
        
        # 生成第一个固定问题
        return self.generate_initial_experience_question()
    
    def generate_initial_experience_question(self) -> Dict:
        """
        生成第一个问题：要求详细介绍简历上的一个经历
        
        Returns:
            经历介绍请求问题
        """
        # 从简历中提取项目和工作经历
        experiences = []
        if self.resume_data.get('projects'):
            experiences.extend([f"项目经历：{proj}" for proj in self.resume_data['projects']])
        if self.resume_data.get('experience'):
            experiences.extend([f"工作经历：{exp}" for exp in self.resume_data['experience']])
        
        # 构建个性化的第一个问题
        if experiences:
            experience_list = "\n".join([f"- {exp}" for exp in experiences[:5]])  # 限制显示数量
            question = f"""我看到您的简历中有以下几项经历：

{experience_list}

请您选择其中一项您觉得最有代表性或者最有成就感的经历，详细介绍一下这个项目/工作的背景、您的具体职责、技术实现方案、遇到的挑战以及最终的成果。请尽可能详细地描述，这样我可以更好地了解您的技术能力和项目经验。"""
        else:
            question = """请您详细介绍一个您参与过的技术项目或工作经历，包括：
1. 项目背景和目标
2. 您在其中的具体角色和职责
3. 使用的技术栈和实现方案
4. 遇到的主要技术挑战
5. 最终的成果和收获

请尽可能详细地描述，这样我可以更好地了解您的技术能力。"""
        
        question_data = {
            'question': question,
            'question_type': 'initial_experience_request',
            'source': 'experience_engine',
            'stage': '第二阶段：经历类问题',
            'question_number': 1,
            'total_questions': self.max_questions,
            'category': '经历介绍'
        }
        
        self.asked_questions.append(question_data)
        self.current_question_index += 1
        
        return question_data
    
    def generate_follow_up_question(self, user_experience_description: str) -> Dict:
        """
        根据用户的经历描述生成深挖追问
        
        Args:
            user_experience_description: 用户的经历描述
            
        Returns:
            深挖追问数据
        """
        if self.current_question_index >= self.max_questions:
            return {
                'question': None,
                'stage_completed': True,
                'message': '第二阶段经历类问题已完成'
            }
        
        # 更新当前经历上下文
        if self.current_question_index == 1:  # 第一次收到经历描述
            self.current_experience = user_experience_description
            self.experience_context['current_experience'] = user_experience_description
            self.technical_keywords = self._extract_technical_keywords(user_experience_description)
        
        # 生成深挖问题
        question_data = self.deep_dive_generator.generate_deep_dive_question(
            user_experience=user_experience_description,
            question_history=self.asked_questions,
            technical_keywords=self.technical_keywords,
            jd_data=self.jd_data,
            question_number=self.current_question_index + 1,
            total_questions=self.max_questions
        )
        
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
        
        # 特殊处理：如果是第一个问题的回答，提取经历信息
        if question_data['question_type'] == 'initial_experience_request':
            self.current_experience = user_response
            self.technical_keywords = self._extract_technical_keywords(user_response)
        
        # 评估回答
        evaluation = self.evaluator.evaluate_response(
            user_response=user_response,
            question_data=question_data,
            context={
                'resume_data': self.resume_data,
                'jd_data': self.jd_data,
                'current_experience': self.current_experience,
                'technical_keywords': self.technical_keywords
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
        获取第二阶段总结
        
        Returns:
            阶段总结数据
        """
        if not self.question_scores:
            average_score = 0
        else:
            average_score = sum(self.question_scores) / len(self.question_scores)
        
        return {
            'stage_name': '第二阶段：经历类问题',
            'questions_asked': len(self.asked_questions),
            'total_questions': self.max_questions,
            'average_score': round(average_score, 2),
            'question_responses': self.question_responses,
            'detailed_scores': self.question_scores,
            'current_experience_summary': self.current_experience[:200] + "..." if self.current_experience and len(self.current_experience) > 200 else self.current_experience,
            'technical_keywords_discussed': self.technical_keywords,
            'stage_completed': self.current_question_index >= self.max_questions,
            'next_stage': '第三阶段：技术类问题' if self.current_question_index >= self.max_questions else None
        }
    
    def get_progress_info(self) -> Dict:
        """获取当前进度信息"""
        return {
            'current_question': self.current_question_index,
            'total_questions': self.max_questions,
            'progress_percentage': (self.current_question_index / self.max_questions) * 100,
            'remaining_questions': self.max_questions - self.current_question_index,
            'experience_provided': self.current_experience is not None,
            'keywords_extracted': len(self.technical_keywords)
        }
    
    def _extract_technical_keywords(self, experience_text: str) -> List[str]:
        """从经历描述中提取技术关键词"""
        import re
        
        # 常见技术关键词模式
        tech_patterns = [
            # 编程语言
            r'\b(Java|Python|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Scala|Kotlin|PHP|Ruby)\b',
            # 框架和库
            r'\b(Spring|Django|Flask|React|Vue|Angular|Express|FastAPI|TensorFlow|PyTorch|Spark|Flink)\b',
            # 数据库
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|ElasticSearch|Neo4j|Oracle|SQLServer|Cassandra)\b',
            # 云服务和容器
            r'\b(Docker|Kubernetes|AWS|Azure|GCP|Alibaba Cloud|Tencent Cloud|Jenkins|GitLab)\b',
            # 机器学习和AI
            r'\b(机器学习|深度学习|神经网络|CNN|RNN|LSTM|Transformer|BERT|GPT|LLM|NLP|CV|RAG|微调|Lora)\b',
            # 架构和模式
            r'\b(微服务|分布式|负载均衡|缓存|消息队列|API网关|服务网格|Lambda架构)\b',
            # 大数据和流处理
            r'\b(Hadoop|Kafka|Storm|Hive|HBase|Flume|Sqoop|Zookeeper)\b',
            # 其他技术
            r'\b(区块链|物联网|WebSocket|GraphQL|gRPC|Protobuf)\b'
        ]
        
        keywords = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, experience_text, re.IGNORECASE)
            keywords.extend(matches)
        
        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # 限制关键词数量
    
    def reset(self):
        """重置引擎状态"""
        self.current_question_index = 0
        self.stage_started = False
        self.current_experience = None
        self.experience_context = {}
        self.technical_keywords = []
        self.asked_questions.clear()
        self.question_responses.clear()
        self.question_scores.clear()
        self.resume_data = None
        self.jd_data = None
