import time
import ollama
import pyttsx3
import json
import pyaudio
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
import tkinter as tk
from tkinter import scrolledtext, font, ttk, filedialog
import threading
import queue
import wave
import os
import math
import fitz  # PyMuPDF for PDF parsing
import docx  # For DOCX parsing
import re

# 语音识别模块
class VoiceRecorder:
    def __init__(self, model):
        self.model = model
        self.rec = KaldiRecognizer(model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.start_time = 0

    def start_recording(self):
        if not self.is_recording:
            self.frames = []
            self.stream = self.p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            self.is_recording = True
            self.start_time = time.time()
            print("Recording started...")
            threading.Thread(target=self._record).start()

    def _record(self):
        while self.is_recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            print("Recording stopped.")
            return self.process_recording()
        return None

    def process_recording(self):
        # 保存为临时WAV文件
        temp_file = "temp_recording.wav"
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.audio_format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # 使用Vosk进行识别
        result_text = self._recognize_speech(temp_file)
        # 删除临时文件
        os.remove(temp_file)
        return result_text

    def _recognize_speech(self, filename):
        wf = wave.open(filename, 'rb')
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            return None
        
        recognizer = KaldiRecognizer(self.model, wf.getframerate())
        recognizer.SetWords(True)
        
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                results.append(result.get("text", ""))
        
        final_result = json.loads(recognizer.FinalResult())
        results.append(final_result.get("text", ""))
        return ' '.join(results)

# 简历解析类
class ResumeParser:
    def __init__(self):
        self.resume_data = {
            "name": "",
            "contact": "",
            "education": [],
            "experience": [],
            "skills": [],
            "projects": [],
            "summary": ""
        }
    
    def parse_resume(self, file_path):
        """根据文件类型调用相应的解析方法"""
        if file_path.lower().endswith('.pdf'):
            return self.parse_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.parse_docx(file_path)
        else:
            return "不支持的文件格式，请上传PDF或DOCX文件"
    
    def parse_pdf(self, file_path):
        """解析PDF格式的简历"""
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            
            return self._extract_info(text)
        except Exception as e:
            return f"解析PDF失败: {str(e)}"
    
    def parse_docx(self, file_path):
        """解析DOCX格式的简历"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return self._extract_info(text)
        except Exception as e:
            return f"解析DOCX失败: {str(e)}"
    
    def _extract_info(self, text):
        """从文本中提取简历信息"""
        # 提取姓名
        name_match = re.search(r"^(.*?)\n", text)
        if name_match:
            self.resume_data["name"] = name_match.group(1).strip()
        
        # 提取联系方式
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4})", text)
        email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
        self.resume_data["contact"] = f"电话: {phone_match.group(0) if phone_match else '未找到'} | 邮箱: {email_match.group(0) if email_match else '未找到'}"
        
        # 提取教育背景
        edu_section = re.search(r"(教育背景|教育经历|学历|Education)(.*?)(?=(工作经历|项目经历|技能|$))", text, re.DOTALL | re.IGNORECASE)
        if edu_section:
            edu_text = edu_section.group(2)
            self.resume_data["education"] = [line.strip() for line in edu_text.split('\n') if line.strip()]
        
        # 提取工作经历
        exp_section = re.search(r"(工作经历|工作经验|工作|Experience)(.*?)(?=(项目经历|技能|教育背景|$))", text, re.DOTALL | re.IGNORECASE)
        if exp_section:
            exp_text = exp_section.group(2)
            self.resume_data["experience"] = [line.strip() for line in exp_text.split('\n') if line.strip()]
        
        # 提取技能
        skills_section = re.search(r"(技能|专业技能|技术能力|Skills)(.*?)(?=(项目经历|工作经历|教育背景|$))", text, re.DOTALL | re.IGNORECASE)
        if skills_section:
            skills_text = skills_section.group(2)
            self.resume_data["skills"] = [line.strip() for line in skills_text.split('\n') if line.strip()]
        
        # 提取项目经历
        projects_section = re.search(r"(项目经历|项目经验|项目|Projects)(.*?)(?=(技能|工作经历|教育背景|$))", text, re.DOTALL | re.IGNORECASE)
        if projects_section:
            projects_text = projects_section.group(2)
            self.resume_data["projects"] = [line.strip() for line in projects_text.split('\n') if line.strip()]
        
        # 生成摘要
        self.resume_data["summary"] = f"候选人: {self.resume_data['name']}，教育背景: {len(self.resume_data['education'])}项，工作经验: {len(self.resume_data['experience'])}项，技能: {len(self.resume_data['skills'])}项"
        
        return self.resume_data

# Tkinter 窗口模块
class InteractiveTextApp:
    def __init__(self, root, solution):
        self.root = root
        self.solution = solution
        self.root.title("AI面试智能官")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 设置字体
        self.custom_font = font.Font(family="Helvetica", size=16)
        self.small_font = font.Font(family="Helvetica", size=12)
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")

        # 创建标题
        title_label = tk.Label(
            main_frame,
            text="AI面试智能官",
            font=("Helvetica", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)

        # 创建顶部按钮框架
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)
        
        # 添加简历上传按钮
        self.upload_btn = tk.Button(
            button_frame,
            text="上传简历",
            command=self.upload_resume,
            font=self.small_font,
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加面试开始按钮
        self.start_interview_btn = tk.Button(
            button_frame,
            text="开始面试",
            command=self.start_interview,
            font=self.small_font,
            bg="#2ecc71",
            fg="white",
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        self.start_interview_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加面试结束按钮
        self.end_interview_btn = tk.Button(
            button_frame,
            text="结束面试",
            command=self.end_interview,
            font=self.small_font,
            bg="#e74c3c",
            fg="white",
            padx=10,
            pady=5,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.end_interview_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加候选人信息面板
        info_frame = tk.LabelFrame(
            main_frame,
            text="候选人信息",
            font=self.small_font,
            bg="#f0f0f0",
            bd=2,
            relief=tk.GROOVE
        )
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_label = tk.Label(
            info_frame,
            text="请上传简历以查看候选人信息",
            font=self.small_font,
            bg="#f0f0f0",
            fg="#7f8c8d",
            justify=tk.LEFT,
            wraplength=900
        )
        self.info_label.pack(fill=tk.X, padx=10, pady=5)

        # 创建可滚动的文本框
        text_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.GROOVE)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=70,
            height=18,
            state='disabled',
            font=self.custom_font,
            bg="#ffffff",
            fg="#333333",
            padx=15,
            pady=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # 添加初始提示
        self.display_text("欢迎使用AI面试智能官！\n请先上传简历，然后点击'开始面试'按钮开始面试。")

        # 创建录音控制区域
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, pady=10)
        
        # 添加录音状态标签
        self.status_label = tk.Label(
            control_frame,
            text="准备就绪",
            font=self.small_font,
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 添加进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 添加录音时间标签
        self.time_label = tk.Label(
            control_frame,
            text="0.0s",
            font=self.small_font,
            bg="#f0f0f0",
            fg="#7f8c8d",
            width=6
        )
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # 添加操作提示
        help_frame = tk.Frame(main_frame, bg="#f0f0f0")
        help_frame.pack(fill=tk.X, pady=5)
        
        self.help_label = tk.Label(
            help_frame,
            text="按住空格键开始录音，松开结束录音",
            font=("Helvetica", 12, "italic"),
            bg="#f0f0f0",
            fg="#3498db"
        )
        self.help_label.pack()

        # 绑定按键事件
        self.root.bind("<KeyPress-space>", self.start_recording)
        self.root.bind("<KeyRelease-space>", self.stop_recording)
        self.root.focus_set()

        # 创建队列，用于线程间通信
        self.message_queue = queue.Queue()
        self.input_queue = queue.Queue()

        # 启动队列监听器
        self.start_queue_listener()
        
        # 启动模型响应线程
        self.model_thread = threading.Thread(target=self.process_model_responses, daemon=True)
        self.model_thread.start()
        
        # 状态变量
        self.recording_start_time = 0
        self.progress_active = False
        self.is_processing = False
        self.interview_active = False
        self.resume_data = None
        self.parser = ResumeParser()

    def upload_resume(self):
        """上传并解析简历"""
        file_path = filedialog.askopenfilename(
            title="选择简历文件",
            filetypes=[("PDF文件", "*.pdf"), ("Word文件", "*.docx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.display_text(f"正在解析简历: {os.path.basename(file_path)}...")
            self.resume_data = self.parser.parse_resume(file_path)
            
            if isinstance(self.resume_data, dict):
                # 更新候选人信息面板
                info_text = f"姓名: {self.resume_data['name']}\n"
                info_text += f"联系方式: {self.resume_data['contact']}\n"
                info_text += f"教育背景: {len(self.resume_data['education'])}项\n"
                info_text += f"工作经验: {len(self.resume_data['experience'])}项\n"
                info_text += f"技能: {len(self.resume_data['skills'])}项"
                
                self.info_label.config(text=info_text)
                self.display_text("简历解析完成！请点击'开始面试'按钮开始面试。")
                self.start_interview_btn.config(state=tk.NORMAL)
            else:
                self.display_text(f"简历解析失败: {self.resume_data}")

    def start_interview(self):
        """开始面试"""
        if not self.resume_data:
            self.display_text("请先上传简历！")
            return
        
        self.interview_active = True
        self.display_text("面试已开始！请准备回答面试官的问题。")
        self.end_interview_btn.config(state=tk.NORMAL)
        self.start_interview_btn.config(state=tk.DISABLED)
        
        # 发送初始面试问题
        self.input_queue.put("现在开始面试。请基于以下简历内容提出问题：" + json.dumps(self.resume_data, ensure_ascii=False))

    def end_interview(self):
        """结束面试"""
        self.interview_active = False
        self.display_text("面试已结束！感谢参与。")
        self.end_interview_btn.config(state=tk.DISABLED)
        self.start_interview_btn.config(state=tk.NORMAL)
        
        # 发送评估请求
        self.input_queue.put("面试结束，请根据整个面试过程给出候选人评估")

    def start_recording(self, event):
        """开始录音"""
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
        """停止录音并处理录音内容"""
        if not self.progress_active or self.is_processing or not self.interview_active:
            return
            
        self.progress_active = False
        self.is_processing = True
        self.status_label.config(text="处理中...", fg="#f39c12")
        user_input = self.solution.recorder.stop_recording()
        
        if user_input:
            self.message_queue.put(f"候选人: {user_input}")
            self.input_queue.put(user_input)
        
        self.root.after(100, self.reset_progress)

    def reset_progress(self):
        self.progress_var.set(0)
        self.time_label.config(text="0.0s")

    def process_model_responses(self):
        """处理模型响应的线程"""
        while True:
            user_input = self.input_queue.get()
            
            if not self.interview_active and not user_input.startswith("现在开始面试"):
                continue
            
            try:
                # 准备系统提示词
                system_prompt = (
                    "你是一个专业的AI面试官。基于候选人的简历信息，提出相关的问题来评估候选人的技能和经验。"
                    "面试问题应聚焦于候选人的工作经验、项目经历、技能掌握程度等专业领域。"
                    "面试结束后，请提供对候选人的全面评估。"
                    "以下是候选人的简历信息：\n" + 
                    (json.dumps(self.resume_data, ensure_ascii=False) if self.resume_data else "无简历信息")
                )
                
                # 调用模型生成回复
                output = ollama.chat(
                    model="Jerrypoi/deepseek-r1-with-tool-calls:latest",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                model_output = output['message']['content']
                self.message_queue.put(f"面试官: {model_output}")
                
                # 语音播报模型输出
                self.solution.use_pyttsx3(model_output)
                
                # 更新状态
                self.status_label.config(text="回答中...", fg="#9b59b6")
                
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
        """监听队列，将消息显示在文本框中"""
        def check_queue():
            try:
                while True:
                    message = self.message_queue.get_nowait()
                    self.display_text(message)
            except queue.Empty:
                pass
            self.root.after(100, check_queue)

        check_queue()

    def display_text(self, text):
        """将文本显示在文本框中"""
        self.text_area.config(state='normal')
        
        if text.startswith("候选人:"):
            self.text_area.tag_configure("candidate", foreground="#2980b9", font=("Helvetica", 14, "bold"))
            self.text_area.insert(tk.END, text + "\n\n", "candidate")
        elif text.startswith("面试官:"):
            self.text_area.tag_configure("interviewer", foreground="#27ae60", font=("Helvetica", 14))
            self.text_area.insert(tk.END, text + "\n\n", "interviewer")
        elif text.startswith("错误:"):
            self.text_area.tag_configure("error", foreground="#e74c3c", font=("Helvetica", 14))
            self.text_area.insert(tk.END, text + "\n", "error")
        else:
            self.text_area.insert(tk.END, text + "\n")
        
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

# 主逻辑模块
class Solution:
    def __init__(self):
        model = Model("vosk-model-cn-0.15")
        SetLogLevel(-1)
        self.recorder = VoiceRecorder(model)

    def use_pyttsx3(self, word):
        """语音播报"""
        threading.Thread(target=self._speak, args=(word,), daemon=True).start()
    
    def _speak(self, word):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.say(word)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"语音播报出错: {e}")

# 主程序
if __name__ == "__main__":
    # 创建解决方案实例
    solution = Solution()
    
    # 创建 Tkinter 窗口
    root = tk.Tk()
    app = InteractiveTextApp(root, solution)
    
    # 运行 Tkinter 主循环
    root.mainloop()
