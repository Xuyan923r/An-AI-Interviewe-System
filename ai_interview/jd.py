# -*- coding: utf-8 -*-

class JDAnalyzer:
    """职位描述分析器"""
    def __init__(self):
        self.jd_data = {}

    def parse_jd(self, jd_text):
        """解析JD文本，提取关键信息"""
        self.jd_data = {
            "position": "",
            "requirements": [],
            "responsibilities": [],
            "skills": [],
            "experience": "",
            "education": "",
            "keywords": []
        }

        # 提取职位名称
        lines = jd_text.split('\n')
        if lines:
            self.jd_data["position"] = lines[0].strip()

        # 关键词匹配提取
        requirements_keywords = ["要求", "任职要求", "岗位要求", "职位要求"]
        responsibilities_keywords = ["职责", "工作职责", "岗位职责", "工作内容"]
        skills_keywords = ["技能", "技术要求", "专业技能", "掌握"]

        current_section = ""
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # 判断当前段落类型
            if any(keyword in line for keyword in requirements_keywords):
                current_section = "requirements"
                continue
            elif any(keyword in line for keyword in responsibilities_keywords):
                current_section = "responsibilities"
                continue
            elif any(keyword in line for keyword in skills_keywords):
                current_section = "skills"
                continue

            # 添加到对应段落
            if current_section == "requirements":
                self.jd_data["requirements"].append(line)
            elif current_section == "responsibilities":
                self.jd_data["responsibilities"].append(line)
            elif current_section == "skills":
                self.jd_data["skills"].append(line)

        # 提取技术关键词
        tech_keywords = [
            "Java", "Python", "JavaScript", "React", "Vue", "Node.js", "Spring", "MySQL",
            "Redis", "Docker", "Kubernetes", "微服务", "分布式", "高并发", "架构设计",
            "算法", "数据结构", "设计模式", "Linux", "Git", "Jenkins", "DevOps"
        ]

        jd_lower = jd_text.lower()
        for keyword in tech_keywords:
            if keyword.lower() in jd_lower:
                self.jd_data["keywords"].append(keyword)

        return self.jd_data

    def get_jd_summary(self):
        """获取JD摘要"""
        if not self.jd_data:
            return "未解析JD信息"

        return f"""
职位: {self.jd_data['position']}
技术要求: {', '.join(self.jd_data['keywords'][:8])}
要求数量: {len(self.jd_data['requirements'])}项
职责数量: {len(self.jd_data['responsibilities'])}项
"""


