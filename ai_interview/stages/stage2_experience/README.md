# 🎯 第二阶段：经历类问题模块

## 📋 模块概述

第二阶段经历类问题模块是AI面试系统的核心环节，专注于深度挖掘候选人的项目经历和技术能力。本模块完全基于**case.docx**的专业深挖提问方式，实现了从基础经历介绍到深度技术追问的完整流程。

## 🎪 核心特性

### 1. 固定首问机制
- **第一个问题固定**：要求候选人详细介绍简历上的一个经历
- **个性化展示**：根据简历内容动态生成经历列表
- **全面覆盖**：引导候选人从背景、职责、技术、挑战、成果等维度描述

### 2. 基于case.docx的深挖提问
- **完整集成**：将case.docx的41段深挖示例作为AI系统提示词
- **专业风格**：仿照真实技术面试官的深挖方式
- **五大原则**：技术深度、数据细节、架构决策、实际效果、团队协作

### 3. 智能技术分析
- **关键词提取**：自动识别经历中的技术关键词
- **深度追问**：基于技术栈生成针对性问题
- **避重复机制**：确保每轮追问都有新的探索角度

### 4. 多维度评估
- **技术准确性**：评估技术描述的专业性和准确性
- **项目复杂度**：分析项目的技术挑战和规模
- **个人贡献**：了解候选人的具体角色和贡献
- **真实经验**：判断经历的真实性和深度

## 🏗️ 架构设计

### 模块结构
```
stage2_experience/
├── __init__.py                  # 模块初始化和导出
├── experience_engine.py         # 主引擎，控制整个流程
├── deep_dive_generator.py       # 深挖问题生成器
├── experience_evaluator.py      # 经历回答评估器
├── case_prompts.py              # case.docx深挖模板
└── README.md                    # 本文档
```

### 类关系图
```
ExperienceQuestionEngine (主引擎)
    ├── DeepDiveQuestionGenerator (深挖生成)
    │   └── CaseBasedPrompts (case.docx模板)
    └── ExperienceEvaluator (回答评估)
```

## 🛠️ 详细实现

### 1. ExperienceQuestionEngine (主引擎)

**职责**：控制第二阶段的整个面试流程

**核心方法**：
```python
# 开始第二阶段
start_stage(resume_data: Dict, jd_data: Dict) -> Dict

# 生成固定的第一个问题
generate_initial_experience_question() -> Dict

# 生成后续深挖追问
generate_follow_up_question(user_experience_description: str) -> Dict

# 处理用户回答
process_answer(user_response: str, question_data: Dict) -> Dict

# 获取阶段总结
get_stage_summary() -> Dict
```

**状态管理**：
- `current_question_index`: 当前问题索引
- `max_questions`: 最大问题数（默认3题）
- `current_experience`: 当前讨论的经历
- `technical_keywords`: 技术关键词列表
- `asked_questions`: 已提问问题列表

### 2. CaseBasedPrompts (case.docx模板)

**职责**：提供基于case.docx的深挖提问模板和系统提示词

**核心内容**：
```python
@staticmethod
def get_system_prompt() -> str:
    """获取完整的系统提示词，包含case.docx的所有深挖示例"""
    
@staticmethod 
def get_fallback_questions() -> dict:
    """获取备用深挖问题"""
```

**案例示例**：
- **绿色金融问答系统**：微调、RAG、模型选择等深挖
- **古典文学AI项目**：韵律状态机、Token Masking等细节
- **企业知识库系统**：向量检索、对比学习等架构
- **Speculative Decoding优化**：草稿头蒸馏、动态选择等算法
- **DiffuText项目**：扩散模型、变分推断等前沿技术
- **跨平台竞价系统**：联邦学习、差分隐私等复杂场景

### 3. DeepDiveQuestionGenerator (深挖生成器)

**职责**：基于case.docx风格生成专业的深挖追问

**生成策略**：
1. **AI优先策略**：使用大语言模型结合case.docx模板生成
2. **智能分类**：根据技术关键词选择合适的追问角度
3. **避重复机制**：分析已提问历史，避免相似问题

**深挖生成流程**：
```python
def generate_deep_dive_question(user_experience, question_history, technical_keywords):
    # 1. 构建包含case.docx示例的提示词
    prompt = _build_deep_dive_prompt(user_experience, question_history, technical_keywords)
    
    # 2. 调用AI生成深挖问题
    ai_question = _generate_ai_deep_dive_question(prompt)
    
    # 3. 格式清理和质量检查
    return _clean_question_format(ai_question)
```

