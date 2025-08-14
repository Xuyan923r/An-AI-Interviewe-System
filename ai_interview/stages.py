# -*- coding: utf-8 -*-

class ThreeStageInterviewManager:
    """三阶段面试管理器：非技术问题、经历类问题、技术类问题"""
    def __init__(self):
        self.stages = ["非技术问题", "经历类问题", "技术类问题"]
        self.current_stage = 0
        self.stage_questions = {
            "非技术问题": [],
            "经历类问题": [],
            "技术类问题": []
        }
        self.stage_scores = {
            "非技术问题": [],
            "经历类问题": [],
            "技术类问题": []
        }
        self.questions_per_stage = [2, 3, 3]
        self.current_stage_question_count = 0

    def get_current_stage(self):
        if self.current_stage < len(self.stages):
            return self.stages[self.current_stage]
        return "面试结束"

    def should_advance_stage(self):
        return self.current_stage_question_count >= self.questions_per_stage[self.current_stage]

    def advance_to_next_stage(self):
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            self.current_stage_question_count = 0
            return True
        return False

    def add_question_to_stage(self, question, stage=None):
        if stage is None:
            stage = self.get_current_stage()
        if stage in self.stage_questions:
            self.stage_questions[stage].append(question)
            self.current_stage_question_count += 1

    def add_score_to_stage(self, score, stage=None):
        if stage is None:
            stage = self.get_current_stage()
        if stage in self.stage_scores:
            self.stage_scores[stage].append(score)

    def get_stage_prompt(self, jd_data=None, resume_data=None):
        current_stage = self.get_current_stage()
        if current_stage == "非技术问题":
            return self._get_non_technical_prompt(jd_data, resume_data)
        elif current_stage == "经历类问题":
            return self._get_experience_prompt(resume_data)
        elif current_stage == "技术类问题":
            return self._get_technical_prompt(jd_data)
        else:
            return "面试已结束"

    def _get_non_technical_prompt(self, jd_data, resume_data):
        prompt = f"""
### 当前阶段：非技术问题（第{self.current_stage_question_count + 1}题）

这是面试的第一阶段，主要考察候选人的基本情况、沟通能力和职业规划。

**问题类型要求：**
1. 自我介绍类问题
2. 职业发展规划
3. 对公司和岗位的了解
4. 基本的工作态度和价值观

**基于简历信息生成问题：**
"""
        if resume_data:
            prompt += f"- 候选人姓名: {resume_data.get('name', '未知')}\n"
            prompt += f"- 工作经验: {len(resume_data.get('experience', []))}项\n"
            prompt += f"- 主要技能: {', '.join(resume_data.get('skills', [])[:3])}\n"

        if jd_data:
            prompt += f"- 目标职位: {jd_data.get('position', '未知')}\n"

        return prompt

    def _get_experience_prompt(self, resume_data):
        prompt = f"""
### 当前阶段：经历类问题（第{self.current_stage_question_count + 1}题）

这是面试的第二阶段，深入挖掘候选人的项目经历和工作经验。

**问题类型要求：**
1. 深入挖掘简历中的项目经历
2. 具体技术实现细节
3. 遇到的挑战和解决方案
4. 团队协作和角色分工

**基于简历经历生成问题：**
"""
        if resume_data:
            if resume_data.get('projects'):
                prompt += "**项目经历：**\n"
                for project in resume_data['projects'][:3]:
                    prompt += f"- {project}\n"

            if resume_data.get('experience'):
                prompt += "**工作经验：**\n"
                for exp in resume_data['experience'][:3]:
                    prompt += f"- {exp}\n"

        return prompt

    def _get_technical_prompt(self, jd_data):
        prompt = f"""
### 当前阶段：技术类问题（第{self.current_stage_question_count + 1}题）

这是面试的第三阶段，重点考察候选人的专业技术能力。

**问题类型要求：**
1. 基于JD要求的核心技术能力
2. 算法和数据结构（如果相关）
3. 系统设计和架构能力
4. 技术深度和广度

**基于JD要求生成问题：**
"""
        if jd_data:
            if jd_data.get('keywords'):
                prompt += f"**关键技术要求：** {', '.join(jd_data['keywords'])}\n"
            if jd_data.get('requirements'):
                prompt += "**技术要求细节：**\n"
                for req in jd_data['requirements'][:3]:
                    prompt += f"- {req}\n"

        return prompt

    def get_stage_summary(self):
        summary = "### 三阶段面试总结：\n"
        for i, stage in enumerate(self.stages):
            scores = self.stage_scores[stage]
            if scores:
                avg_score = sum(scores) / len(scores)
                summary += f"**{stage}**: {len(scores)}题, 平均分: {avg_score:.2f}\n"
            else:
                summary += f"**{stage}**: 未完成\n"
        return summary

    def adjust_stage_questions(self, recent_scores):
        if len(recent_scores) < 2:
            return
        avg_recent = sum(recent_scores[-2:]) / len(recent_scores[-2:])
        if avg_recent >= 0.75:
            if self.current_stage < 2:
                self.questions_per_stage[2] = min(5, self.questions_per_stage[2] + 1)
        elif avg_recent < 0.5:
            if self.current_stage < 2:
                self.questions_per_stage[2] = max(2, self.questions_per_stage[2] - 1)
                self.questions_per_stage[1] = min(4, self.questions_per_stage[1] + 1)



