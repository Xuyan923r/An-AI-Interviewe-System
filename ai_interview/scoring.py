# # -*- coding: utf-8 -*-

# import ollama
# import re


# class ScoreAndDifficultyManager:
#     """评分系统和动态难度调整管理器"""
#     def __init__(self):
#         self.current_difficulty = "中等"
#         self.score_history = []
#         self.difficulty_history = []
#         self.question_count = 0

#         self.difficulty_levels = {
#             "简单": {"level": 1, "keywords": ["基础", "简单", "基本", "介绍"], "description": "基础概念和简单问题"},
#             "中等": {"level": 2, "keywords": ["实际", "应用", "经验", "项目"], "description": "实际应用和项目经验"},
#             "困难": {"level": 3, "keywords": ["深入", "复杂", "高级", "架构", "优化"], "description": "深度技术和复杂场景"},
#         }

#     def evaluate_response(self, user_response, question_context=""):
#         try:
#             scoring_prompt = f"""
# 你是一个友善而专业的面试官，正在对候选人的回答进行评分。请根据面试的实际情况，给出公平合理的评分。

# 面试问题: {question_context}
# 候选人回答: {user_response}

# 评分指导原则：
# - 如果候选人的回答合理、相关且表达清楚，应给予0.6-0.8的分数
# - 如果回答特别出色、有深度或有创新见解，可给予0.8-1.0的分数  
# - 如果回答基本合理但略显简单，可给予0.4-0.6的分数
# - 只有在回答完全不相关、错误或无法理解时，才给予0.4以下的分数

# 请模拟真实面试场景，用人性化的角度来评判。大多数正常的回答都应该在0.5-0.8这个合理区间内。

# 请只返回一个0到1之间的小数作为评分，保留两位小数，不要包含任何其他文字。
# """
#             response = ollama.chat(
#                 model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
#                 messages=[{"role": "user", "content": scoring_prompt}]
#             )
#             score_text = response['message']['content'].strip()
#             score_match = re.search(r'(\d*\.?\d+)', score_text)
#             if score_match:
#                 score = float(score_match.group(1))
#                 score = max(0.0, min(1.0, score))
#             else:
#                 score = 0.5
#             self.score_history.append(score)
#             self.question_count += 1
#             return score
#         except Exception as e:
#             print(f"评分过程出错: {e}")
#             return 0.5

#     def adjust_difficulty(self, score):
#         previous_difficulty = self.current_difficulty
#         if score >= 0.75:
#             if self.current_difficulty == "简单":
#                 self.current_difficulty = "中等"
#             elif self.current_difficulty == "中等":
#                 self.current_difficulty = "困难"
#         elif score < 0.5:
#             if self.current_difficulty == "困难":
#                 self.current_difficulty = "中等"
#             elif self.current_difficulty == "中等":
#                 self.current_difficulty = "简单"
#         self.difficulty_history.append({
#             "question_num": self.question_count,
#             "score": score,
#             "previous_difficulty": previous_difficulty,
#             "new_difficulty": self.current_difficulty
#         })
#         return self.current_difficulty

#     def get_difficulty_prompt(self):
#         current_level = self.difficulty_levels[self.current_difficulty]
#         prompt = f"""
# 当前问题难度级别: {self.current_difficulty} (级别 {current_level['level']})
# 难度描述: {current_level['description']}
# 建议关键词: {', '.join(current_level['keywords'])}

# 请根据此难度级别生成相应的面试问题。

# 难度级别说明：
# - 简单：基础概念、基本技能、入门级问题
# - 中等：实际应用、项目经验、中级技术问题
# - 困难：深度技术、复杂场景、高级架构问题
# """
#         return prompt

#     def get_score_summary(self):
#         if not self.score_history:
#             return "暂无评分记录"
#         avg_score = sum(self.score_history) / len(self.score_history)
#         max_score = max(self.score_history)
#         min_score = min(self.score_history)
#         summary = f"""
# 评分摘要：
# - 总问题数: {len(self.score_history)}
# - 平均分: {avg_score:.2f}
# - 最高分: {max_score:.2f}
# - 最低分: {min_score:.2f}
# - 当前难度: {self.current_difficulty}
# """
#         return summary

#     def get_difficulty_progression(self):
#         if not self.difficulty_history:
#             return "暂无难度调整记录"
#         progression = "难度调整轨迹：\n"
#         for record in self.difficulty_history:
#             progression += f"问题{record['question_num']}: 得分{record['score']:.2f} -> {record['previous_difficulty']} → {record['new_difficulty']}\n"
#         return progression





# -*- coding: utf-8 -*-

import ollama
import re


