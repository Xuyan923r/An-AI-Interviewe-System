# # -*- coding: utf-8 -*-

# class JDAnalyzer:
#     """职位描述分析器"""
#     def __init__(self):
#         self.jd_data = {}

#     def parse_jd(self, jd_text):
#         """解析JD文本，提取关键信息"""
#         self.jd_data = {
#             "position": "",
#             "requirements": [],
#             "responsibilities": [],
#             "skills": [],
#             "experience": "",
#             "education": "",
#             "keywords": []
#         }

#         # 提取职位名称
#         lines = jd_text.split('\n')
#         if lines:
#             self.jd_data["position"] = lines[0].strip()

#         # 关键词匹配提取
#         requirements_keywords = ["要求", "任职要求", "岗位要求", "职位要求"]
#         responsibilities_keywords = ["职责", "工作职责", "岗位职责", "工作内容"]
#         skills_keywords = ["技能", "技术要求", "专业技能", "掌握"]

#         current_section = ""
#         for line in lines[1:]:
#             line = line.strip()
#             if not line:
#                 continue

#             # 判断当前段落类型
#             if any(keyword in line for keyword in requirements_keywords):
#                 current_section = "requirements"
#                 continue
#             elif any(keyword in line for keyword in responsibilities_keywords):
#                 current_section = "responsibilities"
#                 continue
#             elif any(keyword in line for keyword in skills_keywords):
#                 current_section = "skills"
#                 continue

#             # 添加到对应段落
#             if current_section == "requirements":
#                 self.jd_data["requirements"].append(line)
#             elif current_section == "responsibilities":
#                 self.jd_data["responsibilities"].append(line)
#             elif current_section == "skills":
#                 self.jd_data["skills"].append(line)

#         # 提取技术关键词
#         tech_keywords = [
#             "Java", "Python", "JavaScript", "React", "Vue", "Node.js", "Spring", "MySQL",
#             "Redis", "Docker", "Kubernetes", "微服务", "分布式", "高并发", "架构设计",
#             "算法", "数据结构", "设计模式", "Linux", "Git", "Jenkins", "DevOps"
#         ]

#         jd_lower = jd_text.lower()
#         for keyword in tech_keywords:
#             if keyword.lower() in jd_lower:
#                 self.jd_data["keywords"].append(keyword)

#         return self.jd_data

#     def get_jd_summary(self):
#         """获取JD摘要"""
#         if not self.jd_data:
#             return "未解析JD信息"

#         return f"""
# 职位: {self.jd_data['position']}
# 技术要求: {', '.join(self.jd_data['keywords'][:8])}
# 要求数量: {len(self.jd_data['requirements'])}项
# 职责数量: {len(self.jd_data['responsibilities'])}项
# """




# -*- coding: utf-8 -*-
import re
from typing import Dict, List, Any, Optional

