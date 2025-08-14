# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple


class AbilityPyramid:
    """岗位-能力金字塔表示与摘要。

    设计目标：
    - 根据JD信息构建基础/中级/高级三层能力要点
    - 提供当前关注层级建议，便于动态提示对齐问题难度
    - 仅做轻量实现，真实映射数据留空位，后续可由外部数据补全
    """

    def __init__(self, base: List[str], middle: List[str], advanced: List[str]):
        self.base = base
        self.middle = middle
        self.advanced = advanced

    @staticmethod
    def from_jd(jd_data: Dict) -> "AbilityPyramid":
        """从JD关键信息粗略生成能力金字塔。

        说明：此处仅为启发式占位逻辑；
        - 若提供更精细的岗位-能力映射表，可在此处替换为知识库驱动。
        """
        keywords = (jd_data or {}).get("keywords", [])
        requirements = (jd_data or {}).get("requirements", [])

        base: List[str] = []
        middle: List[str] = []
        advanced: List[str] = []

        for kw in keywords:
            lowered = kw.lower()
            if any(x in lowered for x in ["基础", "basic", "入门", "概念"]):
                base.append(kw)
            elif any(x in lowered for x in ["架构", "architecture", "高并发", "分布式", "kubernetes", "k8s"]):
                advanced.append(kw)
            else:
                middle.append(kw)

        if not base and requirements:
            base.extend(requirements[:2])
        if not middle and requirements:
            middle.extend(requirements[2:5])
        if not advanced and keywords:
            advanced.extend(keywords[-2:])

        return AbilityPyramid(base=base[:8], middle=middle[:8], advanced=advanced[:8])

    def summarize(self) -> str:
        lines = [
            "### 能力金字塔 (占位摘要)",
            f"- 基础层: {', '.join(self.base) if self.base else '待补充'}",
            f"- 中级层: {', '.join(self.middle) if self.middle else '待补充'}",
            f"- 高级层: {', '.join(self.advanced) if self.advanced else '待补充'}",
        ]
        return "\n".join(lines)

    def suggest_focus_level(self, score_history: List[float]) -> str:
        if not score_history:
            return "中级"
        avg = sum(score_history[-3:]) / min(3, len(score_history))
        if avg >= 0.75:
            return "高级"
        if avg < 0.5:
            return "基础"
        return "中级"


class JobKnowledgeGraphBuilder:
    """岗位知识图谱构建（轻量）

    - 从简历与JD中抽取节点，生成关系三元组摘要
    - 真实图谱数据与映射规则可外置到 data/knowledge/ 下，当前实现仅做占位
    """

    def __init__(self, resume_data: Dict, jd_data: Dict):
        self.resume_data = resume_data or {}
        self.jd_data = jd_data or {}

    def build_triplets(self, limit: int = 6) -> List[Tuple[str, str, str]]:
        triplets: List[Tuple[str, str, str]] = []
        skills = self.resume_data.get("skills", [])
        projects = self.resume_data.get("projects", [])
        requirements = self.jd_data.get("requirements", [])

        for skill in skills[:3]:
            for proj in projects[:2]:
                triplets.append((skill, "应用于", proj))

        for req in requirements[:3]:
            for skill in skills[:2]:
                triplets.append((req, "需要", skill))

        return triplets[:limit]

    def summarize(self, limit: int = 6) -> str:
        triplets = self.build_triplets(limit=limit)
        if not triplets:
            return "### 岗位能力知识图谱\n待补充"
        lines = ["### 岗位能力知识图谱"]
        for h, r, t in triplets:
            lines.append(f"- {h} -- {r} --> {t}")
        return "\n".join(lines)