**问题分类**：
- `technical_details`: 技术实现细节
- `performance_metrics`: 性能指标和优化
- `architecture_design`: 架构设计决策
- `business_impact`: 业务价值和效果
- `team_collaboration`: 团队协作和管理

### 4. ExperienceEvaluator (经历评估器)

**职责**：多维度评估经历类问题的回答质量

**评估维度**：

#### 经历介绍请求 (`initial_experience_request`)
- **技术深度** (30%)：技术描述的深度和专业性
- **项目复杂度** (25%)：项目的技术复杂度和挑战性
- **个人贡献** (20%)：个人在项目中的具体贡献和角色
- **问题解决能力** (15%)：遇到问题时的分析和解决能力
- **表达清晰度** (10%)：表达是否清晰、逻辑性强

#### 深挖追问 (`deep_dive`)
- **技术准确性** (40%)：技术回答的准确性和专业性
- **细节丰富度** (30%)：回答中技术细节的丰富程度
- **真实经验体现** (20%)：是否体现出真实的项目经验
- **逻辑思维** (10%)：回答的逻辑性和条理性

**评估流程**：
```python
def evaluate_response(user_response, question_data, context):
    # 1. AI智能评估
    ai_evaluation = _ai_evaluate(user_response, question_data, context)
    
    # 2. 技术关键词分析
    tech_analysis = _analyze_technical_content(user_response, technical_keywords)
    
    # 3. 项目经验分析
    experience_analysis = _analyze_project_experience(user_response, question_type)
    
    # 4. 综合评分计算
    final_score = _calculate_final_score(ai_evaluation, tech_analysis, experience_analysis)
    
    return evaluation_result
```

## 📊 数据流程

### 输入数据格式

**简历数据** (`resume_data`)：
```python
{
    'name': '候选人姓名',
    'projects': [
        '智能推荐系统 - 基于协同过滤和深度学习的个性化推荐平台',
        '分布式数据处理平台 - 支持大规模数据实时处理的微服务架构'
    ],
    'experience': [
        '阿里巴巴 - 高级后端开发工程师 (2021-2023)',
        '字节跳动 - 后端开发工程师 (2019-2021)'
    ],
    'skills': ['Python', 'Java', 'Spring Boot', 'Redis', 'MySQL']
}
```

### 输出数据格式

**第一个问题**（经历介绍请求）：
```python
{
    'question': '我看到您的简历中有以下几项经历：\n\n- 项目经历：智能推荐系统...\n\n请您选择其中一项您觉得最有代表性的经历，详细介绍...',
    'question_type': 'initial_experience_request',
    'source': 'experience_engine',
    'stage': '第二阶段：经历类问题',
    'question_number': 1,
    'total_questions': 3,
    'category': '经历介绍'
}
```

**深挖追问**：
```python
{
    'question': '关于Lambda架构中的流处理层，为什么选择Flink而非Storm或Kafka Streams？Flink的状态管理在你们的场景下如何优化？',
    'question_type': 'deep_dive',
    'source': 'ai_generated_deep_dive',
    'stage': '第二阶段：经历类问题',
    'question_number': 2,
    'total_questions': 3,
    'tech_keywords': ['Lambda架构', 'Flink', 'Storm', 'Kafka'],
    'category': '深挖追问'
}
```

**评估结果**：
```python
{
    'score': 0.82,
    'ai_evaluation': {
        'scores': {
            '技术深度': 0.85,
            '项目复杂度': 0.80,
            '个人贡献': 0.85,
            '问题解决能力': 0.78,
            '表达清晰度': 0.80
        },
        'technical_highlights': '对Lambda架构有深入理解，Flink状态管理优化有实际经验',
        'improvement_suggestions': '可以补充更多性能优化的具体数据',
        'overall_comment': '回答展现了扎实的大数据架构经验和深度技术理解'
    },
    'technical_analysis': {
        'keyword_coverage': 0.75,
        'mentioned_keywords': ['Lambda架构', 'Flink', 'Spark', 'Redis'],
        'detail_score': 0.80,
        'number_score': 0.60,
        'technical_numbers': ['3ms', '92%', '50亿次']
    },
    'experience_analysis': {
        'experience_score': 0.85,
        'scale_score': 0.90,
        'length_score': 0.85,
        'response_length': 456
    }
}
```