class JDAnalyzer:
    """职位描述分析器 - 增强版"""
    
    def __init__(self):
        self.jd_data = {}
        # 预定义关键词库
        self.keyword_lib = {
            "position_keywords": ["岗位", "职位", "招聘", "招募", "聘请", "聘"],
            "requirement_keywords": ["要求", "任职资格", "任职要求", "岗位要求", "职位要求", "基本要求", "必备条件"],
            "responsibility_keywords": ["职责", "工作职责", "岗位职责", "职位职责", "工作内容", "主要职责", "责任"],
            "skill_keywords": ["技能", "技术要求", "专业技能", "技术栈", "掌握", "熟悉", "了解", "必备技能"],
            "experience_keywords": ["经验", "工作经验", "从业经验", "相关经验", "经历", "年限"],
            "education_keywords": ["学历", "教育", "毕业", "学位", "本科", "硕士", "博士", "大专", "中专"],
            "benefit_keywords": ["福利", "待遇", "薪酬", "薪资", "工资", "奖金", "补贴", "五险一金", "社保", "公积金"],
            "location_keywords": ["地点", "位置", "工作地", "办公地点", "城市", "地址"]
        }
        
        # 技术关键词库
        self.tech_keywords = [
            # 编程语言
            "Java", "Python", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Go", "Rust", "Kotlin", "Swift", 
            "Ruby", "Scala", "HTML", "CSS", "SQL", "Shell", "R", "MATLAB",
            # 前端框架
            "React", "Vue", "Angular", "jQuery", "Bootstrap", "SASS", "LESS", "Webpack", "Vite",
            # 后端框架
            "Spring", "Spring Boot", "Spring Cloud", "Django", "Flask", "Express", "Node.js", "NestJS", "MyBatis",
            # 移动开发
            "Android", "iOS", "React Native", "Flutter", "Weex", "小程序",
            # 数据库
            "MySQL", "Oracle", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "Cassandra", "HBase",
            # 云计算与运维
            "Docker", "Kubernetes", "Jenkins", "Git", "CI/CD", "DevOps", "AWS", "Azure", "阿里云", "腾讯云", "华为云",
            "Linux", "Nginx", "Apache", "Tomcat", "Shell", "Ansible", "Prometheus", "Grafana",
            # 大数据与AI
            "Hadoop", "Spark", "Flink", "Kafka", "Hive", "TensorFlow", "PyTorch", "机器学习", "深度学习", "自然语言处理",
            "计算机视觉", "数据分析", "数据挖掘",
            # 架构与模式
            "微服务", "分布式", "高并发", "高可用", "负载均衡", "架构设计", "系统设计", "设计模式", "RESTful", "API设计",
            "消息队列", "服务网格", "云原生"
        ]

    def _extract_section(self, lines: List[str], section_keywords: List[str]) -> List[str]:
        """提取特定部分的文本"""
        section_content = []
        in_section = False
        section_end_keywords = ["职责", "要求", "福利", "待遇", "任职", "岗位", "职位", "工作", "技能", "经验"]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否进入目标部分
            if any(keyword in line for keyword in section_keywords):
                in_section = True
                continue
                
            # 检查是否进入其他部分（结束当前部分）
            if in_section and any(keyword in line for keyword in section_end_keywords):
                # 确保不是当前部分的关键词
                if not any(keyword in line for keyword in section_keywords):
                    in_section = False
                    continue
                    
            # 收集当前部分内容
            if in_section:
                # 跳过明显的标题行
                if len(line) < 20 and any(keyword in line for keyword in self.keyword_lib.values()):
                    continue
                section_content.append(line)
                
        return section_content

    def _extract_with_regex(self, text: str, patterns: List[str]) -> Optional[str]:
        """使用正则表达式提取信息"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
        return None

    def _extract_experience(self, text: str) -> str:
        """提取工作经验要求"""
        patterns = [
            r'(\d+[-–]?\d*[\+]?年以上?工作经验)',
            r'工作经验[：:]\s*(\d+[-–]?\d*[\+]?年)',
            r'(\d+[-–]?\d*[\+]?年)以上?经验',
            r'至少\s*(\d+)\s*年经验',
        ]
        
        result = self._extract_with_regex(text, patterns)
        return result if result else "未明确"

    def _extract_education(self, text: str) -> str:
        """提取学历要求"""
        patterns = [
            r'学历[：:]\s*([大专本科硕士博士及以上]+)',
            r'([大专本科硕士博士及以上]+)[及以上]*学历',
            r'教育背景[：:]\s*([大专本科硕士博士及以上]+)',
        ]
        
        result = self._extract_with_regex(text, patterns)
        return result if result else "未明确"

    def _extract_salary(self, text: str) -> str:
        """提取薪资信息"""
        patterns = [
            r'薪资[：:]\s*([\d万千\-–~～至]+[元kK]?[-–~～至]*[\d万千]*[元kK]?)',
            r'薪酬[：:]\s*([\d万千\-–~～至]+[元kK]?[-–~～至]*[\d万千]*[元kK]?)',
            r'([\d万千\-–~～至]+[元kK]?[-–~～至]*[\d万千]*[元kK]?)[元/月]*[薪待遇]',
        ]
        
        result = self._extract_with_regex(text, patterns)
        return result if result else "面议"

    def _extract_location(self, text: str) -> str:
        """提取工作地点"""
        patterns = [
            r'工作地[点]?[：:]\s*([省市县区\u4e00-\u9fa5]+)',
            r'地点[：:]\s*([省市县区\u4e00-\u9fa5]+)',
            r'位于[：:]\s*([省市县区\u4e00-\u9fa5]+)',
        ]
        
        result = self._extract_with_regex(text, patterns)
        return result if result else "未明确"

    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """对技能进行分类"""
        categorized = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "tools_platforms": [],
            "concepts_methodologies": []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # 编程语言
            if any(lang.lower() in skill_lower for lang in [
                "java", "python", "javascript", "typescript", "c++", "c#", "php", 
                "go", "rust", "kotlin", "swift", "ruby", "scala"
            ]):
                categorized["programming_languages"].append(skill)
                
            # 框架
            elif any(framework.lower() in skill_lower for framework in [
                "react", "vue", "angular", "spring", "django", "flask", "express", 
                "node", "nestjs", "mybatis", "bootstrap", "jquery"
            ]):
                categorized["frameworks"].append(skill)
                
            # 数据库
            elif any(db.lower() in skill_lower for db in [
                "mysql", "oracle", "postgresql", "mongodb", "redis", "elasticsearch", 
                "sqlite", "cassandra", "hbase", "hive"
            ]):
                categorized["databases"].append(skill)
                
            # 工具和平台
            elif any(tool.lower() in skill_lower for tool in [
                "docker", "kubernetes", "jenkins", "git", "aws", "azure", "linux", 
                "nginx", "apache", "tomcat", "ansible"
            ]):
                categorized["tools_platforms"].append(skill)
                
            # 概念和方法论
            elif any(concept.lower() in skill_lower for concept in [
                "微服务", "分布式", "高并发", "高可用", "负载均衡", "架构设计", 
                "设计模式", "restful", "devops", "ci/cd", "敏捷开发"
            ]):
                categorized["concepts_methodologies"].append(skill)
                
        return categorized

    def parse_jd(self, jd_text: str) -> Dict[str, Any]:
        """解析JD文本，提取关键信息"""
        # 初始化数据结构
        self.jd_data = {
            "position": "",
            "requirements": [],
            "responsibilities": [],
            "skills": {
                "all": [],
                "categorized": {}
            },
            "experience": "",
            "education": "",
            "salary": "",
            "location": "",
            "keywords": [],
            "raw_text": jd_text
        }

        try:
            # 分割文本行
            lines = [line.strip() for line in jd_text.split('\n') if line.strip()]
            
            if not lines:
                return self.jd_data
                
            # 提取职位名称（通常在第一行或包含职位关键词的行）
            self.jd_data["position"] = lines[0]
            for line in lines:
                if any(keyword in line for keyword in self.keyword_lib["position_keywords"]):
                    # 提取职位名称（去除关键词本身）
                    for keyword in self.keyword_lib["position_keywords"]:
                        if keyword in line:
                            self.jd_data["position"] = line.replace(keyword, "").strip()
                            break
                    break

            # 提取各个部分
            self.jd_data["requirements"] = self._extract_section(lines, self.keyword_lib["requirement_keywords"])
            self.jd_data["responsibilities"] = self._extract_section(lines, self.keyword_lib["responsibility_keywords"])
            
            # 提取技能部分
            skill_section = self._extract_section(lines, self.keyword_lib["skill_keywords"])
            self.jd_data["skills"]["all"] = skill_section
            
            # 从整个文本中提取技术关键词
            jd_lower = jd_text.lower()
            for keyword in self.tech_keywords:
                if keyword.lower() in jd_lower:
                    self.jd_data["keywords"].append(keyword)
            
            # 对技能进行分类
            all_skills = skill_section + self.jd_data["requirements"]
            self.jd_data["skills"]["categorized"] = self._categorize_skills(
                self.jd_data["keywords"] + all_skills
            )
            
            # 提取其他信息
            full_text = " ".join(lines)
            self.jd_data["experience"] = self._extract_experience(full_text)
            self.jd_data["education"] = self._extract_education(full_text)
            self.jd_data["salary"] = self._extract_salary(full_text)
            self.jd_data["location"] = self._extract_location(full_text)
            
        except Exception as e:
            print(f"解析JD时出错: {str(e)}")
            
        return self.jd_data

    def get_jd_summary(self) -> str:
        """获取JD摘要"""
        if not self.jd_data or not self.jd_data.get("position"):
            return "未解析JD信息或JD格式不正确"

        # 统计信息
        req_count = len(self.jd_data["requirements"])
        resp_count = len(self.jd_data["responsibilities"])
        skill_count = len(self.jd_data["skills"]["all"])
        keyword_count = len(self.jd_data["keywords"])
        
        # 技术分类统计
        categorized = self.jd_data["skills"]["categorized"]
        cat_stats = {cat: len(skills) for cat, skills in categorized.items() if skills}
        
        return f"""
