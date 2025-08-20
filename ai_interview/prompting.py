# -*- coding: utf-8 -*-

class DynamicPromptAdjuster:
    """动态提示调整模块，包含Triplet Filter和Demo Selector。

    扩展点：
    - 实体权重衰减-激活机制（近因/高频优先）
    - 行为类型连续性，影响实体权重与示例选择
    - 预留外部知识接入点（如RAG检索、知识库）
    """
    def __init__(self, resume_data):
        self.resume_data = resume_data
        self.key_entities = []
        self.historical_entities = []
        self.historical_acts = []
        self.current_entities = []
        self.current_acts = []
        self.retained_triplets = []
        self.max_triplets = 5
        # 动态权重
        self.entity_weights = {}
        self.decay_rate = 0.85  # 每轮指数衰减
        self.activation_increment = 1.0  # 新出现实体的激活增量
        self.recent_window = 5

    def extract_entities(self):
        entities = []
        if self.resume_data.get("skills"):
            entities.extend(self.resume_data["skills"])
        if self.resume_data.get("projects"):
            for project in self.resume_data["projects"]:
                if "(" in project and ")" in project:
                    techs = project.split("(")[1].split(")")[0].split(",")
                    entities.extend([tech.strip() for tech in techs if len(tech.strip()) > 3])
        self.key_entities = list(set(entities))
        return self.key_entities

    def update_conversation_context(self, user_input, model_output):
        user_entities = self._extract_entities_from_text(user_input)
        self.historical_entities.extend(user_entities)
        model_act = self._classify_question_type(model_output)
        self.historical_acts.append(model_act)
        self._decay_entity_weights()
        self._activate_entities(user_entities)
        self.current_entities = self._predict_entities()

    def _extract_entities_from_text(self, text):
        extracted = []
        for entity in self.key_entities:
            if entity.lower() in text.lower():
                extracted.append(entity)
        return extracted

    def _classify_question_type(self, text):
        question_types = {
            "技术": ["技术", "技能", "编程", "框架", "语言"],
            "项目": ["项目", "经验", "案例", "实施"],
            "行为": ["行为", "情景", "处理", "挑战"],
            "动机": ["动机", "为什么", "原因", "兴趣"],
            "基础": ["介绍", "背景", "教育", "经历"],
        }
        for act, keywords in question_types.items():
            for keyword in keywords:
                if keyword in text:
                    return act
        return "其他"

    def _predict_entities(self):
        if not self.entity_weights and self.historical_entities:
            # 冷启动：基于最近实体
            return list(set(self.historical_entities[-3:]))
        # 综合最近行为与实体权重
        top_entities = sorted(self.entity_weights.items(), key=lambda x: x[1], reverse=True)
        return [e for e, _ in top_entities[:3]] or self.key_entities[:3]

    def _decay_entity_weights(self):
        for k in list(self.entity_weights.keys()):
            self.entity_weights[k] *= self.decay_rate
            if self.entity_weights[k] < 0.01:
                del self.entity_weights[k]

    def _activate_entities(self, entities):
        for e in entities:
            self.entity_weights[e] = self.entity_weights.get(e, 0.0) + self.activation_increment

    def triplet_filter(self):
        initial_triplets = self._generate_initial_triplets()
        # 按实体权重+出现频率排序，兼顾近因高频
        freq = {}
        for h, _, t in initial_triplets:
            freq[h] = freq.get(h, 0) + 1
            freq[t] = freq.get(t, 0) + 1
        def score_triplet(tri):
            h, _, t = tri
            return freq.get(h, 0) + freq.get(t, 0) + \
                   self.entity_weights.get(h, 0.0) + self.entity_weights.get(t, 0.0)
        ranked = sorted(initial_triplets, key=score_triplet, reverse=True)
        self.retained_triplets = ranked[: self.max_triplets]
        return self.retained_triplets

    def _generate_initial_triplets(self):
        triplets = []
        if self.resume_data.get("skills") and self.resume_data.get("projects"):
            for skill in self.resume_data["skills"][:3]:
                for project in self.resume_data["projects"][:2]:
                    triplets.append((skill, "应用于", project))
        if self.resume_data.get("skills") and self.resume_data.get("experience"):
            for skill in self.resume_data["skills"][:3]:
                for exp in self.resume_data["experience"][:2]:
                    triplets.append((skill, "用于", exp))
        if self.resume_data.get("projects"):
            for project in self.resume_data["projects"][:3]:
                parts = project.split("(")
                if len(parts) > 1:
                    techs = parts[1].split(")")[0].split(",")
                    for tech in techs[:3]:
                        triplets.append((project, "使用技术", tech.strip()))
        return triplets

    def demo_selector(self):
        demo = """
        <面试示例>
        面试官: 请介绍一下你在XX项目中的角色和贡献。
        候选人: 在该项目中，我担任后端开发负责人，负责系统架构设计和核心模块实现。
        面试官: 你在项目中遇到的最大技术挑战是什么？如何解决的？
        候选人: 我们面临高并发场景下的性能问题，我通过引入Redis缓存和优化数据库查询解决了问题。
        """
        return demo




