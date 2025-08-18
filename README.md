# 🤖 AI面试智能官 - 你的模拟面试助手

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()

一个基于AI的智能面试系统，采用**三阶段递进式面试流程**，支持**B1 < B2 < B3动态难度调整**，具备**模块化架构设计**，提供全方位的个性化面试体验。

## 🎯 核心特性

### 🏗️ 模块化架构设计
采用全新的三阶段模块化架构，每个阶段都是独立完整的模块：

```
ai_interview/stages/
├── stage1_non_technical/     # 第一阶段：非技术问题模块
├── stage2_experience/        # 第二阶段：经历类问题模块  
├── stage3_technical/         # 第三阶段：技术类问题模块
└── integrated_interview.py   # 集成面试管理器
```

### 🎭 三阶段面试流程

#### 📍 **第一阶段：非技术问题**
- **考察目标**：基本情况、沟通能力、职业规划、工作态度
- **问题类型**：自我介绍、职业规划、公司岗位了解、工作态度
- **智能特性**：AI个性化生成 + 多维度评估
- **评估维度**：表达清晰度、信息完整性、与岗位相关性、逻辑结构
- **默认题数**：2题

#### 📍 **第二阶段：经历类问题**  
- **考察目标**：项目经历深挖、技术实现能力、实际工作经验
- **特色功能**：
  - **固定首问**：第一个问题限定为经历介绍请求
  - **专业深挖**：基于case.docx的深挖提问方式
  - **技术关键词提取**：自动识别并针对性追问
- **深挖五大原则**：技术深度、数据细节、架构决策、实际效果、团队协作
- **默认题数**：3题

#### 📍 **第三阶段：技术类问题**
- **考察目标**：专业技术能力、系统设计、深度理解
- **核心特性**：**B1 < B2 < B3动态难度调整系统**
  - **B1级别**：基础概念、入门技能（适合初级开发者）
  - **B2级别**：实际应用、项目经验（适合有经验开发者）
  - **B3级别**：深度技术、架构设计（适合高级开发者）
- **调整机制**：
  - 得分 ≥ 0.75 → 难度提升 (B1→B2→B3)
  - 0.5 ≤ 得分 < 0.75 → 保持当前难度
  - 得分 < 0.5 → 难度降低 (B3→B2→B1)
- **默认题数**：3题

### 📄 JD智能解析
- **自动解析**：提取职位名称、技术要求、岗位职责
- **技术匹配**：识别核心技术栈和关键词
- **个性化提问**：基于JD要求生成针对性问题
- **支持技术**：Java、Python、React、Vue、Docker、微服务、分布式等主流技术

### 🧠 智能评分系统
- **AI自动评分**：0-1分制，多维度智能评估
- **分阶段评估**：
  - **第一阶段**：沟通能力、完整性、相关性、逻辑性
  - **第二阶段**：技术深度、项目复杂度、个人贡献、问题解决
  - **第三阶段**：技术准确性、深度理解、实践经验、表达清晰度
- **智能反馈**：每题提供详细评分和改进建议

### 📊 专业评估报告
- **综合评级**：优秀/良好/一般/待提升/不合格
- **各阶段表现分析**：每个阶段的详细得分和反馈
- **技术能力评估**：基于第三阶段的专业技术水平定级
- **优势与改进建议**：具体的技能优势和需要提升的领域
- **录用建议**：基于综合表现的招聘建议

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 8GB+ 内存推荐
- Ollama服务（用于AI问题生成和评估）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-repo/AI_Interviewerrr.git
cd AI_Interviewerrr
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置Ollama**
```bash
# 安装并启动Ollama
ollama pull deepseek-r1:latest  # 或其他支持的模型
ollama serve
```

4. **启动应用**
```bash
python main.py
```

## 💻 使用方式

### 1. 集成面试系统（推荐）

```python
from ai_interview.stages import IntegratedInterviewManager

# 初始化集成管理器
manager = IntegratedInterviewManager()

# 准备候选人数据
resume_data = {
    'name': '候选人姓名',
    'education': '教育背景',
    'experience': ['工作经历1', '工作经历2'],
    'skills': ['技能1', '技能2'],
    'projects': ['项目1', '项目2']
}

jd_data = {
    'position': '职位名称',
    'company': '公司名称',
    'keywords': ['技术关键词1', '技术关键词2'],
    'requirements': ['要求1', '要求2']
}

# 开始完整面试
first_question = manager.start_interview(resume_data, jd_data)

# 处理回答并获取下一个问题
next_result = manager.process_answer_and_get_next_question(
    user_response, current_question
)

# 获取最终评估报告
if next_result.get('interview_completed'):
    final_assessment = next_result['final_assessment']
```

