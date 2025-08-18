# 🎯 第一阶段：非技术问题模块

## 📋 模块概述

第一阶段非技术问题模块负责AI面试系统的开场环节，主要考察候选人的基本情况、沟通能力、职业规划和对公司岗位的了解程度。这是建立初步印象和评估综合素质的重要阶段。

## 🎪 核心功能

### 1. 问题类型覆盖
- **自我介绍** (`self_introduction`)：评估表达能力和背景匹配度
- **职业规划** (`career_planning`)：了解发展目标和动机
- **公司岗位了解** (`company_position`)：评估求职诚意和准备程度
- **工作态度** (`work_attitude`)：考察价值观和团队合作能力

### 2. 智能问题生成
- **AI个性化生成**：基于简历和JD信息定制问题
- **模板备用方案**：确保系统稳定性
- **避重复机制**：防止相似问题重复出现

### 3. 多维度评估
- **AI智能评估**：深度分析回答质量
- **基础规则评估**：长度、结构、词汇丰富度
- **综合评分机制**：结合多种评估方法

## 🏗️ 架构设计

### 模块结构
```
stage1_non_technical/
├── __init__.py              # 模块初始化和导出
├── non_technical_engine.py  # 主引擎，控制整个流程
├── question_generator.py    # 问题生成器
├── evaluator.py            # 回答评估器
└── README.md               # 本文档
```

### 类关系图
```
NonTechnicalQuestionEngine (主引擎)
    ├── NonTechnicalQuestionGenerator (问题生成)
    └── NonTechnicalEvaluator (回答评估)
```

## 🛠️ 详细实现

### 1. NonTechnicalQuestionEngine (主引擎)

**职责**：控制第一阶段的整个面试流程

**核心方法**：
```python
# 开始第一阶段
start_stage(resume_data: Dict, jd_data: Dict) -> Dict

# 生成下一个问题
generate_next_question() -> Dict

# 处理用户回答
process_answer(user_response: str, question_data: Dict) -> Dict

# 检查是否继续
should_continue() -> bool

# 获取阶段总结
get_stage_summary() -> Dict
```

**状态管理**：
- `current_question_index`: 当前问题索引
- `max_questions`: 最大问题数（默认2题）
- `asked_questions`: 已提问问题列表
- `question_responses`: 问答记录
- `question_scores`: 评分记录

### 2. NonTechnicalQuestionGenerator (问题生成器)

**职责**：根据简历和JD信息生成个性化非技术问题

**生成策略**：
1. **AI优先策略**：使用大语言模型生成个性化问题
2. **模板备用策略**：AI失败时使用预定义模板
3. **个性化调整**：根据候选人背景调整问题细节

**AI生成流程**：
```python
def _generate_ai_question(question_type, resume_data, jd_data):
    # 1. 构建个性化提示词
    prompt = _build_ai_prompt(question_type, resume_data, jd_data)
    
    # 2. 调用大语言模型
    response = ollama.chat(model="deepseek-r1", messages=[prompt])
    
    # 3. 返回生成的问题
    return response['message']['content']
```

**问题模板**：
```python
question_templates = {
    "self_introduction": [
        "请简单介绍一下您自己，包括您的教育背景、工作经历和主要技能。",
        "能否用几分钟时间介绍一下您的个人背景和职业经历？",
        # ... 更多模板
    ],
    # ... 其他类型
}
```

### 3. NonTechnicalEvaluator (回答评估器)

**职责**：多维度评估非技术问题的回答质量

**评估维度**：

#### 自我介绍 (`self_introduction`)
- **表达清晰度** (30%)：语言流畅性、表达清晰度
- **信息完整性** (30%)：是否包含关键背景信息
- **与岗位相关性** (20%)：内容与目标职位的匹配度
- **逻辑结构** (20%)：介绍的条理性和层次性

#### 职业规划 (`career_planning`)
- **目标清晰度** (30%)：职业目标是否明确具体
- **规划可行性** (30%)：规划是否现实可执行
- **与岗位匹配度** (20%)：规划与职位的契合度
- **动机合理性** (20%)：选择理由是否充分

#### 公司岗位了解 (`company_position`)
- **了解程度** (40%)：对公司和岗位的认知深度
- **准备充分性** (30%)：面试前的准备情况
- **求职诚意** (30%)：对职位的兴趣和诚意

#### 工作态度 (`work_attitude`)
- **价值观** (40%)：工作价值观的积极性
- **团队合作** (30%)：团队协作意识和能力
- **问题解决** (30%)：面对挑战的态度和方法

**评估流程**：
```python
def evaluate_response(user_response, question_data, context):
    # 1. AI智能评估
    ai_evaluation = _ai_evaluate(user_response, question_data, context)
    
    # 2. 基础规则评估
    basic_evaluation = _basic_evaluate(user_response, question_type)
    
    # 3. 综合评分计算
    final_score = _calculate_final_score(ai_evaluation, basic_evaluation)
    
    # 4. 生成反馈和建议
    return {
        'score': final_score,
        'feedback': feedback,
        'suggestions': suggestions
    }
```

## 📊 数据流程

### 输入数据格式

**简历数据** (`resume_data`)：
```python
{
    'name': '候选人姓名',
    'education': '教育背景',
    'experience': ['工作经历1', '工作经历2'],
    'skills': ['技能1', '技能2', '技能3'],
    'projects': ['项目1', '项目2']
}
```

