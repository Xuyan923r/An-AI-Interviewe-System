# -*- coding: utf-8 -*-
"""
自适应难度管理器

实现B1 < B2 < B3的动态难度调整系统，根据用户回答质量实时调整问题难度。
"""

from typing import Dict, List, Optional


class AdaptiveDifficultyManager:
    """
    自适应难度管理器
    
    实现B1 < B2 < B3的三级难度系统和动态调整逻辑
    """
    
    def __init__(self):
        self.current_difficulty = "B2"  # 默认从中等难度开始
        self.difficulty_history = []
        self.question_count = 0
        
        # B1 < B2 < B3 难度级别定义
        self.difficulty_levels = {
            "B1": {
                "level": 1, 
                "name": "基础级别",
                "description": "基础概念、入门技能、简单实现",
                "keywords": ["基础", "概念", "简单", "入门"],
                "target_audience": "初级开发者",
                "score_range": "0.4-0.7"
            },
            "B2": {
                "level": 2, 
                "name": "中等级别",
                "description": "实际应用、项目经验、中等复杂度",
                "keywords": ["实际", "项目", "应用", "经验"],
                "target_audience": "有经验的开发者",
                "score_range": "0.5-0.8"
            },
            "B3": {
                "level": 3, 
                "name": "高级级别",
                "description": "深度技术、架构设计、复杂场景",
                "keywords": ["深度", "架构", "复杂", "高级"],
                "target_audience": "高级开发者",
                "score_range": "0.6-0.9"
            }
        }
        
        # 难度调整阈值
        self.adjustment_thresholds = {
            "increase": 0.75,  # 得分 >= 0.75 时提升难度
            "decrease": 0.5,   # 得分 < 0.5 时降低难度
            "maintain": (0.5, 0.75)  # 0.5 <= 得分 < 0.75 时保持难度
        }
    
    def adjust_difficulty(self, score: float, question_context: Dict = None, 
                         response_analysis: Dict = None) -> Dict:
        """
        根据回答质量动态调整难度
        
        Args:
            score: 用户回答得分 (0-1)
            question_context: 问题上下文
            response_analysis: 回答分析结果
            
        Returns:
            难度调整结果
        """
        previous_difficulty = self.current_difficulty
        adjustment_reason = ""
        
        # 执行难度调整逻辑
        if score >= self.adjustment_thresholds["increase"]:
            # 回答优秀，提升难度
            new_difficulty = self._increase_difficulty()
            if new_difficulty != previous_difficulty:
                adjustment_reason = f"回答优秀(得分{score:.2f})，难度提升：{previous_difficulty}→{new_difficulty}"
            else:
                adjustment_reason = f"回答优秀(得分{score:.2f})，但已达最高难度{new_difficulty}"
                
        elif score < self.adjustment_thresholds["decrease"]:
            # 回答较差，降低难度
            new_difficulty = self._decrease_difficulty()
            if new_difficulty != previous_difficulty:
                adjustment_reason = f"回答较差(得分{score:.2f})，难度降低：{previous_difficulty}→{new_difficulty}"
            else:
                adjustment_reason = f"回答较差(得分{score:.2f})，但已达最低难度{new_difficulty}"
                
        else:
            # 回答一般，保持当前难度
            new_difficulty = self.current_difficulty
            adjustment_reason = f"回答一般(得分{score:.2f})，保持当前难度{new_difficulty}"
        
        # 更新当前难度
        self.current_difficulty = new_difficulty
        self.question_count += 1
        
        # 记录难度调整历史
        adjustment_record = {
            "question_number": self.question_count,
            "score": score,
            "previous_difficulty": previous_difficulty,
            "new_difficulty": new_difficulty,
            "adjustment_reason": adjustment_reason,
            "adjustment_type": self._get_adjustment_type(previous_difficulty, new_difficulty),
            "question_context": question_context.get('category', '未知') if question_context else '未知'
        }
        
        self.difficulty_history.append(adjustment_record)
        
        return {
            "previous_difficulty": previous_difficulty,
            "new_difficulty": new_difficulty,
            "adjustment_reason": adjustment_reason,
            "adjustment_type": adjustment_record["adjustment_type"],
            "difficulty_info": self.difficulty_levels[new_difficulty]
        }
    
    def _increase_difficulty(self) -> str:
        """提升难度级别"""
        if self.current_difficulty == "B1":
            return "B2"
        elif self.current_difficulty == "B2":
            return "B3"
        else:
            return "B3"  # 已是最高难度
    
    def _decrease_difficulty(self) -> str:
        """降低难度级别"""
        if self.current_difficulty == "B3":
            return "B2"
        elif self.current_difficulty == "B2":
            return "B1"
        else:
            return "B1"  # 已是最低难度
    
    def _get_adjustment_type(self, prev_diff: str, new_diff: str) -> str:
        """获取调整类型"""
        prev_level = self.difficulty_levels[prev_diff]["level"]
        new_level = self.difficulty_levels[new_diff]["level"]
        
        if new_level > prev_level:
            return "increase"
        elif new_level < prev_level:
            return "decrease"
        else:
            return "maintain"
    
    def get_current_difficulty(self) -> str:
        """获取当前难度级别"""
        return self.current_difficulty
    
    def get_difficulty_info(self, difficulty: str = None) -> Dict:
        """获取难度级别信息"""
        if difficulty is None:
            difficulty = self.current_difficulty
        return self.difficulty_levels.get(difficulty, {})
    
    def get_difficulty_analysis(self) -> Dict:
        """获取当前难度分析"""
        current_info = self.difficulty_levels[self.current_difficulty]
        
        return {
            "current_difficulty": self.current_difficulty,
            "difficulty_name": current_info["name"],
            "description": current_info["description"],
            "target_audience": current_info["target_audience"],
            "expected_score_range": current_info["score_range"],
            "question_count": self.question_count,
            "adjustment_history_count": len(self.difficulty_history)
        }
    
    def get_difficulty_progression_summary(self) -> Dict:
        """获取难度调整轨迹总结"""
        if not self.difficulty_history:
            return {
                "total_adjustments": 0,
                "difficulty_distribution": {},
                "adjustment_summary": "暂无调整记录"
            }
        
        # 统计难度分布
        difficulty_counts = {}
        adjustment_types = {"increase": 0, "decrease": 0, "maintain": 0}
        
        for record in self.difficulty_history:
            # 统计各难度级别的使用次数
            diff = record["new_difficulty"]
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            # 统计调整类型
            adj_type = record["adjustment_type"]
            adjustment_types[adj_type] += 1
        
        # 生成轨迹描述
        difficulties = [record["new_difficulty"] for record in self.difficulty_history]
        if len(set(difficulties)) == 1:
            trend = "稳定"
        elif difficulties[-1] > difficulties[0]:
            trend = "上升"
        elif difficulties[-1] < difficulties[0]:
            trend = "下降"
        else:
            trend = "波动"
        
        return {
            "total_adjustments": len(self.difficulty_history),
            "difficulty_distribution": difficulty_counts,
            "adjustment_types": adjustment_types,
            "trend": trend,
            "final_difficulty": self.current_difficulty,
            "adjustment_summary": self._generate_adjustment_summary()
        }
    
    def _generate_adjustment_summary(self) -> str:
        """生成调整总结"""
        if not self.difficulty_history:
            return "暂无调整记录"
        
        summary_parts = []
        
        # 总体趋势
        first_diff = self.difficulty_history[0]["previous_difficulty"]
        final_diff = self.current_difficulty
        
        if final_diff > first_diff:
            summary_parts.append(f"整体难度从{first_diff}提升至{final_diff}")
        elif final_diff < first_diff:
            summary_parts.append(f"整体难度从{first_diff}降低至{final_diff}")
        else:
            summary_parts.append(f"整体难度保持在{final_diff}级别")
        
        # 调整次数
        increases = sum(1 for r in self.difficulty_history if r["adjustment_type"] == "increase")
        decreases = sum(1 for r in self.difficulty_history if r["adjustment_type"] == "decrease")
        
        if increases > 0:
            summary_parts.append(f"提升{increases}次")
        if decreases > 0:
            summary_parts.append(f"降低{decreases}次")
        
        return "，".join(summary_parts)
    
    def set_initial_difficulty(self, difficulty: str):
        """设置初始难度"""
        if difficulty in self.difficulty_levels:
            self.current_difficulty = difficulty
    
    def reset(self):
        """重置难度管理器"""
        self.current_difficulty = "B2"
        self.difficulty_history.clear()
        self.question_count = 0
