# -*- coding: utf-8 -*-

import random
import pandas as pd


class QuestionBankManager:
    """题库管理器，支持多赛道面试题库"""
    def __init__(self):
        self.question_banks = {}
        self.tracks = ["后端", "前端", "算法", "测试", "产品", "运营"]
        self.current_track = None
        self.load_question_banks()

    def load_question_banks(self):
        for track in self.tracks:
            try:
                file_path = f"data/data_divided/{track}.csv"
                df = pd.read_csv(file_path, encoding='utf-8')

                questions = []
                if track in ["后端"]:
                    for _, row in df.iterrows():
                        if len(row) >= 2 and pd.notna(row.iloc[1]):
                            questions.append({
                                "category": str(row.iloc[0]).strip(),
                                "question": str(row.iloc[1]).strip(),
                                "company": ""
                            })
                elif track in ["前端", "运营"]:
                    for _, row in df.iterrows():
                        if len(row) >= 2 and pd.notna(row.iloc[1]) and "Unnamed" not in str(row.iloc[1]):
                            questions.append({
                                "category": str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else "",
                                "question": str(row.iloc[1]).strip(),
                                "company": str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                            })
                else:
                    for _, row in df.iterrows():
                        if len(row) >= 2 and pd.notna(row.iloc[1]):
                            questions.append({
                                "category": str(row.iloc[0]).strip(),
                                "question": str(row.iloc[1]).strip(),
                                "company": str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                            })

                self.question_banks[track] = self._categorize_by_difficulty(questions)
                print(f"已加载 {track} 题库: {len(questions)} 题")
            except Exception as e:
                print(f"加载 {track} 题库失败: {e}")
                self.question_banks[track] = {"简单": [], "中等": [], "困难": []}

    def _categorize_by_difficulty(self, questions):
        categorized = {"简单": [], "中等": [], "困难": []}
        easy_keywords = ["自我介绍", "介绍", "背景", "经历", "基础", "了解", "是什么", "简单"]
        hard_keywords = ["架构", "设计", "优化", "性能", "复杂", "系统", "深入", "原理", "底层", "高级"]
        for q in questions:
            question_text = q["question"].lower()
            category_text = q["category"].lower()
            combined_text = question_text + " " + category_text
            if any(keyword in combined_text for keyword in easy_keywords):
                categorized["简单"].append(q)
            elif any(keyword in combined_text for keyword in hard_keywords):
                categorized["困难"].append(q)
            else:
                categorized["中等"].append(q)
        return categorized

    def set_track(self, track):
        if track in self.tracks:
            self.current_track = track
            return True
        return False

    def get_reference_questions(self, difficulty="中等", num_questions=3):
        if not self.current_track or self.current_track not in self.question_banks:
            return []
        track_questions = self.question_banks[self.current_track]
        difficulty_questions = track_questions.get(difficulty, [])
        if not difficulty_questions:
            all_questions = []
            for diff_level in track_questions.values():
                all_questions.extend(diff_level)
            if all_questions:
                return random.sample(all_questions, min(num_questions, len(all_questions)))
            return []
        return random.sample(difficulty_questions, min(num_questions, len(difficulty_questions)))

    def get_track_summary(self):
        if not self.current_track:
            return "未选择赛道"
        track_data = self.question_banks.get(self.current_track, {})
        summary = f"{self.current_track}赛道题库:\n"
        for difficulty, questions in track_data.items():
            summary += f"- {difficulty}: {len(questions)}题\n"
        return summary