职位: {self.jd_data['position']}
工作地点: {self.jd_data['location']}
经验要求: {self.jd_data['experience']}
学历要求: {self.jd_data['education']}
薪资范围: {self.jd_data['salary']}
----------------------------
要求数量: {req_count}项
职责数量: {resp_count}项
技能数量: {skill_count}项
关键技术: {', '.join(self.jd_data['keywords'][:10])}{'...' if len(self.jd_data['keywords']) > 10 else ''}
技术分类: {', '.join([f'{k}{v}项' for k, v in cat_stats.items()])}
"""

    def get_detailed_analysis(self) -> Dict[str, Any]:
        """获取详细分析报告"""
        if not self.jd_data or not self.jd_data.get("position"):
            return {"error": "未解析JD信息或JD格式不正确"}
            
        return {
            "position_analysis": {
                "title": self.jd_data["position"],
                "location": self.jd_data["location"],
                "experience": self.jd_data["experience"],
                "education": self.jd_data["education"],
                "salary": self.jd_data["salary"]
            },
            "requirements_analysis": {
                "count": len(self.jd_data["requirements"]),
                "items": self.jd_data["requirements"]
            },
            "responsibilities_analysis": {
                "count": len(self.jd_data["responsibilities"]),
                "items": self.jd_data["responsibilities"]
            },
            "skills_analysis": {
                "total_count": len(self.jd_data["skills"]["all"]),
                "categorized": self.jd_data["skills"]["categorized"],
                "keywords": self.jd_data["keywords"]
            },
            "completeness_score": self._calculate_completeness()
        }
    
    def _calculate_completeness(self) -> float:
        """计算JD信息完整度评分"""
        score = 0
        max_score = 100
        
        # 职位名称 (10分)
        if self.jd_data.get("position"):
            score += 10
            
        # 要求部分 (20分)
        if self.jd_data.get("requirements"):
            score += min(20, len(self.jd_data["requirements"]) * 2)
            
        # 职责部分 (20分)
        if self.jd_data.get("responsibilities"):
            score += min(20, len(self.jd_data["responsibilities"]) * 2)
            
        # 技能关键词 (20分)
        if self.jd_data.get("keywords"):
            score += min(20, len(self.jd_data["keywords"]) * 2)
            
        # 其他信息 (30分)
        if self.jd_data.get("experience") and self.jd_data["experience"] != "未明确":
            score += 10
        if self.jd_data.get("education") and self.jd_data["education"] != "未明确":
            score += 10
        if self.jd_data.get("location") and self.jd_data["location"] != "未明确":
            score += 5
        if self.jd_data.get("salary") and self.jd_data["salary"] != "面议":
            score += 5
            
        return round(score / max_score * 100, 1)