**职位数据** (`jd_data`)：
```python
{
    'position': '职位名称',
    'company': '公司名称',
    'requirements': ['要求1', '要求2'],
    'keywords': ['关键词1', '关键词2']
}
```

### 输出数据格式

**问题数据**：
```python
{
    'question': '具体问题内容',
    'question_type': 'self_introduction|career_planning|company_position|work_attitude',
    'source': 'ai_generated|template',
    'category': '问题分类',
    'question_number': 1,
    'total_questions': 2,
    'stage': '第一阶段：非技术问题'
}
```

**评估结果**：
```python
{
    'score': 0.75,
    'ai_evaluation': {
        'scores': {'维度1': 0.8, '维度2': 0.7},
        'overall_comment': '总体评价',
        'improvement_suggestions': '改进建议'
    },
    'basic_metrics': {
        'length_score': 0.8,
        'vocabulary_score': 0.7,
        'structure_score': 0.6
    },
    'feedback': '具体反馈内容',
    'suggestions': ['建议1', '建议2']
}
```

**阶段总结**：
```python
{
    'stage_name': '第一阶段：非技术问题',
    'questions_asked': 2,
    'total_questions': 2,
    'average_score': 0.75,
    'question_responses': [问答记录],
    'detailed_scores': [0.8, 0.7],
    'stage_completed': True,
    'next_stage': '第二阶段：经历类问题'
}
```

## 🚀 使用示例

### 基本使用流程

```python
from ai_interview.stages.stage1_non_technical import NonTechnicalQuestionEngine

# 1. 初始化引擎
engine = NonTechnicalQuestionEngine()

# 2. 准备数据
resume_data = {
    'name': '张三',
    'experience': ['阿里巴巴-软件工程师'],
    'skills': ['Python', 'Java'],
    'education': '计算机科学本科'
}

jd_data = {
    'position': '高级后端开发工程师',
    'company': '字节跳动',
    'requirements': ['3年以上经验', 'Python熟练']
}

# 3. 开始第一阶段
first_question = engine.start_stage(resume_data, jd_data)
print(f"问题: {first_question['question']}")

# 4. 处理用户回答
user_response = "我是张三，毕业于XX大学计算机科学专业..."
evaluation = engine.process_answer(user_response, first_question)
print(f"评分: {evaluation['score']}")

# 5. 继续下一题
if engine.should_continue():
    next_question = engine.generate_next_question()
    print(f"下一题: {next_question['question']}")

# 6. 获取阶段总结
summary = engine.get_stage_summary()
print(f"阶段完成，平均分: {summary['average_score']}")
```

### 高级使用示例

```python
# 自定义配置
engine = NonTechnicalQuestionEngine()
engine.max_questions = 3  # 增加到3题

# 获取实时进度
progress = engine.get_progress_info()
print(f"进度: {progress['current_question']}/{progress['total_questions']}")

# 重置引擎状态
engine.reset()
```

## ⚙️ 配置选项

### 问题数量调整
```python
# 在引擎初始化后修改
engine.max_questions = 3  # 默认为2
```

### 评估权重调整
```python
# 在evaluator.py中修改evaluation_criteria
evaluation_criteria = {
    "self_introduction": {
        "communication": 0.4,    # 调整权重
        "completeness": 0.3,
        "relevance": 0.2,
        "logic": 0.1
    }
}
```

### AI模型配置
```python
# 在question_generator.py和evaluator.py中修改
model = "your-custom-model"
```

## 🧪 测试用例

### 单元测试示例

```python
def test_question_generation():
    generator = NonTechnicalQuestionGenerator()
    
    resume_data = {'name': '测试', 'skills': ['Python']}
    jd_data = {'position': '开发工程师'}
    
    question = generator.generate_question(
        'self_introduction', resume_data, jd_data
    )
    
    assert question['question'] is not None
    assert question['question_type'] == 'self_introduction'
    assert question['source'] in ['ai_generated', 'template']

def test_evaluation():
    evaluator = NonTechnicalEvaluator()
    
    response = "我是一名有3年经验的Python开发工程师..."
    question_data = {'question_type': 'self_introduction'}
    context = {'resume_data': {}, 'jd_data': {}}
    
    result = evaluator.evaluate_response(response, question_data, context)
    
    assert 0 <= result['score'] <= 1
    assert result['feedback'] is not None
```

## ⚠️ 注意事项

1. **依赖环境**：需要ollama服务正常运行
2. **网络连接**：AI生成和评估需要稳定网络
3. **容错机制**：AI失败时自动切换到模板方案
4. **数据安全**：不保存敏感个人信息

## 🔧 故障排除

### 常见问题

1. **AI生成失败**
   ```python
   # 检查ollama服务状态
   # 自动降级到模板方案
   ```

2. **评估结果异常**
   ```python
   # 使用备用评估方法
   # 检查输入数据格式
   ```

3. **进度状态错误**
   ```python
   # 调用reset()方法重置状态
   engine.reset()
   ```

## 🎯 总结

第一阶段非技术问题模块是整个AI面试系统的重要开端，通过：

- ✅ **四大问题类型**：全面覆盖非技术能力评估
- ✅ **AI智能生成**：个性化问题定制
- ✅ **多维度评估**：综合评价回答质量  
- ✅ **完整流程管理**：从开始到结束的全程控制
- ✅ **灵活配置**：支持自定义参数调整

为后续的经历类问题和技术类问题奠定了良好的基础，确保面试流程的专业性和有效性。
