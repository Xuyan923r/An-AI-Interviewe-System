# # -*- coding: utf-8 -*-

# from datetime import datetime
# import sys
# import ollama
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib import colors
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont


# class InterviewReviewManager:
#     """面试复盘和报告管理器"""
#     def __init__(self):
#         self.interview_records = []
#         self.detailed_feedback = []
#         self.overall_assessment = {}

#     def add_qa_record(self, question, answer, score, feedback, stage):
#         record = {
#             "timestamp": datetime.now().strftime("%H:%M:%S"),
#             "stage": stage,
#             "question": question,
#             "answer": answer,
#             "score": score,
#             "feedback": feedback
#         }
#         self.interview_records.append(record)

#     def generate_detailed_feedback(self, answer, question_context, score):
#         try:
#             feedback_prompt = f"""
# 请作为专业面试官，对以下回答给出详细的评价和改进建议：

# 问题背景：{question_context}
# 候选人回答：{answer}
# 当前评分：{score:.2f}

# 请从以下维度给出反馈：
# 1. 回答的完整性和准确性
# 2. 技术深度和理解程度
# 3. 表达清晰度和逻辑性
# 4. 具体的改进建议

# 请用简洁的中文回复，不超过100字。
# """
#             response = ollama.chat(
#                 model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
#                 messages=[{"role": "user", "content": feedback_prompt}]
#             )
#             return response['message']['content'].strip()
#         except Exception:
#             return f"技术掌握程度：{score:.1f}/1.0，建议加强相关技术的深入学习和实践。"

#     def generate_overall_assessment(self, stage_manager, score_manager):
#         self.overall_assessment = {
#             "interview_date": datetime.now().strftime("%Y年%m月%d日"),
#             "total_questions": len(self.interview_records),
#             "overall_score": sum([r["score"] for r in self.interview_records]) / len(self.interview_records) if self.interview_records else 0,
#             "stage_performance": {},
#             "strengths": [],
#             "weaknesses": [],
#             "improvement_suggestions": []
#         }

#         for stage in stage_manager.stages:
#             stage_records = [r for r in self.interview_records if r["stage"] == stage]
#             if stage_records:
#                 avg_score = sum([r["score"] for r in stage_records]) / len(stage_records)
#                 self.overall_assessment["stage_performance"][stage] = {
#                     "questions": len(stage_records),
#                     "avg_score": avg_score
#                 }

#         self._analyze_performance()
#         return self.overall_assessment

#     def _analyze_performance(self):
#         if not self.interview_records:
#             return
#         stage_scores = {}
#         for record in self.interview_records:
#             stage = record["stage"]
#             if stage not in stage_scores:
#                 stage_scores[stage] = []
#             stage_scores[stage].append(record["score"])

#         for stage, scores in stage_scores.items():
#             avg_score = sum(scores) / len(scores)
#             if avg_score >= 0.7:
#                 self.overall_assessment["strengths"].append(f"{stage}表现优秀")
#             elif avg_score < 0.55:
#                 self.overall_assessment["weaknesses"].append(f"{stage}需要加强")

#         overall_score = self.overall_assessment["overall_score"]
#         if overall_score < 0.55:
#             self.overall_assessment["improvement_suggestions"].extend([
#                 "建议加强基础技术知识的学习",
#                 "多做项目实践，积累实际经验",
#                 "提高技术表达和沟通能力"
#             ])
#         elif overall_score < 0.75:
#             self.overall_assessment["improvement_suggestions"].extend([
#                 "继续深化技术理解",
#                 "关注行业前沿技术发展",
#                 "提升系统设计和架构能力"
#             ])
#         else:
#             self.overall_assessment["improvement_suggestions"].extend([
#                 "表现优秀，继续保持",
#                 "可以尝试挑战更高难度的技术领域",
#                 "分享经验，帮助他人成长"
#             ])

#     def export_to_pdf(self, filename, candidate_name, track_name):
#         try:
#             if sys.platform.startswith('darwin'):
#                 try:
#                     pdfmetrics.registerFont(TTFont('PingFang', '/System/Library/Fonts/PingFang.ttc'))
#                     chinese_font = 'PingFang'
#                 except Exception:
#                     try:
#                         pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Light.ttc'))
#                         chinese_font = 'STHeiti'
#                     except Exception:
#                         chinese_font = 'Helvetica'
#             elif sys.platform.startswith('win'):
#                 try:
#                     pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
#                     chinese_font = 'SimSun'
#                 except Exception:
#                     try:
#                         pdfmetrics.registerFont(TTFont('Microsoft YaHei', 'C:/Windows/Fonts/msyh.ttc'))
#                         chinese_font = 'Microsoft YaHei'
#                     except Exception:
#                         chinese_font = 'Helvetica'
#             else:
#                 try:
#                     pdfmetrics.registerFont(TTFont('WenQuanYi', '/usr/share/fonts/wenquanyi/wqy-zenhei.ttc'))
#                     chinese_font = 'WenQuanYi'
#                 except Exception:
#                     chinese_font = 'Helvetica'

#             doc = SimpleDocTemplate(filename, pagesize=A4)
#             styles = getSampleStyleSheet()