**阶段总结**：
```python
{
    'stage_name': '第二阶段：经历类问题',
    'questions_asked': 3,
    'total_questions': 3,
    'average_score': 0.78,
    'question_responses': [问答记录],
    'detailed_scores': [0.82, 0.76, 0.77],
    'current_experience_summary': '我想详细介绍一下我在阿里巴巴负责的智能推荐系统项目...',
    'technical_keywords_discussed': ['推荐系统', 'Lambda架构', 'Flink', 'Transformer'],
    'stage_completed': True,
    'next_stage': '第三阶段：技术类问题'
}
```

## 🚀 使用示例

### 基本使用流程

```python
from ai_interview.stages.stage2_experience import ExperienceQuestionEngine

# 1. 初始化引擎
engine = ExperienceQuestionEngine()

# 2. 准备数据
resume_data = {
    'name': '李明',
    'projects': [
        '智能推荐系统 - 基于协同过滤和深度学习的个性化推荐平台',
        '分布式数据处理平台 - 支持大规模数据实时处理的微服务架构'
    ],
    'experience': ['阿里巴巴-高级后端开发工程师'],
    'skills': ['Python', 'Java', 'Flink', 'Redis']
}

jd_data = {
    'position': '资深后端开发工程师',
    'keywords': ['Java', 'Spring Cloud', '微服务', '大数据']
}

# 3. 开始第二阶段（第一个问题：经历介绍请求）
first_question = engine.start_stage(resume_data, jd_data)
print(f"第一个问题: {first_question['question']}")

# 4. 处理第一个回答（用户详细介绍经历）
user_experience = """
我想详细介绍一下我在阿里巴巴负责的智能推荐系统项目。这个项目是为了提升淘宝APP的商品推荐精准度，服务数亿用户的个性化推荐需求。

项目背景是当时的推荐系统主要基于传统的协同过滤算法，准确率约65%，而且无法很好地处理冷启动问题和实时性要求。我作为后端架构师，负责整个推荐引擎的设计和实现。

技术架构方面，我们采用了Lambda架构，包括批处理层、流处理层和服务层。批处理层使用Spark处理历史数据，训练深度学习模型（主要是基于Transformer的序列推荐模型）；流处理层使用Flink处理实时用户行为，更新用户画像和实时特征；服务层使用Spring Cloud微服务架构，提供高并发的推荐API。
"""

evaluation = engine.process_answer(user_experience, first_question)
print(f"第一题评分: {evaluation['score']}")

# 5. 生成深挖追问
if engine.should_continue():
    deep_dive_question = engine.generate_follow_up_question(user_experience)
    print(f"深挖问题: {deep_dive_question['question']}")

# 6. 继续处理后续回答...

# 7. 获取阶段总结
summary = engine.get_stage_summary()
print(f"阶段完成，平均分: {summary['average_score']}")
print(f"技术关键词: {summary['technical_keywords_discussed']}")
```

### 高级使用示例

```python
# 自定义配置
engine = ExperienceQuestionEngine()
engine.max_questions = 4  # 增加到4题

# 获取实时进度
progress = engine.get_progress_info()
print(f"进度: {progress['current_question']}/{progress['total_questions']}")
print(f"已提取关键词: {progress['keywords_extracted']}个")

# 查看技术关键词
if progress['experience_provided']:
    print(f"技术关键词: {engine.technical_keywords}")

# 重置引擎状态
engine.reset()
```

## 🎯 深挖提问五大原则

### 1. **技术深度**
- 不满足于表面描述，深入技术实现细节
- 为什么选择某个技术方案？
- 具体的参数设置和调优过程
- 遇到的技术挑战和解决方案

### 2. **数据细节**
- 关注具体的数据和指标
- 数据量、准确率、延迟等具体数字
- 实验对比和A/B测试结果
- 性能优化的具体提升幅度

### 3. **架构决策**
- 了解架构选择的思考过程
- 技术选型的权衡考虑
- 替代方案的对比分析
- 可扩展性和维护性考虑

### 4. **实际效果**
- 关注项目的实际应用和价值
- 业务价值和用户反馈
- 部署规模和使用情况
- 后续优化和迭代计划

### 5. **团队协作**
- 了解在项目中的具体角色
- 个人承担的具体工作内容
- 与团队成员的协作方式
- 项目管理和时间安排

## ⚙️ 配置选项

