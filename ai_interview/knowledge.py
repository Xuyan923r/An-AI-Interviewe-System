# # -*- coding: utf-8 -*-

# from typing import Dict, List, Tuple


# class AbilityPyramid:
#     """岗位-能力金字塔表示与摘要。

#     设计目标：
#     - 根据JD信息构建基础/中级/高级三层能力要点
#     - 提供当前关注层级建议，便于动态提示对齐问题难度
#     - 仅做轻量实现，真实映射数据留空位，后续可由外部数据补全
#     """

#     def __init__(self, base: List[str], middle: List[str], advanced: List[str]):
#         self.base = base
#         self.middle = middle
#         self.advanced = advanced

#     @staticmethod
#     def from_jd(jd_data: Dict) -> "AbilityPyramid":
#         """从JD关键信息粗略生成能力金字塔。

#         说明：此处仅为启发式占位逻辑；
#         - 若提供更精细的岗位-能力映射表，可在此处替换为知识库驱动。
#         """
#         keywords = (jd_data or {}).get("keywords", [])
#         requirements = (jd_data or {}).get("requirements", [])

#         base: List[str] = []
#         middle: List[str] = []
#         advanced: List[str] = []

#         for kw in keywords:
#             lowered = kw.lower()
#             if any(x in lowered for x in ["基础", "basic", "入门", "概念"]):
#                 base.append(kw)
#             elif any(x in lowered for x in ["架构", "architecture", "高并发", "分布式", "kubernetes", "k8s"]):
#                 advanced.append(kw)
#             else:
#                 middle.append(kw)

#         if not base and requirements:
#             base.extend(requirements[:2])
#         if not middle and requirements:
#             middle.extend(requirements[2:5])
#         if not advanced and keywords:
#             advanced.extend(keywords[-2:])

#         return AbilityPyramid(base=base[:8], middle=middle[:8], advanced=advanced[:8])

#     def summarize(self) -> str:
#         lines = [
#             "### 能力金字塔 (占位摘要)",
#             f"- 基础层: {', '.join(self.base) if self.base else '待补充'}",
#             f"- 中级层: {', '.join(self.middle) if self.middle else '待补充'}",
#             f"- 高级层: {', '.join(self.advanced) if self.advanced else '待补充'}",
#         ]
#         return "\n".join(lines)

#     def suggest_focus_level(self, score_history: List[float]) -> str:
#         if not score_history:
#             return "中级"
#         avg = sum(score_history[-3:]) / min(3, len(score_history))
#         if avg >= 0.75:
#             return "高级"
#         if avg < 0.5:
#             return "基础"
#         return "中级"


# class JobKnowledgeGraphBuilder:
#     """岗位知识图谱构建（轻量）

#     - 从简历与JD中抽取节点，生成关系三元组摘要
#     - 真实图谱数据与映射规则可外置到 data/knowledge/ 下，当前实现仅做占位
#     """

#     def __init__(self, resume_data: Dict, jd_data: Dict):
#         self.resume_data = resume_data or {}
#         self.jd_data = jd_data or {}

#     def build_triplets(self, limit: int = 6) -> List[Tuple[str, str, str]]:
#         triplets: List[Tuple[str, str, str]] = []
#         skills = self.resume_data.get("skills", [])
#         projects = self.resume_data.get("projects", [])
#         requirements = self.jd_data.get("requirements", [])

#         for skill in skills[:3]:
#             for proj in projects[:2]:
#                 triplets.append((skill, "应用于", proj))

#         for req in requirements[:3]:
#             for skill in skills[:2]:
#                 triplets.append((req, "需要", skill))

#         return triplets[:limit]

#     def summarize(self, limit: int = 6) -> str:
#         triplets = self.build_triplets(limit=limit)
#         if not triplets:
#             return "### 岗位能力知识图谱\n待补充"
#         lines = ["### 岗位能力知识图谱"]
#         for h, r, t in triplets:
#             lines.append(f"- {h} -- {r} --> {t}")
#         return "\n".join(lines)





# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
import json
from dataclasses import dataclass


class SkillLevel(Enum):
    """技能水平枚举"""
    BASIC = "基础"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    EXPERT = "专家"


@dataclass
class SkillNode:
    """技能节点"""
    name: str
    level: SkillLevel
    category: str  # 如"编程语言", "框架", "数据库"等
    description: Optional[str] = None
    aliases: Optional[List[str]] = None  # 技能的别名/相关术语


@dataclass
class Relationship:
    """关系三元组"""
    source: str
    relation: str
    target: str
    weight: float = 1.0  # 关系强度/置信度


