# -*- coding: utf-8 -*-

import time
import json
import math
import threading
import queue
import os
import tkinter as tk
from tkinter import scrolledtext, font, ttk, filedialog, messagebox
import ollama

from .scoring import ScoreAndDifficultyManager
from .questions import QuestionBankManager
from .stages import ThreeStageInterviewManager
from .jd import JDAnalyzer
from .review import InterviewReviewManager
from .resume import ResumeParser
from .prompting import DynamicPromptAdjuster
from .knowledge import AbilityPyramid, JobKnowledgeGraphBuilder


class InteractiveTextApp:
    def __init__(self, root, solution):
        self.root = root
        self.solution = solution
        self.root.title("AI面试智能官")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        # 主题与色板（light/dark）
        self.theme = "light"
        self.theme_palettes = {
            "light": {
                "bg": "#f7f8fa",
                "card": "#ffffff",
                "text": "#1f2937",
                "muted": "#6b7280",
                "primary": "#2ecc71",
                "accent": "#3498db",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "info": "#9b59b6"
            },
            "dark": {
                "bg": "#0f172a",
                "card": "#111827",
                "text": "#e5e7eb",
                "muted": "#9ca3af",
                "primary": "#22c55e",
                "accent": "#60a5fa",
                "warning": "#fbbf24",
                "danger": "#ef4444",
                "info": "#a78bfa"
            }
        }
        # 全局ttk样式实例
        self.style = ttk.Style()
        self.dynamic_prompt_adjuster = None
        self.conversation_context = []
        self.score_manager = ScoreAndDifficultyManager()
        self.question_bank_manager = QuestionBankManager()
        self.stage_manager = ThreeStageInterviewManager()
        self.jd_analyzer = JDAnalyzer()
        self.review_manager = InterviewReviewManager()
        self.parser = ResumeParser()
        self.ability_pyramid = None
        self.job_graph_builder = None
        self.last_question = ""
        self.selected_track = None
        self.jd_data = None
        self.resume_data = None

        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        try:
            import sys
            if sys.platform.startswith('win'):
                self.default_family = "Microsoft YaHei"
            elif sys.platform.startswith('darwin'):
                self.default_family = "PingFang SC"
            else:
                self.default_family = "WenQuanYi Micro Hei"
        except Exception:
            self.default_family = "Helvetica"

        self.custom_font = font.Font(family=self.default_family, size=16)
        self.small_font = font.Font(family=self.default_family, size=12)
        self.title_font = font.Font(family=self.default_family, size=18, weight="bold")

        title_label = tk.Label(
            main_frame, text="AI面试智能官", font=(self.default_family, 22, "bold"), bg="#f0f0f0", fg="#2c3e50"
        )
        title_label.pack(pady=6)
        subtitle_label = tk.Label(
            main_frame, text="三阶段 · 动态难度 · 知识图谱驱动", font=(self.default_family, 12), bg="#f0f0f0", fg="#6b7280"
        )
        subtitle_label.pack(pady=(0, 8))

        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)

        self.upload_btn = ttk.Button(button_frame, text="上传简历", command=self.upload_resume)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.upload_jd_btn = ttk.Button(button_frame, text="上传JD", command=self.upload_jd)
        self.upload_jd_btn.pack(side=tk.LEFT, padx=5)

        self.track_select_btn = ttk.Button(button_frame, text="选择赛道", command=self.select_track)
        self.track_select_btn.pack(side=tk.LEFT, padx=5)

        self.start_interview_btn = ttk.Button(button_frame, text="开始面试", command=self.start_interview)
        self.start_interview_btn.configure(state=tk.DISABLED)
        self.start_interview_btn.pack(side=tk.LEFT, padx=5)

        self.end_interview_btn = ttk.Button(button_frame, text="结束面试", command=self.end_interview)
        self.end_interview_btn.configure(state=tk.DISABLED)
        self.end_interview_btn.pack(side=tk.LEFT, padx=5)

        self.review_btn = ttk.Button(button_frame, text="面试复盘", command=self.show_interview_review)
        self.review_btn.configure(state=tk.DISABLED)
        self.review_btn.pack(side=tk.LEFT, padx=5)

        self.export_pdf_btn = ttk.Button(button_frame, text="导出PDF", command=self.export_interview_pdf)
        self.export_pdf_btn.configure(state=tk.DISABLED)
        self.export_pdf_btn.pack(side=tk.LEFT, padx=5)
        # 主题切换按钮
        self.theme_btn = ttk.Button(button_frame, text="切换主题", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

        info_frame = ttk.LabelFrame(main_frame, text="候选人信息")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        self.info_label = tk.Label(info_frame, text="请上传简历以查看候选人信息", font=self.small_font, bg="#f0f0f0", fg="#7f8c8d", justify=tk.LEFT, wraplength=900)
        self.info_label.pack(fill=tk.X, padx=10, pady=5)

        track_frame = ttk.LabelFrame(main_frame, text="面试赛道")
        track_frame.pack(fill=tk.X, pady=(0, 10))
        self.track_info_label = tk.Label(track_frame, text="请选择面试赛道", font=("Helvetica", 12, "bold"), bg="#f0f0f0", fg="#9b59b6", justify=tk.LEFT, wraplength=900)
        self.track_info_label.pack(fill=tk.X, padx=10, pady=5)

        stage_frame = ttk.LabelFrame(main_frame, text="面试阶段")
        stage_frame.pack(fill=tk.X, pady=(0, 10))
        self.stage_info_label = tk.Label(stage_frame, text="当前阶段: 等待开始", font=("Helvetica", 12, "bold"), bg="#f0f0f0", fg="#e67e22", justify=tk.LEFT)
        self.stage_info_label.pack(fill=tk.X, padx=10, pady=5)

        score_frame = ttk.LabelFrame(main_frame, text="面试状态")
        score_frame.pack(fill=tk.X, pady=(0, 10))
        left_score_frame = tk.Frame(score_frame, bg="#f0f0f0")
        left_score_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        right_score_frame = tk.Frame(score_frame, bg="#f0f0f0")
        right_score_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        self.difficulty_label = tk.Label(left_score_frame, text="系统智能调节中", font=(self.default_family, 12, "bold"), bg="#f0f0f0", fg="#3498db")
        self.difficulty_label.pack(anchor=tk.W, pady=2)
        self.latest_score_label = tk.Label(left_score_frame, text="面试进行中...", font=self.small_font, bg="#f0f0f0", fg="#2ecc71")
        self.latest_score_label.pack(anchor=tk.W, pady=2)
        self.avg_score_label = tk.Label(right_score_frame, text="实时分析中...", font=self.small_font, bg="#f0f0f0", fg="#f39c12")
        self.avg_score_label.pack(anchor=tk.W, pady=2)
        self.question_count_label = tk.Label(right_score_frame, text="问题数: 0", font=self.small_font, bg="#f0f0f0", fg="#9b59b6")
        self.question_count_label.pack(anchor=tk.W, pady=2)

        text_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.GROOVE)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=70, height=18, state='disabled', font=self.custom_font, bg="#ffffff", fg="#333333", padx=15, pady=15)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.display_text("欢迎使用AI面试智能官！\n请按以下步骤操作：\n1. 上传简历\n2. 上传JD职位描述\n3. 选择面试赛道\n4. 开始面试\n\n面试过程中系统会智能分析您的回答，请放心作答。")

        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, pady=10)
        self.status_label = tk.Label(control_frame, text="准备就绪", font=self.small_font, bg="#f0f0f0", fg="#7f8c8d")
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.time_label = tk.Label(control_frame, text="0.0s", font=self.small_font, bg="#f0f0f0", fg="#7f8c8d", width=6)
        self.time_label.pack(side=tk.LEFT, padx=10)

        help_frame = tk.Frame(main_frame, bg="#f0f0f0")
        help_frame.pack(fill=tk.X, pady=5)
        self.help_label = tk.Label(help_frame, text="按住空格键开始录音，松开结束录音", font=("Helvetica", 12, "italic"), bg="#f0f0f0", fg="#3498db")
        self.help_label.pack()

        self.root.bind("<KeyPress-space>", self.start_recording)
        self.root.bind("<KeyRelease-space>", self.stop_recording)
        self.root.focus_set()

        self.message_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.start_queue_listener()
        self.model_thread = threading.Thread(target=self.process_model_responses, daemon=True)
        self.model_thread.start()
        self.check_interview_ready()
        self.recording_start_time = 0
        self.progress_active = False
        self.is_processing = False
        self.interview_active = False
        self.resume_data = None
        self.parser = ResumeParser()
        self.conversation_history = []
        self.initial_prompt_set = False
        self.question_count = 0
        self.first_question_asked = False
        self.key_topics = []

        # 记录主题相关容器以便统一美化
        self._containers = {
            "root": self.root,
            "frames": [main_frame, button_frame, info_frame, track_frame, stage_frame, score_frame, left_score_frame, right_score_frame, text_frame, control_frame, help_frame],
            "labels": [title_label, self.info_label, self.track_info_label, self.stage_info_label, self.difficulty_label, self.latest_score_label, self.avg_score_label, self.question_count_label, self.status_label, self.time_label, self.help_label],
            "buttons": [self.upload_btn, self.upload_jd_btn, self.track_select_btn, self.start_interview_btn, self.end_interview_btn, self.review_btn, self.export_pdf_btn, self.theme_btn],
            "text": self.text_area,
            "progress": self.progress_bar
        }
        self.apply_theme(self.theme)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(self.theme)

    def apply_theme(self, theme_name):
        colors = self.theme_palettes.get(theme_name, self.theme_palettes["light"])
        try:
            self.root.configure(bg=colors["bg"])
        except Exception:
            pass
        for frame in self._containers.get("frames", []):
            try:
                frame.configure(bg=colors["bg"]) if isinstance(frame, tk.Frame) else None
            except Exception:
                pass
        for lbl in self._containers.get("labels", []):
            try:
                lbl.configure(bg=colors["bg"], fg=colors["text"])
            except Exception:
                pass
        for btn in self._containers.get("buttons", []):
            try:
                btn.configure(bg=colors["accent"], fg="#ffffff", activebackground=colors["primary"], activeforeground="#ffffff")
            except Exception:
                pass
        # 特殊区块：卡片背景
        try:
            self._set_card_bg(self._containers["frames"], colors)
        except Exception:
            pass
        # 文本区域
        try:
            self._containers["text"].configure(bg=colors["card"], fg=colors["text"])
        except Exception:
            pass
        # 进度条配色
        try:
            style = ttk.Style()
            style.theme_use('default')
            style.configure("Custom.Horizontal.TProgressbar", troughcolor=colors["card"], background=colors["primary"], bordercolor=colors["card"])
            self._containers["progress"].configure(style="Custom.Horizontal.TProgressbar")
        except Exception:
            pass

    def _set_card_bg(self, frames, colors):
        # 将 LabelFrame 边框与内部背景调至卡片样式
        for frame in frames:
            if isinstance(frame, tk.LabelFrame):
                try:
                    frame.configure(bg=colors["bg"], fg=colors["text"])
                except Exception:
                    pass
            # 内部的容器可保持卡片感
            if isinstance(frame, tk.Frame):
                for child in frame.winfo_children():
                    if isinstance(child, tk.Frame) and child not in self._containers.get("frames", []):
                        try:
                            child.configure(bg=colors["card"])  # 内部次级容器
                        except Exception:
                            pass

    # 赛道与数据准备
    def select_track(self):
        track_window = tk.Toplevel(self.root)
        track_window.title("选择面试赛道")
        track_window.geometry("400x300")
        track_window.configure(bg="#f0f0f0")
        track_window.transient(self.root)
        track_window.grab_set()
        title_label = tk.Label(track_window, text="请选择面试赛道", font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title_label.pack(pady=20)
        tracks = ["后端", "前端", "算法", "测试", "产品", "运营"]
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
        for i, track in enumerate(tracks):
            btn = tk.Button(
                track_window,
                text=f"🎯 {track}",
                command=lambda t=track: self.confirm_track_selection(t, track_window),
                font=("Helvetica", 12, "bold"),
                bg=colors[i % len(colors)], fg="white", padx=20, pady=10, relief=tk.FLAT, width=15
            )
            btn.pack(pady=5)

    def confirm_track_selection(self, track, window):
        self.selected_track = track
        self.question_bank_manager.set_track(track)
        track_summary = self.question_bank_manager.get_track_summary()
        self.track_info_label.config(text=f"已选择: {track} 赛道\n{track_summary}", fg="#2ecc71")
        self.check_interview_ready()
        self.display_text(f"已选择 {track} 赛道！题库已加载完成。")
        window.destroy()

    def upload_jd(self):
        jd_window = tk.Toplevel(self.root)
        jd_window.title("输入职位描述(JD)")
        jd_window.geometry("600x420")
        jd_window.minsize(520, 360)
        jd_window.configure(bg="#f0f0f0")
        jd_window.transient(self.root)
        jd_window.grab_set()

        # 使用网格布局，确保在不同平台窗口缩放时按钮不被遮挡
        jd_window.rowconfigure(1, weight=1)
        jd_window.columnconfigure(0, weight=1)

        title_label = tk.Label(
            jd_window,
            text="请输入职位描述(JD)信息",
            font=(self.default_family, 14, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="w")

        jd_text = scrolledtext.ScrolledText(
            jd_window,
            wrap=tk.WORD,
            width=70,
            height=12,
            font=(self.default_family, 12)
        )
        jd_text.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")

        btn_frame = tk.Frame(jd_window, bg="#f0f0f0")
        btn_frame.grid(row=2, column=0, padx=16, pady=(6, 12), sticky="e")

        def confirm_jd():
            jd_content = jd_text.get("1.0", tk.END).strip()
            if jd_content:
                self.jd_data = self.jd_analyzer.parse_jd(jd_content)
                # 构建能力金字塔与知识图谱（占位，可替换为外部数据）
                self.ability_pyramid = AbilityPyramid.from_jd(self.jd_data)
                if self.resume_data:
                    self.job_graph_builder = JobKnowledgeGraphBuilder(self.resume_data, self.jd_data)
                jd_summary = self.jd_analyzer.get_jd_summary()
                ability_summary = self.ability_pyramid.summarize() if self.ability_pyramid else ""
                graph_summary = self.job_graph_builder.summarize(limit=6) if self.job_graph_builder else ""
                self.display_text(f"JD解析完成！\n{jd_summary}\n{ability_summary}\n{graph_summary}")
                self.check_interview_ready()
                jd_window.destroy()
            else:
                tk.messagebox.showerror("错误", "请输入JD内容")

        # 使用 ttk.Button 以获得更好的跨平台一致性
        confirm_btn = ttk.Button(btn_frame, text="确认", command=confirm_jd)
        confirm_btn.pack(side=tk.RIGHT, padx=(8, 0))
        cancel_btn = ttk.Button(btn_frame, text="取消", command=jd_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))

    def upload_resume(self):
        file_path = filedialog.askopenfilename(title="选择简历文件", filetypes=[("PDF文件", "*.pdf"), ("Word文件", "*.docx"), ("所有文件", "*.*")])
        if file_path:
            self.display_text(f"正在解析简历: {os.path.basename(file_path)}...")
            self.resume_data = self.parser.parse_resume(file_path)
            if isinstance(self.resume_data, dict):
                info_text = f"姓名: {self.resume_data['name']}\n"
                info_text += f"联系方式: {self.resume_data['contact']}\n"
                info_text += f"教育背景: {len(self.resume_data['education'])}项\n"
                info_text += f"工作经验: {len(self.resume_data['experience'])}项\n"
                info_text += f"技能: {len(self.resume_data['skills'])}项"
                self.info_label.config(text=info_text)
                self.display_text("简历解析完成！")
                self.resume_data = self.resume_data
                self.dynamic_prompt_adjuster = DynamicPromptAdjuster(self.resume_data)
                entities = self.parser.extract_entities(file_path)
                if entities:
                    self.dynamic_prompt_adjuster.key_entities = entities
                    self.display_text(f"已提取关键实体: {', '.join(entities[:5])}...")
                else:
                    self.display_text("未提取到关键实体。")
                # 如果JD已存在，构建知识图谱
                if self.jd_data:
                    self.job_graph_builder = JobKnowledgeGraphBuilder(self.resume_data, self.jd_data)
            else:
                self.display_text(f"简历解析失败: {self.resume_data}")

    def start_interview(self):
        if not self.resume_data:
            self.display_text("请先上传简历！")
            return
        if not self.selected_track:
            self.display_text("请先选择面试赛道！")
            return
        if not self.jd_data:
            self.display_text("请先上传JD！")
            return
        self.interview_active = True
        self.question_count = 0
        self.first_question_asked = False
        self.score_manager = ScoreAndDifficultyManager()
        self.stage_manager = ThreeStageInterviewManager()
        self.review_manager = InterviewReviewManager()
        self.update_status_display()
        current_stage = self.stage_manager.get_current_stage()
        self.stage_info_label.config(text=f"当前阶段: {current_stage} (第1题)")
        self.display_text("面试已开始！请准备回答面试官的问题。")
        self.display_text(f"📍 当前阶段: {current_stage}")
        self.end_interview_btn.config(state=tk.NORMAL)
        self.start_interview_btn.config(state=tk.DISABLED)
        self.review_btn.config(state=tk.DISABLED)
        self.export_pdf_btn.config(state=tk.DISABLED)
        self.conversation_history = []
        self.initial_prompt_set = False
        self.input_queue.put("start_interview")

    def end_interview(self):
        self.interview_active = False
        self.display_text("面试已结束！感谢参与。")
        score_summary = self.score_manager.get_score_summary()
        difficulty_progression = self.score_manager.get_difficulty_progression()
        self.display_text("\n" + "="*50)
        self.display_text("📊 面试评分总结")
        self.display_text("="*50)
        self.display_text(score_summary)
        self.display_text(difficulty_progression)
        self.display_text("="*50)
        self.end_interview_btn.config(state=tk.DISABLED)
        self.start_interview_btn.config(state=tk.NORMAL)
        self.input_queue.put("end_interview")
        self.review_btn.config(state=tk.NORMAL)
        self.export_pdf_btn.config(state=tk.NORMAL)

    def show_interview_review(self):
        if not self.review_manager.interview_records:
            tk.messagebox.showinfo("提示", "暂无面试记录")
            return
        if hasattr(self, 'full_evaluation'):
            assessment = self.full_evaluation
        else:
            assessment = self.review_manager.generate_overall_assessment(self.stage_manager, self.score_manager)
        review_window = tk.Toplevel(self.root)
        review_window.title("面试复盘分析")
        review_window.geometry("800x600")
        review_window.configure(bg="#f0f0f0")
        review_text = scrolledtext.ScrolledText(review_window, wrap=tk.WORD, width=90, height=35, font=("Helvetica", 10), bg="#ffffff", fg="#333333")
        review_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        review_content = f"""
🎯 面试复盘报告
{'='*60}

📅 面试日期: {assessment['interview_date']}
📊 总题数: {assessment['total_questions']}题
🎯 综合得分: {assessment['overall_score']:.2f}/1.00

{'='*60}
📈 各阶段表现分析
{'='*60}
"""
        for stage, performance in assessment['stage_performance'].items():
            review_content += f"""
🔸 {stage}:
   - 题目数量: {performance['questions']}题
   - 平均得分: {performance['avg_score']:.2f}/1.00
   - 表现评价: {'优秀' if performance['avg_score'] >= 0.75 else '良好' if performance['avg_score'] >= 0.6 else '一般' if performance['avg_score'] >= 0.5 else '需改进'}
"""
        review_content += f"""
{'='*60}
✅ 优势表现
{'='*60}
"""
        for strength in assessment['strengths']:
            review_content += f"• {strength}\n"
        if not assessment['strengths']:
            review_content += "建议在各个方面继续努力\n"
        review_content += f"""
{'='*60}
⚠️ 待改进方面
{'='*60}
"""
        for weakness in assessment['weaknesses']:
            review_content += f"• {weakness}\n"
        if not assessment['weaknesses']:
            review_content += "整体表现良好\n"
        review_content += f"""
{'='*60}
💡 改进建议
{'='*60}
"""
        for suggestion in assessment['improvement_suggestions']:
            review_content += f"• {suggestion}\n"
        review_content += f"""
{'='*60}
📝 详细问答记录
{'='*60}
"""
        for i, record in enumerate(self.review_manager.interview_records):
            review_content += f"""
第{i+1}题 [{record['stage']}] - {record['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ 问题: {record['question']}

💬 回答: {record['answer']}

📊 得分: {record['score']:.2f}/1.00

💭 反馈: {record['feedback']}

"""
        review_text.insert(tk.END, review_content)
        review_text.config(state='disabled')

    def export_interview_pdf(self):
        if not self.review_manager.interview_records:
            tk.messagebox.showinfo("提示", "暂无面试记录")
            return
        filename = filedialog.asksaveasfilename(title="保存面试报告", defaultextension=".pdf", filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")])
        if filename:
            self.review_manager.generate_overall_assessment(self.stage_manager, self.score_manager)
            candidate_name = self.resume_data.get('name', '候选人') if self.resume_data else '候选人'
            track_name = self.selected_track or '未知赛道'
            success = self.review_manager.export_to_pdf(filename, candidate_name, track_name)
            if success:
                tk.messagebox.showinfo("成功", f"面试报告已导出至:\n{filename}")
            else:
                tk.messagebox.showerror("失败", "PDF导出失败，请检查权限和路径")

    # 录音与处理
    def start_recording(self, event):
        if not self.interview_active:
            self.display_text("请先开始面试！")
            return
        if not self.is_processing and not self.progress_active:
            self.solution.recorder.start_recording()
            self.recording_start_time = time.time()
            self.progress_active = True
            self.update_progress()
            self.status_label.config(text="录音中...", fg="#e74c3c")

    def update_progress(self):
        if not self.progress_active:
            return
        elapsed = time.time() - self.recording_start_time
        progress = min(100, math.log(1 + elapsed * 10) * 30)
        self.progress_var.set(progress)
        self.time_label.config(text=f"{elapsed:.1f}s")
        if self.progress_active:
            self.root.after(50, self.update_progress)

    def stop_recording(self, event):
        if not self.progress_active or self.is_processing or not self.interview_active:
            return
        self.progress_active = False
        self.is_processing = True
        self.status_label.config(text="处理中...", fg="#f39c12")
        user_input = self.solution.recorder.stop_recording()
        if user_input:
            self.message_queue.put(f"候选人: {user_input}")
            self.last_answer = user_input
            self.conversation_history.append({"role": "user", "content": user_input})
            self.analyze_response(user_input)
            self.input_queue.put("candidate_response")
        self.root.after(100, self.reset_progress)

    def analyze_response(self, response):
        if self.dynamic_prompt_adjuster and hasattr(self, 'last_model_output'):
            self.dynamic_prompt_adjuster.update_conversation_context(response, self.last_model_output)
        self.conversation_context.append(f"候选人: {response}")
        if len(self.conversation_context) > 6:
            self.conversation_context = self.conversation_context[-6:]

        if (hasattr(self, 'last_question') and self.last_question and hasattr(self, 'question_count') and self.question_count > 0 and self.interview_active):
            def score_response():
                try:
                    score = self.score_manager.evaluate_response(response, self.last_question)
                    new_difficulty = self.score_manager.adjust_difficulty(score)
                    self.root.after(0, lambda: self._update_after_scoring_silent(score, new_difficulty))
                except Exception as e:
                    print(f"评分过程出错: {e}")
            threading.Thread(target=score_response, daemon=True).start()

    def _update_after_scoring_silent(self, score, new_difficulty):
        if hasattr(self, 'last_question') and hasattr(self, 'last_answer'):
            feedback = self.review_manager.generate_detailed_feedback(self.last_answer, self.last_question, score)
        else:
            feedback = f"得分: {score:.2f}/1.0"
        current_stage = self.stage_manager.get_current_stage()
        self.review_manager.add_qa_record(self.last_question, self.last_answer, score, feedback, current_stage)
        self.stage_manager.add_score_to_stage(score)
        if self.stage_manager.should_advance_stage():
            if self.stage_manager.advance_to_next_stage():
                new_stage = self.stage_manager.get_current_stage()
                self.stage_info_label.config(text=f"当前阶段: {new_stage} (第{self.stage_manager.current_stage_question_count + 1}题)")
            else:
                self.stage_info_label.config(text="当前阶段: 面试完成")
        else:
            current_stage = self.stage_manager.get_current_stage()
            self.stage_info_label.config(text=f"当前阶段: {current_stage} (第{self.stage_manager.current_stage_question_count + 1}题)")
        self.stage_manager.adjust_stage_questions(self.score_manager.score_history)
        self.update_status_display_silent()

    def _update_after_scoring(self, score, new_difficulty):
        if hasattr(self, 'last_question') and hasattr(self, 'last_answer'):
            feedback = self.review_manager.generate_detailed_feedback(self.last_answer, self.last_question, score)
        else:
            feedback = f"得分: {score:.2f}/1.0"
        current_stage = self.stage_manager.get_current_stage()
        self.review_manager.add_qa_record(self.last_question, self.last_answer, score, feedback, current_stage)
        score_text = f"本题评分: {score:.2f}"
        if score > 0.8:
            score_text += " (优秀)"
        elif score > 0.6:
            score_text += " (良好)"
        elif score > 0.4:
            score_text += " (及格)"
        else:
            score_text += " (需改进)"
        self.display_text(score_text)
        self.display_text(f"反馈: {feedback}")
        self.stage_manager.add_score_to_stage(score)
        if self.stage_manager.should_advance_stage():
            if self.stage_manager.advance_to_next_stage():
                new_stage = self.stage_manager.get_current_stage()
                self.display_text(f"📍 进入下一阶段: {new_stage}")
                self.stage_info_label.config(text=f"当前阶段: {new_stage} (第{self.stage_manager.current_stage_question_count + 1}题)")
            else:
                self.display_text("📍 所有阶段已完成，可以结束面试")
                self.stage_info_label.config(text="当前阶段: 面试完成")
        else:
            current_stage = self.stage_manager.get_current_stage()
            self.stage_info_label.config(text=f"当前阶段: {current_stage} (第{self.stage_manager.current_stage_question_count + 1}题)")
        self.stage_manager.adjust_stage_questions(self.score_manager.score_history)
        if new_difficulty != self.score_manager.difficulty_history[-1]["previous_difficulty"]:
            self.display_text(f"难度调整: {self.score_manager.difficulty_history[-1]['previous_difficulty']} → {new_difficulty}")
        self.update_status_display()

    def update_status_display_silent(self):
        if hasattr(self, 'question_count'):
            self.question_count_label.config(text=f"问题数: {self.question_count}")
        self.latest_score_label.config(text="面试进行中...")
        self.avg_score_label.config(text="实时分析中...")

    def update_status_display(self):
        self.difficulty_label.config(text=f"当前难度: {self.score_manager.current_difficulty}")
        if self.score_manager.score_history:
            latest_score = self.score_manager.score_history[-1]
            self.latest_score_label.config(text=f"最新评分: {latest_score:.2f}")
            avg_score = sum(self.score_manager.score_history) / len(self.score_manager.score_history)
            self.avg_score_label.config(text=f"平均分: {avg_score:.2f}")
        else:
            self.latest_score_label.config(text="最新评分: --")
            self.avg_score_label.config(text="平均分: --")
        self.question_count_label.config(text=f"问题数: {len(self.score_manager.score_history)}")

    def reset_progress(self):
        self.progress_var.set(0)
        self.time_label.config(text="0.0s")

    def extract_question(self, model_output):
        while "<think>" in model_output and "</think>" in model_output:
            think_start = model_output.find("<think>")
            think_end = model_output.find("</think>") + len("</think>")
            model_output = model_output[:think_start] + model_output[think_end:]
        arrow_index = model_output.find(">")
        if arrow_index != -1:
            question_text = model_output[arrow_index + 1:].strip()
            end_marks = ['.', '?', '！', '。', '？']
            end_indices = [question_text.find(mark) for mark in end_marks if mark in question_text]
            if end_indices:
                valid_indices = [i for i in end_indices if i != -1]
                if valid_indices:
                    first_end = min(valid_indices) + 1
                    question_text = question_text[:first_end].strip()
            return question_text
        return model_output.strip()

    def build_dynamic_prompt(self):
        stage_prompt = self.stage_manager.get_stage_prompt(self.jd_data, self.resume_data)
        difficulty_prompt = self.score_manager.get_difficulty_prompt()
        # 结合能力金字塔建议层级
        focus_level = None
        if self.ability_pyramid:
            focus_level = self.ability_pyramid.suggest_focus_level(self.score_manager.score_history)
        reference_questions = []
        if self.selected_track:
            ref_questions = self.question_bank_manager.get_reference_questions(difficulty=self.score_manager.current_difficulty, num_questions=3)
            reference_questions = [q["question"] for q in ref_questions]
        instruction = (
            f"你是一个专业的{self.selected_track}面试官，具备三阶段面试和动态难度调整能力。"
            f"当前正在进行第{self.stage_manager.current_stage + 1}阶段面试。\n\n"
            f"{stage_prompt}\n\n"
            f"{difficulty_prompt}\n\n"
        )
        if focus_level:
            instruction += f"基于能力金字塔，当前建议关注层级: {focus_level}。\n\n"
        if self.jd_data and self.jd_data.get('keywords'):
            instruction += f"### JD关键技术要求:\n{', '.join(self.jd_data['keywords'])}\n\n"
        if reference_questions:
            instruction += "### 参考题库示例:\n"
            for i, q in enumerate(reference_questions, 1):
                instruction += f"{i}. {q}\n"
            instruction += "\n请参考以上题库内容和当前阶段要求，生成相应的问题。\n\n"
        instruction += (
            "你必须严格遵守以下规则：\n"
            "1. 直接输出问题，不要输出思考过程\n"
            "2. 在问题前添加'>'符号作为前缀\n"
            "3. 只输出问题内容，不要添加任何前缀（如'面试官：'）\n"
            "4. 每次只提一个问题\n"
            "5. 问题应该简洁明了，不超过2句话\n"
            "6. 问题难度必须与当前设定的难度级别匹配\n"
            f"7. 问题必须符合当前{self.stage_manager.get_current_stage()}阶段要求\n"
            f"8. 问题必须符合{self.selected_track}赛道的专业要求\n"
            "9. 面试结束时只评价候选人表现，不要评价问题质量\n"
        )
        history_details = "### 对话历史摘要:\n"
        if self.conversation_context:
            history_details += "\n".join(self.conversation_context[-3:])
        else:
            history_details += "暂无历史对话"
        evidence_details = "### 证据细节:\n"
        if self.dynamic_prompt_adjuster:
            triplets = self.dynamic_prompt_adjuster.triplet_filter()
            if triplets:
                evidence_details += "知识三元组:\n"
                for head, rel, tail in triplets:
                    evidence_details += f"- {head} -- {rel} --> {tail}\n"
            if self.dynamic_prompt_adjuster.historical_entities:
                evidence_details += "\n历史实体:\n"
                evidence_details += ", ".join(set(self.dynamic_prompt_adjuster.historical_entities[-5:]))
            if self.dynamic_prompt_adjuster.current_entities:
                evidence_details += "\n当前相关实体:\n"
                evidence_details += ", ".join(self.dynamic_prompt_adjuster.current_entities)
        # 合并岗位知识图谱摘要（占位）
        if self.job_graph_builder:
            evidence_details += "\n\n"
            evidence_details += self.job_graph_builder.summarize(limit=6)
        demonstration = "### 相关演示:\n"
        if self.dynamic_prompt_adjuster:
            demo = self.dynamic_prompt_adjuster.demo_selector()
            demonstration += demo
        prompt = f"""
        {instruction}

        {history_details}

        {evidence_details}

        {demonstration}
        """
        return prompt

    def process_model_responses(self):
        while True:
            action = self.input_queue.get()
            if not self.interview_active and action != "start_interview":
                continue
            try:
                dynamic_prompt = self.build_dynamic_prompt()
                if not self.initial_prompt_set:
                    self.conversation_history = [{"role": "system", "content": dynamic_prompt}]
                    self.initial_prompt_set = True
                else:
                    self.conversation_history[0] = {"role": "system", "content": dynamic_prompt}
                if action == "start_interview":
                    self.conversation_history.append({"role": "user", "content": "请基于候选人的简历提出第一个面试问题"})
                    self.question_count = 0
                    self.first_question_asked = False
                elif action == "end_interview":
                    score_info = self.score_manager.get_score_summary()
                    difficulty_info = self.score_manager.get_difficulty_progression()
                    evaluation_content = """面试结束，请根据整个面试过程给出候选人综合评估。
请从以下几个方面进行评价：

1. 技术掌握程度
2. 项目经验深度
3. 解决问题能力
4. 沟通表达能力
5. 学习成长潜力

注意：
- 只评价候选人的表现，不要评价问题的质量
- 不要显示具体分数，用定性描述替代
- 重点关注候选人的优势和可提升空间
- 给出明确的是否通过面试的结论"""
                    self.conversation_history.append({"role": "user", "content": evaluation_content})
                elif action == "candidate_response":
                    pass
                output = ollama.chat(model="Jerrypoi/deepseek-r1-with-tool-calls:latest", messages=self.conversation_history)
                model_output = output['message']['content']
                self.last_model_output = model_output
                self.conversation_history.append({"role": "assistant", "content": model_output})
                if action == "end_interview":
                    self.full_evaluation = model_output
                    self.message_queue.put("面试已结束,请点击查看复盘按钮查看详细评估，或导出PDF报告查看完整分析。")
                    self.solution.use_pyttsx3("面试评估已完成")
                    continue
                question_text = self.extract_question(model_output)
                self.last_question = question_text
                self.message_queue.put(f"> {question_text}")
                self.solution.use_pyttsx3(question_text)
                self.status_label.config(text="回答中...", fg="#9b59b6")
                self.question_count += 1
                if not self.first_question_asked and self.question_count >= 1:
                    self.first_question_asked = True
                    self.display_text("面试进入深入追问阶段...")
            except Exception as e:
                error_msg = f"错误: {str(e)}"
                self.message_queue.put(error_msg)
                self.solution.use_pyttsx3("抱歉，处理您的请求时出错了")
            finally:
                self.is_processing = False
                if self.interview_active:
                    self.status_label.config(text="准备提问...", fg="#2ecc71")
                else:
                    self.status_label.config(text="准备就绪", fg="#2ecc71")

    def start_queue_listener(self):
        def check_queue():
            try:
                while True:
                    message = self.message_queue.get_nowait()
                    self.display_text(message)
            except queue.Empty:
                pass
            self.root.after(100, check_queue)
        check_queue()

    def check_interview_ready(self):
        remaining = []
        if not self.resume_data:
            remaining.append("上传简历")
        if not self.selected_track:
            remaining.append("选择赛道")
        if not self.jd_data:
            remaining.append("上传JD")
        if not remaining:
            self.start_interview_btn.config(state=tk.NORMAL)
            self.display_text("✅ 已完成所有准备工作，可以开始面试！")
        else:
            self.start_interview_btn.config(state=tk.DISABLED)
            if len(remaining) > 1:
                self.display_text(f"⏳ 请完成以下步骤：{', '.join(remaining)}")
            else:
                self.display_text(f"⏳ 请{remaining[0]}后开始面试")

    def display_text(self, text):
        self.text_area.config(state='normal')
        if text.startswith("候选人:"):
            self.text_area.tag_configure("candidate", foreground="#2980b9", font=(self.default_family, 14, "bold"))
            self.text_area.insert(tk.END, text + "\n\n", "candidate")
        elif text.startswith(">"):
            self.text_area.tag_configure("interviewer", foreground="#27ae60", font=(self.default_family, 14))
            self.text_area.insert(tk.END, text + "\n\n", "interviewer")
        elif text.startswith("错误:") or text.startswith("面试评估:"):
            self.text_area.tag_configure("error", foreground="#e74c3c", font=(self.default_family, 14))
            self.text_area.insert(tk.END, text + "\n", "error")
        else:
            self.text_area.insert(tk.END, text + "\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)



