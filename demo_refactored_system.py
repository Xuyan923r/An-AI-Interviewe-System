# -*- coding: utf-8 -*-
"""
重构后的AI面试系统演示脚本

展示新的三阶段模块化架构：
- 第一阶段：非技术问题模块
- 第二阶段：经历类问题模块（基于case.docx深挖）
- 第三阶段：技术类问题模块（B1 < B2 < B3动态难度调整）

每个阶段都是独立完整的模块，具备清晰的接口和完整的功能实现。
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试导入重构后的模块
    from ai_interview.stages import IntegratedInterviewManager
    from ai_interview.stages.stage1_non_technical import NonTechnicalQuestionEngine
    from ai_interview.stages.stage2_experience import ExperienceQuestionEngine
    from ai_interview.stages.stage3_technical import TechnicalQuestionEngine
    
    print("✅ 成功导入重构后的模块")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("使用备用导入...")
    
    # 备用导入方案
    class MockIntegratedInterviewManager:
        def __init__(self):
            print("使用模拟的集成面试管理器")


def demo_integrated_interview_system():
    """演示完整的集成面试系统"""
    
    print("=" * 80)
    print("🎯 重构后的AI面试系统 - 三阶段模块化架构演示")
    print("=" * 80)
    print()
    
    # 初始化集成面试管理器
    interview_manager = IntegratedInterviewManager()
    
    # 模拟候选人数据
    resume_data = {
        'name': '王小明',
        'education': '计算机科学与技术本科',
        'experience': [
            '阿里巴巴 - 高级后端开发工程师 (2021-2023)',
            '字节跳动 - 后端开发工程师 (2019-2021)',
            '美团 - 初级开发工程师 (2018-2019)'
        ],
        'skills': ['Java', 'Python', 'Spring Boot', 'MySQL', 'Redis', 'Docker'],
        'projects': [
            '智能推荐系统 - 基于协同过滤和深度学习的个性化推荐平台',
            '分布式数据处理平台 - 支持大规模数据实时处理的微服务架构',
            '企业级API网关 - 高并发场景下的统一服务入口和流量管控'
        ]
    }
    
    # 模拟职位要求
    jd_data = {
        'position': '资深后端开发工程师',
        'company': '创新科技公司',
        'keywords': ['Java', 'Spring Cloud', '微服务', '分布式', '高并发', 'Redis'],
        'requirements': [
            '5年以上后端开发经验',
            '熟悉微服务架构设计',
            '有大型分布式系统开发经验',
            '具备高并发系统优化能力'
        ]
    }
    
    print("📋 面试信息:")
    print(f"- 候选人: {resume_data['name']}")
    print(f"- 目标职位: {jd_data['position']}")
    print(f"- 公司: {jd_data['company']}")
    print(f"- 主要技能: {', '.join(resume_data['skills'])}")
    print()
    
    # 开始面试
    print("🎬 开始三阶段面试流程")
    print("=" * 50)
    
    try:
        # 启动面试
        first_question = interview_manager.start_interview(resume_data, jd_data)
        
        print(f"✅ 面试启动成功")
        print(f"📊 当前进度: {first_question['interview_progress']}")
        print(f"🎯 当前阶段: {first_question['stage_info']}")
        print()
        
        print("❓ 第一个问题:")
        print(f"   {first_question['question']}")
        print()
        
        # 模拟几轮问答
        mock_responses = [
            "我是王小明，毕业于某大学计算机科学与技术专业。有5年的后端开发经验，主要使用Java和Python。曾在阿里巴巴担任高级后端开发工程师，负责推荐系统的架构设计和开发。",
            "我的职业规划是成为一名技术专家，希望在分布式系统和微服务架构方面有更深入的发展。未来3-5年希望能够带领技术团队，参与大型系统的架构设计。"
        ]
        
        current_question = first_question
        
        for i, response in enumerate(mock_responses, 1):
            print(f"💬 候选人回答 (第{i}轮):")
            print(f"   {response}")
            print()
            
            # 处理回答并获取下一个问题
            next_result = interview_manager.process_answer_and_get_next_question(
                response, current_question
            )
            
            if 'evaluation' in next_result:
                print(f"📈 评估结果: 得分 {next_result['evaluation']['score']:.2f}")
                if 'feedback' in next_result['evaluation']:
                    print(f"💡 反馈: {next_result['evaluation']['feedback']}")
                print()
            
            if 'stage_transition' in next_result:
                print(f"🔄 阶段转换: {next_result['stage_transition']['from_stage']} → {next_result['stage_transition']['to_stage']}")
                print()
            
            if next_result.get('interview_completed'):
                print("🎉 面试完成!")
                print(f"📊 最终评估: {next_result['final_assessment']}")
                break
            
            if 'question' in next_result:
                print(f"❓ 下一个问题:")
                print(f"   {next_result['question']}")
                print()
                current_question = next_result
            
            print("=" * 80)
            print()
        
        # 显示完整面试数据
        complete_data = interview_manager.get_complete_interview_data()
        print("📋 完整面试数据:")
        print(f"- 总问题数: {complete_data['interview_metadata']['total_questions']}")
        print(f"- 平均得分: {complete_data['interview_metadata']['overall_average_score']:.2f}")
        print(f"- 当前阶段: {complete_data['interview_metadata']['current_stage']}")
        
    except Exception as e:
        print(f"❌ 面试过程出错: {e}")
        import traceback
        traceback.print_exc()


def demo_individual_stages():
    """演示各个阶段的独立功能"""
    
    print("\n" + "=" * 80)
    print("🧩 各阶段独立模块演示")
    print("=" * 80)
    
    resume_data = {'name': '测试候选人', 'skills': ['Python', 'Java']}
    jd_data = {'position': '开发工程师', 'keywords': ['Python']}
    
    # 演示第一阶段
    print("\n🎯 第一阶段：非技术问题模块")
    print("-" * 40)
    try:
        stage1 = NonTechnicalQuestionEngine()
        q1 = stage1.start_stage(resume_data, jd_data)
        print(f"✅ 第一阶段问题生成成功")
        print(f"📝 问题类型: {q1.get('question_type', '未知')}")
        print(f"📏 问题长度: {len(q1.get('question', ''))} 字符")
        
        progress1 = stage1.get_progress_info()
        print(f"📊 进度: {progress1['current_question']}/{progress1['total_questions']}")
    except Exception as e:
        print(f"❌ 第一阶段测试失败: {e}")
    
    # 演示第二阶段
    print("\n🎯 第二阶段：经历类问题模块")
    print("-" * 40)
    try:
        stage2 = ExperienceQuestionEngine()
        q2 = stage2.start_stage(resume_data, jd_data)
        print(f"✅ 第二阶段问题生成成功")
        print(f"📝 问题类型: {q2.get('question_type', '未知')}")
        print(f"📏 问题长度: {len(q2.get('question', ''))} 字符")
        
        progress2 = stage2.get_progress_info()
        print(f"📊 进度: {progress2['current_question']}/{progress2['total_questions']}")
    except Exception as e:
        print(f"❌ 第二阶段测试失败: {e}")
    
    # 演示第三阶段
    print("\n🎯 第三阶段：技术类问题模块")
    print("-" * 40)
    try:
        stage3 = TechnicalQuestionEngine()
        q3 = stage3.start_stage(jd_data, resume_data)
        print(f"✅ 第三阶段问题生成成功")
        print(f"📝 问题类型: {q3.get('question_type', '未知')}")
        print(f"📏 问题长度: {len(q3.get('question', ''))} 字符")
        print(f"🎯 当前难度: {q3.get('difficulty', '未知')}")
        
        progress3 = stage3.get_progress_info()
        print(f"📊 进度: {progress3['current_question']}/{progress3['total_questions']}")
        print(f"📈 难度趋势: {progress3.get('difficulty_trend', '未知')}")
    except Exception as e:
        print(f"❌ 第三阶段测试失败: {e}")


def show_refactoring_summary():
    """显示重构总结"""
    
    print("\n" + "=" * 80)
    print("📊 重构架构总结")
    print("=" * 80)
    
    print("""