### 2. 独立阶段使用

```python
# 第一阶段：非技术问题
from ai_interview.stages.stage1_non_technical import NonTechnicalQuestionEngine
stage1 = NonTechnicalQuestionEngine()
question = stage1.start_stage(resume_data, jd_data)

# 第二阶段：经历类问题
from ai_interview.stages.stage2_experience import ExperienceQuestionEngine
stage2 = ExperienceQuestionEngine()
question = stage2.start_stage(resume_data, jd_data)

# 第三阶段：技术类问题
from ai_interview.stages.stage3_technical import TechnicalQuestionEngine
stage3 = TechnicalQuestionEngine()
question = stage3.start_stage(jd_data, resume_data)
```

### 3. Web界面使用

```bash
streamlit run ai_interview/app.py
```

## 🏗️ 项目架构

### 核心模块结构

```
AI_Interviewerrr/
├── ai_interview/
│   ├── stages/                          # 🎯 三阶段模块包
│   │   ├── __init__.py                  # 模块导出
│   │   ├── integrated_interview.py      # 集成面试管理器
│   │   │
│   │   ├── stage1_non_technical/        # 第一阶段模块
│   │   │   ├── __init__.py              
│   │   │   ├── non_technical_engine.py  # 主引擎
│   │   │   ├── question_generator.py    # 问题生成器
│   │   │   ├── evaluator.py            # 回答评估器
│   │   │   └── README.md               # 详细功能说明
│   │   │
│   │   ├── stage2_experience/           # 第二阶段模块
│   │   │   ├── __init__.py              
│   │   │   ├── experience_engine.py     # 主引擎
│   │   │   ├── deep_dive_generator.py   # 深挖问题生成器
│   │   │   ├── experience_evaluator.py  # 经历评估器
│   │   │   ├── case_prompts.py         # case.docx深挖模板
│   │   │   └── README.md               # 详细功能说明
│   │   │
│   │   └── stage3_technical/            # 第三阶段模块
│   │       ├── __init__.py              
│   │       ├── technical_engine.py      # 主引擎
│   │       ├── adaptive_difficulty.py   # 动态难度管理器
│   │       ├── question_bank.py        # 技术问题库
│   │       ├── technical_evaluator.py   # 技术评估器
│   │       └── README.md               # 详细功能说明
│   │
│   ├── app.py                          # Streamlit Web界面
│   ├── jd.py                           # 职位描述处理
│   ├── resume.py                       # 简历解析处理
│   ├── ui.py                           # UI界面组件
│   └── voice.py                        # 语音识别和合成
│
├── Data/                               # 数据文件目录
│   ├── data.csv                        # 结构化问题库
│   ├── case.docx                       # 深挖提问示例
│   └── 岗位–能力匹配金字塔.docx          # 岗位能力匹配模型
├── demo_refactored_system.py           # 系统演示脚本
├── main.py                             # 程序入口
├── requirements.txt                    # 依赖管理
└── README.md                           # 项目说明
```

### 架构特点

- **🧩 模块化设计**：每个阶段都是独立完整的模块
- **🔗 松耦合架构**：模块间通过清晰的接口通信
- **📖 文档完备**：每个模块都有详细的README说明
- **🧪 易于测试**：支持单元测试和集成测试
- **🔧 便于扩展**：新功能可以轻松添加到对应模块

## 🎯 智能算法

### 1. AI问题生成算法
- **个性化生成**：基于简历和JD的AI问题生成
- **多样性保证**：避免重复问题的智能机制
- **难度匹配**：根据候选人水平调整问题难度

### 2. 动态难度调整算法（第三阶段）
```python
def adjust_difficulty(score):
    if score >= 0.75:
        # 回答优秀，提升难度
        current_difficulty = increase_level(current_difficulty)
    elif score < 0.5:
        # 回答较差，降低难度  
        current_difficulty = decrease_level(current_difficulty)
    # 0.5 <= score < 0.75 保持当前难度
    return current_difficulty
```