class AbilityPyramid:
    """岗位-能力金字塔表示与摘要。

    设计目标：
    - 根据JD信息构建基础/中级/高级/专家四层能力要点
    - 提供当前关注层级建议，便于动态提示对齐问题难度
    - 支持从外部知识库加载技能映射数据
    """

    def __init__(self, skills: Dict[SkillLevel, List[SkillNode]]):
        self.skills = skills
        self.skill_mapping = self._load_skill_mapping()

    def _load_skill_mapping(self) -> Dict[str, SkillNode]:
        """加载技能映射表（可从外部文件加载）"""
        # 这里使用内置的简单映射，实际应用中可以从文件或数据库加载
        return {
            "Java": SkillNode("Java", SkillLevel.INTERMEDIATE, "编程语言", 
                            "Java编程语言", ["J2EE", "JavaEE"]),
            "Python": SkillNode("Python", SkillLevel.INTERMEDIATE, "编程语言"),
            "Spring": SkillNode("Spring", SkillLevel.ADVANCED, "框架", 
                              "Spring框架", ["Spring Boot", "Spring MVC"]),
            "MySQL": SkillNode("MySQL", SkillLevel.INTERMEDIATE, "数据库"),
            "Redis": SkillNode("Redis", SkillLevel.INTERMEDIATE, "缓存"),
            "Docker": SkillNode("Docker", SkillLevel.ADVANCED, "运维"),
            "Kubernetes": SkillNode("Kubernetes", SkillLevel.EXPERT, "运维", 
                                  "容器编排平台", ["K8s"]),
            "微服务": SkillNode("微服务", SkillLevel.ADVANCED, "架构"),
            "分布式": SkillNode("分布式", SkillLevel.ADVANCED, "架构"),
            "高并发": SkillNode("高并发", SkillLevel.ADVANCED, "架构"),
            "架构设计": SkillNode("架构设计", SkillLevel.EXPERT, "架构"),
            "算法": SkillNode("算法", SkillLevel.INTERMEDIATE, "计算机基础"),
            "数据结构": SkillNode("数据结构", SkillLevel.INTERMEDIATE, "计算机基础"),
            "设计模式": SkillNode("设计模式", SkillLevel.ADVANCED, "计算机基础"),
        }

    @classmethod
    def from_jd(cls, jd_data: Dict) -> "AbilityPyramid":
        """从JD关键信息生成能力金字塔"""
        if not jd_data:
            return cls({level: [] for level in SkillLevel})
            
        keywords = jd_data.get("keywords", [])
        requirements = jd_data.get("requirements", [])
        responsibilities = jd_data.get("responsibilities", [])
        
        # 创建实例以访问技能映射
        instance = cls({level: [] for level in SkillLevel})
        
        # 合并所有文本内容进行分析
        all_text = " ".join(keywords + requirements + responsibilities)
        
        # 识别技能并分配层级
        recognized_skills = instance._recognize_skills(all_text)
        
        # 按层级分组
        skills_by_level = {level: [] for level in SkillLevel}
        for skill in recognized_skills:
            skills_by_level[skill.level].append(skill)
            
        return cls(skills_by_level)

    def _recognize_skills(self, text: str) -> List[SkillNode]:
        """从文本中识别技能并分配层级"""
        result = []
        text_lower = text.lower()
        
        # 检查映射表中的每个技能
        for skill_name, skill_node in self.skill_mapping.items():
            # 检查技能名称或别名是否出现在文本中
            if (skill_name.lower() in text_lower or 
                (skill_node.aliases and 
                 any(alias.lower() in text_lower for alias in skill_node.aliases))):
                result.append(skill_node)
                
        # 处理未映射的技能
        words = set(text.split())
        for word in words:
            if (len(word) > 2 and word not in self.skill_mapping and 
                not any(word in skill.name for skill in result)):
                # 尝试根据上下文推断层级
                level = self._infer_skill_level(word, text)
                category = self._infer_skill_category(word)
                result.append(SkillNode(word, level, category))
                
        return result

    def _infer_skill_level(self, skill: str, context: str) -> SkillLevel:
        """根据上下文推断技能层级"""
        context_lower = context.lower()
        skill_lower = skill.lower()
        
        # 基于关键词推断层级
        if any(word in context_lower for word in ["精通", "专家", "深入理解", "源码"]):
            return SkillLevel.EXPERT
        elif any(word in context_lower for word in ["熟练", "掌握", "丰富经验", "架构"]):
            return SkillLevel.ADVANCED
        elif any(word in context_lower for word in ["熟悉", "了解", "使用过", "基础"]):
            return SkillLevel.INTERMEDIATE
        else:
            # 默认层级
            return SkillLevel.BASIC

    def _infer_skill_category(self, skill: str) -> str:
        """推断技能类别"""
        # 简单的基于关键词的类别推断
        skill_lower = skill.lower()
        
        if any(keyword in skill_lower for keyword in ["java", "python", "go", "c++", "编程"]):
            return "编程语言"
        elif any(keyword in skill_lower for keyword in ["spring", "django", "react", "vue", "框架"]):
            return "框架"
        elif any(keyword in skill_lower for keyword in ["mysql", "redis", "oracle", "数据库"]):
            return "数据库"
        elif any(keyword in skill_lower for keyword in ["docker", "k8s", "kubernetes", "运维"]):
            return "运维"
        elif any(keyword in skill_lower for keyword in ["微服务", "分布式", "架构"]):
            return "架构"
        elif any(keyword in skill_lower for keyword in ["算法", "数据结构", "设计模式"]):
            return "计算机基础"
        else:
            return "其他"

    def summarize(self, max_skills_per_level: int = 5) -> str:
        """生成金字塔摘要"""
        lines = ["### 能力金字塔分析"]
        
        for level in SkillLevel:
            skills = self.skills.get(level, [])
            if skills:
                skill_names = [skill.name for skill in skills[:max_skills_per_level]]
                lines.append(f"- {level.value}层 ({len(skills)}项): {', '.join(skill_names)}")
                if len(skills) > max_skills_per_level:
                    lines.append(f"  等{len(skills) - max_skills_per_level}项...")
            else:
                lines.append(f"- {level.value}层: 暂无相关技能要求")
                
        # 添加技能分布统计
        total_skills = sum(len(skills) for skills in self.skills.values())
        if total_skills > 0:
            lines.append("\n技能分布:")
            for level in SkillLevel:
                count = len(self.skills.get(level, []))
                percentage = (count / total_skills) * 100
                lines.append(f"- {level.value}: {count}项 ({percentage:.1f}%)")
                
        return "\n".join(lines)

    def suggest_focus_level(self, score_history: List[float]) -> SkillLevel:
        """根据历史得分建议关注层级"""
        if not score_history:
            return SkillLevel.INTERMEDIATE
            
        # 计算最近3次的平均分
        recent_scores = score_history[-3:] if len(score_history) >= 3 else score_history
        avg_score = sum(recent_scores) / len(recent_scores)
        
        # 根据平均分推荐层级
        if avg_score >= 0.8:
            return SkillLevel.EXPERT
        elif avg_score >= 0.6:
            return SkillLevel.ADVANCED
        elif avg_score >= 0.4:
            return SkillLevel.INTERMEDIATE
        else:
            return SkillLevel.BASIC

    def to_dict(self) -> Dict:
        """转换为字典格式，便于序列化"""
        return {
            level.value: [
                {
                    "name": skill.name,
                    "category": skill.category,
                    "description": skill.description
                }
                for skill in skills
            ]
            for level, skills in self.skills.items()
        }