### 问题数量调整
```python
# 在引擎初始化后修改
engine.max_questions = 4  # 默认为3
```

### 技术关键词模式扩展
```python
# 在experience_engine.py中扩展tech_patterns
tech_patterns = [
    r'\b(新技术关键词)\b',
    # 添加更多模式
]
```

### 评估权重调整
```python
# 在experience_evaluator.py中修改evaluation_criteria
evaluation_criteria = {
    "initial_experience_request": {
        "technical_depth": 0.4,      # 调整权重
        "project_complexity": 0.3,
        "personal_contribution": 0.2,
        "problem_solving": 0.1
    }
}
```

## 🧪 测试用例

### 单元测试示例

```python
def test_initial_question_generation():
    engine = ExperienceQuestionEngine()
    
    resume_data = {
        'projects': ['智能推荐系统'],
        'experience': ['阿里巴巴-工程师']
    }
    
    question = engine.start_stage(resume_data, {})
    
    assert question['question_type'] == 'initial_experience_request'
    assert '请您选择其中一项' in question['question']
    assert question['question_number'] == 1

def test_deep_dive_generation():
    generator = DeepDiveQuestionGenerator()
    
    user_experience = "我在项目中使用了Flink进行实时流处理..."
    question_history = [{'question_type': 'initial_experience_request'}]
    technical_keywords = ['Flink', '流处理']
    
    question = generator.generate_deep_dive_question(
        user_experience, question_history, technical_keywords
    )
    
    assert question['question_type'] == 'deep_dive'
    assert len(question['question']) > 10

def test_evaluation():
    evaluator = ExperienceEvaluator()
    
    response = "我们选择Flink是因为其强大的状态管理能力..."
    question_data = {'question_type': 'deep_dive'}
    context = {'technical_keywords': ['Flink']}
    
    result = evaluator.evaluate_response(response, question_data, context)
    
    assert 0 <= result['score'] <= 1
    assert result['technical_analysis'] is not None
```

## ⚠️ 注意事项

1. **依赖环境**：需要ollama服务正常运行，确保AI模型可用
2. **网络连接**：深挖问题生成和评估需要稳定网络
3. **case.docx完整性**：确保所有深挖示例都正确集成
4. **容错机制**：AI失败时自动切换到备用问题方案

## 🔧 故障排除

### 常见问题

1. **深挖问题生成失败**
   ```python
   # 检查ollama服务状态
   # 自动降级到备用问题
   fallback_question = _get_fallback_deep_dive_question()
   ```

2. **技术关键词提取不准确**
   ```python
   # 扩展技术关键词模式
   # 手动补充特定领域的技术词汇
   ```

3. **评估结果异常**
   ```python
   # 使用备用评估方法
   # 检查输入数据的完整性
   ```

## 🎊 case.docx集成详情

### 完整案例覆盖
- ✅ **绿色金融问答系统**：微调、RAG、比赛评判
- ✅ **古典文学AI项目**：韵律状态机、Token Masking
- ✅ **企业知识库系统**：向量检索、对比学习
- ✅ **Speculative Decoding**：草稿头蒸馏、动态选择
- ✅ **DiffuText项目**：扩散模型、变分推断
- ✅ **跨平台竞价系统**：联邦学习、差分隐私

### 深挖问题示例
```python
# 绿色金融项目深挖
"微调时是否比较怎样选择batch size和上下文窗口长度效果最好？"
"为什么选择DeepSeek-r1-7b作为基模？"

# 古典文学AI深挖  
"Beam Search中如何实现韵律状态机？请举例说明《浣溪沙》词牌的约束。"
"动态Token Masking如何实现'禁止重复意象'？"

# 企业知识库深挖
"微调时为什么选择对比学习框架而非交叉熵？"
"Faiss索引选择IVF-PQ而非HNSW的关键考量是什么？"
```

## 🎯 总结

第二阶段经历类问题模块完全按照您的要求实现：

- ✅ **固定首问**：第一个问题限定为经历介绍请求
- ✅ **case.docx集成**：完整的深挖提问方式和系统提示词
- ✅ **专业深挖**：基于真实技术面试的深度追问
- ✅ **智能分析**：技术关键词提取和针对性评估
- ✅ **完整流程**：从经历介绍到深挖追问的全程管理

这一模块让AI面试系统能够像资深技术面试官一样，深入挖掘候选人的项目经历和技术能力，真正评估其实际水平和经验深度！🎯