### 3. 多维度评估算法
- **加权评分**：不同维度按重要性加权
- **上下文感知**：结合问题类型和候选人背景
- **智能反馈**：基于评估结果生成改进建议

### 4. 深挖提问算法（第二阶段）
- **技术关键词提取**：自动识别经历中的技术要点
- **case.docx模式**：基于专业面试案例的提问风格
- **递进式深挖**：从概述到细节的层层深入

## 📊 数据和配置

### 问题库数据 (Data/data.csv)
- **总题数**：1020+道专业面试题
- **难度分级**：B1（基础）、B2（中等）、B3（高级）
- **分类维度**：岗位类型、能力项、建议等级
- **覆盖领域**：后端、前端、算法、测试、产品、运营

### 深挖案例 (Data/case.docx)
- **真实案例**：6个完整的项目经历深挖示例
- **提问风格**：专业技术面试官的深度追问方式
- **技术覆盖**：AI、大数据、系统架构、算法优化等
- **集成方式**：完整内容作为AI系统提示词

### 配置选项
```python
# 问题数量配置
stage1.max_questions = 2  # 第一阶段
stage2.max_questions = 3  # 第二阶段  
stage3.max_questions = 3  # 第三阶段

# 难度调整阈值配置
difficulty_thresholds = {
    "increase": 0.75,   # 提升难度阈值
    "decrease": 0.5,    # 降低难度阈值
}

# 评估权重配置
evaluation_weights = {
    'technical_accuracy': 0.4,
    'depth_understanding': 0.3,
    'practical_experience': 0.2,
    'clarity': 0.1
}
```

## 🧪 测试和演示

### 运行系统演示
```bash
# 完整系统演示
python demo_refactored_system.py

# 集成面试流程演示
python -c "
from ai_interview.stages import IntegratedInterviewManager
manager = IntegratedInterviewManager()
# 演示代码...
"

# 各阶段独立测试
python -c "
from ai_interview.stages.stage1_non_technical import NonTechnicalQuestionEngine
from ai_interview.stages.stage2_experience import ExperienceQuestionEngine
from ai_interview.stages.stage3_technical import TechnicalQuestionEngine
# 测试代码...
"
```

### 功能测试用例
```python
def test_integrated_interview():
    manager = IntegratedInterviewManager()
    
    # 测试数据
    resume_data = {'name': '测试候选人', 'skills': ['Python']}
    jd_data = {'position': '开发工程师', 'keywords': ['Python']}
    
    # 启动面试
    first_question = manager.start_interview(resume_data, jd_data)
    assert 'question' in first_question
    
    # 模拟回答
    response = "我是一名有3年经验的Python开发工程师..."
    result = manager.process_answer_and_get_next_question(response, first_question)
    
    assert 'evaluation' in result
    assert 0 <= result['evaluation']['score'] <= 1

def test_difficulty_adjustment():
    from ai_interview.stages.stage3_technical import TechnicalQuestionEngine
    engine = TechnicalQuestionEngine()
    
    # 测试难度提升
    evaluation = engine.difficulty_manager.adjust_difficulty(0.8)
    assert evaluation['adjustment_type'] in ['increase', 'maintain']
    
    # 测试难度降低
    evaluation = engine.difficulty_manager.adjust_difficulty(0.3)
    assert evaluation['adjustment_type'] in ['decrease', 'maintain']
```

## ⚙️ 高级配置

### 1. AI模型配置
```python
# 在各阶段的问题生成器中配置
model_config = {
    "model": "deepseek-r1:latest",
    "temperature": 0.7,
    "max_tokens": 1000
}
```

### 2. 评分标准调整
```python
# 自定义评分权重
custom_weights = {
    "stage1": {
        "communication": 0.3,
        "completeness": 0.3,
        "relevance": 0.2,
        "logic": 0.2
    },
    "stage2": {
        "technical_depth": 0.4,
        "project_complexity": 0.3,
        "personal_contribution": 0.2,
        "problem_solving": 0.1
    },
    "stage3": {
        "technical_accuracy": 0.4,
        "depth_understanding": 0.3,
        "practical_experience": 0.2,
        "clarity": 0.1
    }
}
```

### 3. 难度调整策略
```python
# 自定义难度调整策略
class CustomDifficultyStrategy:
    def adjust(self, score, history):
        # 考虑历史表现的自定义调整逻辑
        if len(history) >= 2:
            recent_trend = sum(h['score'] for h in history[-2:]) / 2
            if recent_trend > 0.8:
                return "increase"
        return "maintain"
```