class JobKnowledgeGraphBuilder:
    """岗位知识图谱构建器

    功能：
    - 从简历与JD中抽取节点，生成关系三元组
    - 支持多种关系类型和权重
    - 提供可视化输出选项
    """

    def __init__(self, resume_data: Dict, jd_data: Dict):
        self.resume_data = resume_data or {}
        self.jd_data = jd_data or {}
        self.nodes: Set[str] = set()
        self.relationships: List[Relationship] = []
        
    def build_graph(self) -> None:
        """构建知识图谱"""
        self._extract_nodes()
        self._build_relationships()
        
    def _extract_nodes(self) -> None:
        """从简历和JD中提取节点"""
        # 从简历提取
        for skill in self.resume_data.get("skills", []):
            self.nodes.add(skill)
            
        for project in self.resume_data.get("projects", []):
            if isinstance(project, dict):
                self.nodes.add(project.get("name", "未知项目"))
            else:
                self.nodes.add(project)
                
        for experience in self.resume_data.get("experiences", []):
            if isinstance(experience, dict):
                self.nodes.add(experience.get("company", "未知公司"))
                self.nodes.add(experience.get("position", "未知职位"))
            else:
                self.nodes.add(experience)
                
        # 从JD提取
        for keyword in self.jd_data.get("keywords", []):
            self.nodes.add(keyword)
            
        for requirement in self.jd_data.get("requirements", []):
            # 简单的提取关键名词
            words = requirement.split()
            for word in words:
                if len(word) > 2 and not word.isdigit():  # 简单的过滤
                    self.nodes.add(word)
                    
        position = self.jd_data.get("position", "")
        if position:
            self.nodes.add(position)

    def _build_relationships(self) -> None:
        """构建节点间的关系"""
        # 技能与项目的关系
        resume_skills = self.resume_data.get("skills", [])
        resume_projects = self.resume_data.get("projects", [])
        
        for skill in resume_skills[:5]:  # 限制数量避免过多关系
            for project in resume_projects[:3]:
                project_name = project if isinstance(project, str) else project.get("name", "")
                if project_name:
                    self.relationships.append(
                        Relationship(skill, "应用于", project_name, 0.7)
                    )
        
        # 技能与经验的关系
        resume_experiences = self.resume_data.get("experiences", [])
        for skill in resume_skills[:3]:
            for exp in resume_experiences[:2]:
                if isinstance(exp, dict):
                    company = exp.get("company", "")
                    if company:
                        self.relationships.append(
                            Relationship(skill, "在...中使用", company, 0.6)
                        )
        
        # JD要求与简历技能的关系
        jd_requirements = self.jd_data.get("requirements", [])
        jd_keywords = self.jd_data.get("keywords", [])
        
        for req in jd_requirements[:5]:
            # 简单的关键词匹配
            for skill in resume_skills:
                if skill.lower() in req.lower():
                    self.relationships.append(
                        Relationship(req, "需要", skill, 0.8)
                    )
                    
        for keyword in jd_keywords:
            for skill in resume_skills:
                if skill.lower() == keyword.lower():
                    self.relationships.append(
                        Relationship("岗位要求", "匹配", skill, 0.9)
                    )
        
        # 添加层级关系
        pyramid = AbilityPyramid.from_jd(self.jd_data)
        pyramid_skills = []
        for level_skills in pyramid.skills.values():
            for skill in level_skills:
                pyramid_skills.append(skill.name)
                
        for i, skill1 in enumerate(pyramid_skills):
            for skill2 in pyramid_skills[i+1:]:
                self.relationships.append(
                    Relationship(skill1, "相关于", skill2, 0.5)
                )

    def get_triplets(self, limit: int = 10) -> List[Tuple[str, str, str]]:
        """获取关系三元组"""
        if not self.relationships:
            self.build_graph()
            
        # 按权重排序并限制数量
        sorted_rels = sorted(self.relationships, key=lambda x: x.weight, reverse=True)
        return [(rel.source, rel.relation, rel.target) for rel in sorted_rels[:limit]]

    def summarize(self, limit: int = 10) -> str:
        """生成知识图谱摘要"""
        triplets = self.get_triplets(limit=limit)
        
        if not triplets:
            return "### 岗位能力知识图谱\n暂无足够数据构建知识图谱"
            
        lines = [
            "### 岗位能力知识图谱",
            f"共发现 {len(self.nodes)} 个节点和 {len(self.relationships)} 条关系",
            "\n关键关系:"
        ]
        
        for i, (source, rel, target) in enumerate(triplets, 1):
            lines.append(f"{i}. {source} -- {rel} --> {target}")
            
        return "\n".join(lines)

    def visualize(self, output_format: str = "text") -> Any:
        """可视化知识图谱（简单实现）"""
        if output_format == "text":
            return self.summarize()
        elif output_format == "json":
            return json.dumps({
                "nodes": list(self.nodes),
                "relationships": [
                    {"source": rel.source, "relation": rel.relation, 
                     "target": rel.target, "weight": rel.weight}
                    for rel in self.relationships
                ]
            }, ensure_ascii=False, indent=2)
        else:
            return "不支持的输出格式"

    def find_skill_gaps(self) -> List[str]:
        """找出简历中缺少但JD要求的技能"""
        if not self.jd_data or not self.resume_data:
            return []
            
        jd_skills = set()
        for keyword in self.jd_data.get("keywords", []):
            jd_skills.add(keyword.lower())
            
        for requirement in self.jd_data.get("requirements", []):
            # 简单的提取名词
            words = requirement.split()
            for word in words:
                if len(word) > 2 and not word.isdigit():
                    jd_skills.add(word.lower())
                    
        resume_skills = set(skill.lower() for skill in self.resume_data.get("skills", []))
        
        # 找出JD要求但简历中没有的技能
        return list(jd_skills - resume_skills)