#             title_style = ParagraphStyle(
#                 'CustomTitle', parent=styles['Heading1'], fontName=chinese_font, fontSize=18, spaceAfter=30, alignment=1
#             )
#             heading_style = ParagraphStyle(
#                 'CustomHeading', parent=styles['Heading2'], fontName=chinese_font, fontSize=14, spaceAfter=12
#             )
#             normal_style = ParagraphStyle(
#                 'CustomNormal', parent=styles['Normal'], fontName=chinese_font, fontSize=10, spaceAfter=6
#             )

#             content = []
#             content.append(Paragraph(f"AI面试报告 - {candidate_name}", title_style))
#             content.append(Spacer(1, 20))

#             content.append(Paragraph("基本信息", heading_style))
#             basic_info = [
#                 ["面试日期", self.overall_assessment.get("interview_date", "")],
#                 ["面试赛道", track_name],
#                 ["总题数", str(self.overall_assessment.get("total_questions", 0))],
#                 ["综合得分", f"{self.overall_assessment.get('overall_score', 0):.2f}/1.00"],
#             ]
#             basic_table = Table(basic_info, colWidths=[2*inch, 3*inch])
#             basic_table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('FONTNAME', (0, 0), (-1, -1), chinese_font),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black)
#             ]))
#             content.append(basic_table)
#             content.append(Spacer(1, 20))

#             content.append(Paragraph("评估报告", heading_style))
#             if hasattr(self, 'full_evaluation'):
#                 content.append(Paragraph(self.full_evaluation, normal_style))
#             content.append(Spacer(1, 20))

#             content.append(Paragraph("各阶段表现", heading_style))
#             stage_data = [["阶段", "题数", "平均分"]]
#             for stage, performance in self.overall_assessment.get("stage_performance", {}).items():
#                 stage_data.append([stage, str(performance["questions"]), f"{performance['avg_score']:.2f}"])
#             stage_table = Table(stage_data, colWidths=[2*inch, 1*inch, 1*inch])
#             stage_table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, -1), chinese_font),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black)
#             ]))
#             content.append(stage_table)
#             content.append(Spacer(1, 20))

#             content.append(Paragraph("详细问答记录", heading_style))
#             for i, record in enumerate(self.interview_records):
#                 content.append(Paragraph(f"第{i+1}题 [{record['stage']}]", normal_style))
#                 content.append(Paragraph(f"问题：{record['question']}", normal_style))
#                 content.append(Paragraph(f"回答：{record['answer'][:200]}...", normal_style))
#                 content.append(Paragraph(f"得分：{record['score']:.2f}", normal_style))
#                 content.append(Paragraph(f"反馈：{record['feedback']}", normal_style))
#                 content.append(Spacer(1, 10))

#             content.append(Paragraph("综合评价", heading_style))
#             strengths = self.overall_assessment.get("strengths", [])
#             if strengths:
#                 content.append(Paragraph("优势：", normal_style))
#                 for strength in strengths:
#                     content.append(Paragraph(f"• {strength}", normal_style))

#             weaknesses = self.overall_assessment.get("weaknesses", [])
#             if weaknesses:
#                 content.append(Paragraph("待改进：", normal_style))
#                 for weakness in weaknesses:
#                     content.append(Paragraph(f"• {weakness}", normal_style))

#             suggestions = self.overall_assessment.get("improvement_suggestions", [])
#             if suggestions:
#                 content.append(Paragraph("改进建议：", normal_style))
#                 for suggestion in suggestions:
#                     content.append(Paragraph(f"• {suggestion}", normal_style))

#             doc.build(content)
#             return True
#         except Exception as e:
#             print(f"PDF导出失败: {e}")
#             return False





# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import ollama
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class InterviewReviewManager:
    """增强版面试复盘和报告管理器"""
    def __init__(self):
        self.interview_records = []
        self.overall_assessment = {}

    # -------------------- 基础功能 --------------------
    def add_qa_record(self, question, answer, score, feedback, stage):
        record = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "stage": stage,
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback
        }
        self.interview_records.append(record)

    def generate_overall_assessment(self, stages=None):
        self.overall_assessment = {
            "interview_date": datetime.now().strftime("%Y年%m月%d日"),
            "total_questions": len(self.interview_records),
            "overall_score": sum([r["score"] for r in self.interview_records]) / len(self.interview_records) if self.interview_records else 0,
            "stage_performance": {},
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }

        if stages:
            for stage in stages:
                stage_records = [r for r in self.interview_records if r["stage"] == stage]
                if stage_records:
                    avg_score = sum([r["score"] for r in stage_records]) / len(stage_records)
                    self.overall_assessment["stage_performance"][stage] = avg_score

        self._analyze_performance()
        return self.overall_assessment

    def _analyze_performance(self):
        if not self.interview_records:
            return
        # 阶段表现分析
        for stage, avg_score in self.overall_assessment.get("stage_performance", {}).items():
            if avg_score >= 0.7:
                self.overall_assessment["strengths"].append(f"{stage}表现优秀")
            elif avg_score < 0.55:
                self.overall_assessment["weaknesses"].append(f"{stage}需要加强")
        # 综合建议
        overall_score = self.overall_assessment["overall_score"]
        if overall_score < 0.55:
            self.overall_assessment["improvement_suggestions"].extend([
                "建议加强基础技术知识的学习",
                "多做项目实践，积累实际经验",
                "提高技术表达和沟通能力"
            ])
        elif overall_score < 0.75:
            self.overall_assessment["improvement_suggestions"].extend([
                "继续深化技术理解",
                "关注行业前沿技术发展",
                "提升系统设计和架构能力"
            ])
        else:
            self.overall_assessment["improvement_suggestions"].extend([
                "表现优秀，继续保持",
                "可以尝试挑战更高难度的技术领域",
                "分享经验，帮助他人成长"
            ])

    # -------------------- 可视化 --------------------
    def _generate_skill_radar_chart(self, skill_scores):
        skills = list(skill_scores.keys())
        values = list(skill_scores.values())
        values += values[:1]  # 封闭雷达图
        angles = [n / float(len(skills)) * 2 * 3.1416 for n in range(len(skills))]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
        ax.plot(angles, values, linewidth=2, linestyle='solid')
        ax.fill(angles, values, 'skyblue', alpha=0.4)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills, fontsize=8)
        ax.set_yticks([0.2,0.4,0.6,0.8,1.0])
        ax.set_yticklabels([])
        buf = BytesIO()
        plt.savefig(buf, format='PNG', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _generate_stage_bar_chart(self, stage_scores):
        stages = list(stage_scores.keys())
        scores = list(stage_scores.values())
        fig, ax = plt.subplots(figsize=(6,2))
        ax.bar(stages, scores, color='skyblue')
        ax.set_ylim(0,1)
        ax.set_ylabel('平均分')
        for i, v in enumerate(scores):
            ax.text(i, v + 0.02, f"{v:.2f}", ha='center')
        buf = BytesIO()
        plt.savefig(buf, format='PNG', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    # -------------------- PDF 导出 --------------------
    def export_to_pdf(self, filename, candidate_name, track_name, skill_scores=None):
        try:
            # 字体注册
            if sys.platform.startswith('win'):
                try:
                    pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
                    chinese_font = 'SimSun'
                except Exception:
                    chinese_font = 'Helvetica'
            else:
                chinese_font = 'Helvetica'

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontName=chinese_font, fontSize=18, spaceAfter=20, alignment=1)
            heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontName=chinese_font, fontSize=14, spaceAfter=12)
            normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontName=chinese_font, fontSize=10, spaceAfter=6)

            content = []
            content.append(Paragraph(f"AI面试报告 - {candidate_name}", title_style))
            content.append(Spacer(1, 12))

            # 基本信息
            content.append(Paragraph("基本信息", heading_style))
            basic_info = [
                ["面试日期", self.overall_assessment.get("interview_date", "")],
                ["面试赛道", track_name],
                ["总题数", str(self.overall_assessment.get("total_questions", 0))],
                ["综合得分", f"{self.overall_assessment.get('overall_score',0):.2f}/1.00"]
            ]
            table = Table(basic_info, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME',(0,0),(-1,-1),chinese_font),
                ('FONTSIZE',(0,0),(-1,-1),10),
                ('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('GRID',(0,0),(-1,-1),1,colors.black)
            ]))
            content.append(table)
            content.append(Spacer(1,12))

            # 技能雷达图
            if skill_scores:
                radar_buf = self._generate_skill_radar_chart(skill_scores)
                content.append(Paragraph("技能掌握雷达图", heading_style))
                content.append(Image(radar_buf, width=200, height=200))
                content.append(Spacer(1,12))

            # 阶段柱状图
            stage_scores = self.overall_assessment.get("stage_performance", {})
            if stage_scores:
                stage_buf = self._generate_stage_bar_chart(stage_scores)
                content.append(Paragraph("各阶段平均分柱状图", heading_style))
                content.append(Image(stage_buf, width=400, height=120))
                content.append(Spacer(1,12))

            # 详细问答
            content.append(Paragraph("详细问答记录", heading_style))
            for i, r in enumerate(self.interview_records):
                score_color = colors.red if r["score"] < 0.55 else colors.black
                content.append(Paragraph(f"第{i+1}题 [{r['stage']}]", normal_style))
                content.append(Paragraph(f"问题：{r['question']}", normal_style))
                content.append(Paragraph(f"回答：{r['answer'][:200]}...", normal_style))
                content.append(Paragraph(f"得分：{r['score']:.2f}", normal_style))
                content.append(Paragraph(f"反馈：{r['feedback']}", normal_style))
                content.append(Spacer(1,6))

            # 综合评价
            content.append(Paragraph("综合评价", heading_style))
            for key in ["strengths","weaknesses","improvement_suggestions"]:
                items = self.overall_assessment.get(key, [])
                if items:
                    content.append(Paragraph(key, normal_style))
                    for item in items:
                        content.append(Paragraph(f"• {item}", normal_style))
            doc.build(content)
            return True
        except Exception as e:
            print(f"PDF导出失败: {e}")
            return False