## 📈 性能优化

### 系统性能
- **响应时间**：单次问题生成 < 3秒
- **并发支持**：支持多用户同时面试
- **内存占用**：基础运行 < 2GB
- **AI推理**：本地部署，数据安全

### 优化建议
1. **硬件配置**：推荐8GB+内存，支持GPU加速
2. **模型优化**：使用量化模型减少内存占用
3. **缓存策略**：常用问题和评估结果缓存
4. **并发控制**：限制同时处理的面试数量

## 📝 开发指南

### 添加新的面试阶段
1. 在`ai_interview/stages/`下创建新模块目录
2. 实现主引擎、问题生成器、评估器
3. 在`integrated_interview.py`中集成新阶段
4. 添加相应的测试用例和文档

### 扩展评估维度
1. 在对应阶段的evaluator中添加新维度
2. 更新evaluation_criteria权重配置
3. 修改AI评估提示词包含新维度
4. 更新文档说明新评估标准

### 自定义问题库
1. 按照data.csv格式准备新问题
2. 在question_bank.py中添加加载逻辑
3. 更新难度分级和分类标准
4. 测试新问题的生成和评估

## 🚀 版本更新记录

### v2.0.0 (2024-01) - 模块化重构版本
- ✅ **架构重构**：全新的三阶段模块化架构
- ✅ **代码清理**：删除69%的冗余代码，提升可维护性
- ✅ **功能完善**：B1/B2/B3动态难度调整系统
- ✅ **深挖提问**：基于case.docx的专业深挖方式
- ✅ **文档完备**：每个模块都有详细的README说明
- ✅ **性能优化**：模块化设计，便于测试和扩展

### v1.5.0 (2023-12) - 智能评估版本
- ✅ **AI评估升级**：多维度智能评分系统
- ✅ **难度调整**：动态问题难度调整机制
- ✅ **深度挖掘**：项目经历深度追问功能
- ✅ **专业报告**：综合面试评估报告

### v1.0.0 (2023-11) - 基础版本
- ✅ **三阶段面试**：基础的三阶段面试流程
- ✅ **JD解析**：职位描述智能解析
- ✅ **简历处理**：简历信息提取和分析
- ✅ **语音交互**：语音识别和合成功能

## 🤝 贡献指南

我们欢迎社区贡献！请参考以下流程：

1. **Fork项目** 并创建功能分支
2. **编写代码** 遵循项目代码规范
3. **添加测试** 确保新功能有测试覆盖
4. **更新文档** 包括README和模块文档
5. **提交PR** 详细描述变更内容

### 开发环境设置
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/AI_Interviewerrr.git
cd AI_Interviewerrr

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有开发依赖

# 4. 运行测试
python -m pytest tests/

# 5. 代码格式检查
black ai_interview/
flake8 ai_interview/
```

## 🛠️ 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查Ollama服务状态
   ollama list
   ollama serve
   ```

2. **模型加载失败**
   ```bash
   # 重新拉取模型
   ollama pull deepseek-r1:latest
   ```

3. **依赖安装问题**
   ```bash
   # 升级pip并重新安装
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **权限错误**
   ```bash
   # 检查文件权限
   chmod +x main.py
   ```

### 性能问题

1. **响应时间过长**
   - 检查Ollama服务是否正常
   - 考虑使用更小的模型
   - 增加系统内存

2. **内存占用过高**
   - 使用量化模型
   - 限制并发用户数
   - 定期清理缓存

## 📞 联系方式

- **项目主页**: https://github.com/your-repo/AI_Interviewerrr
- **问题反馈**: https://github.com/your-repo/AI_Interviewerrr/issues
- **功能建议**: https://github.com/your-repo/AI_Interviewerrr/discussions

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

感谢以下开源项目的支持：
- [Ollama](https://ollama.ai/) - 本地AI模型运行框架
- [Streamlit](https://streamlit.io/) - Web应用框架
- [DeepSeek](https://www.deepseek.com/) - AI语言模型
- [Vosk](https://alphacephei.com/vosk/) - 语音识别引擎

---

🎯 **让AI面试更智能，让求职更高效！**

*如果这个项目对您有帮助，请给我们一个 ⭐ Star！*