class ScoreAndDifficultyManager:
    """评分系统和动态难度调整管理器（多维度评分+智能难度调整）"""
    def __init__(self):
        self.current_difficulty = "中等"
        self.score_history = []
        self.difficulty_history = []
        self.question_count = 0

        self.difficulty_levels = {
            "简单": {"level": 1, "keywords": ["基础", "简单", "基本", "介绍"], "description": "基础概念和简单问题"},
            "中等": {"level": 2, "keywords": ["实际", "应用", "经验", "项目"], "description": "实际应用和项目经验"},
            "困难": {"level": 3, "keywords": ["深入", "复杂", "高级", "架构", "优化"], "description": "深度技术和复杂场景"},
        }

    def evaluate_response(self, user_response, question_context="", history_context=""):
        """
        多维度评分：
        - history_context: 候选人前几题回答
        - 三个子评分：理解程度、表达清晰度、技术深度
        """
        try:
            scoring_prompt = f"""
你是专业面试官，对候选人的回答进行评分。
面试问题: {question_context}
候选人回答: {user_response}
历史回答: {history_context}

请从三个维度打分（0-1）：
1. 理解程度
2. 表达清晰度
3. 技术深度

请只返回json格式，例如：
{{"理解程度":0.7, "表达清晰度":0.8, "技术深度":0.6}}
"""
            response = ollama.chat(
                model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
                messages=[{"role": "user", "content": scoring_prompt}]
            )
            score_text = response['message']['content'].strip()
            match = re.findall(r'\d*\.?\d+', score_text)
            if match and len(match) >= 3:
                scores = list(map(float, match[:3]))
            else:
                scores = [0.5, 0.5, 0.5]

            # 综合得分
            score = sum(scores) / 3
            score = max(0.0, min(1.0, score))

            # 保存历史记录
            self.score_history.append({
                "question_num": self.question_count + 1,
                "score": score,
                "details": {"理解程度": scores[0], "表达清晰度": scores[1], "技术深度": scores[2]}
            })
            self.question_count += 1
            return score
        except Exception as e:
            print(f"评分过程出错: {e}")
            return 0.5

    def adjust_difficulty(self, score, window=2):
        """
        智能调整难度：
        - window: 最近几题平均分控制难度
        """
        previous_difficulty = self.current_difficulty
        recent_scores = [r['score'] for r in self.score_history[-window:]]
        avg_recent = sum(recent_scores) / len(recent_scores)

        if avg_recent >= 0.75:
            if self.current_difficulty == "简单":
                self.current_difficulty = "中等"
            elif self.current_difficulty == "中等":
                self.current_difficulty = "困难"
        elif avg_recent < 0.5:
            if self.current_difficulty == "困难":
                self.current_difficulty = "中等"
            elif self.current_difficulty == "中等":
                self.current_difficulty = "简单"

        self.difficulty_history.append({
            "question_num": self.question_count,
            "score": score,
            "previous_difficulty": previous_difficulty,
            "new_difficulty": self.current_difficulty
        })
        return self.current_difficulty

    def get_difficulty_prompt(self):
        """
        根据当前难度生成问题提示
        """
        current_level = self.difficulty_levels[self.current_difficulty]
        prompt = f"""
当前问题难度级别: {self.current_difficulty} (级别 {current_level['level']})
难度描述: {current_level['description']}
建议关键词: {', '.join(current_level['keywords'])}

请根据此难度级别生成相应的面试问题。

难度级别说明：
- 简单：基础概念、基本技能、入门级问题
- 中等：实际应用、项目经验、中级技术问题
- 困难：深度技术、复杂场景、高级架构问题
"""
        return prompt

    def get_score_summary(self):
        """
        输出评分摘要，包括每个维度的平均分
        """
        if not self.score_history:
            return "暂无评分记录"
        total = len(self.score_history)
        avg_total = sum([r['score'] for r in self.score_history]) / total
        max_total = max([r['score'] for r in self.score_history])
        min_total = min([r['score'] for r in self.score_history])

        avg_understand = sum([r['details']['理解程度'] for r in self.score_history]) / total
        avg_clarity = sum([r['details']['表达清晰度'] for r in self.score_history]) / total
        avg_tech = sum([r['details']['技术深度'] for r in self.score_history]) / total

        summary = f"""
评分摘要：
- 总问题数: {total}
- 平均总分: {avg_total:.2f}
- 最高分: {max_total:.2f}
- 最低分: {min_total:.2f}
- 理解程度平均: {avg_understand:.2f}
- 表达清晰度平均: {avg_clarity:.2f}
- 技术深度平均: {avg_tech:.2f}
- 当前难度: {self.current_difficulty}
"""
        return summary

    def get_difficulty_progression(self):
        """
        输出难度调整轨迹
        """
        if not self.difficulty_history:
            return "暂无难度调整记录"
        progression = "难度调整轨迹：\n"
        for record in self.difficulty_history:
            progression += f"问题{record['question_num']}: 得分{record['score']:.2f} -> {record['previous_difficulty']} → {record['new_difficulty']}\n"
        return progression