🏗️ 新架构特点:

1. **模块化设计**
   ├── stage1_non_technical/     # 第一阶段：非技术问题
   ├── stage2_experience/        # 第二阶段：经历类问题  
   ├── stage3_technical/         # 第三阶段：技术类问题
   └── integrated_interview.py   # 集成管理器

2. **独立完整功能**
   - 每个阶段都是独立的模块
   - 具备完整的问题生成、评估、进度管理功能
   - 清晰的接口和数据传递

3. **专业特性实现**
   - 第一阶段：四大问题类型，AI个性化生成
   - 第二阶段：基于case.docx的深挖提问方式
   - 第三阶段：B1 < B2 < B3动态难度调整系统

4. **提升的可读性**
   - 清晰的代码结构和文档
   - 每个阶段都有详细的README说明
   - 完整的使用示例和测试用例

5. **功能完整性**
   - 保持所有原有功能不变
   - 增强了模块间的数据传递
   - 提供了统一的集成管理接口
""")


if __name__ == "__main__":
    try:
        # 运行集成系统演示
        demo_integrated_interview_system()
        
        # 演示各阶段独立功能
        demo_individual_stages()
        
        # 显示重构总结
        show_refactoring_summary()
        
        print("\n✅ 重构后的系统演示完成！")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示已终止")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("请确保所有依赖都已正确安装。")
        import traceback
        traceback.print_exc()
