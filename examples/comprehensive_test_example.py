# -*- coding: utf-8 -*-
"""
反馈系统综合测试示例

该脚本提供了一个详细的测试示例，展示如何使用TestDataGenerator生成各种类型的反馈数据，
并验证反馈系统的各个组件功能。通过运行该脚本，可以直观地了解反馈系统的工作原理和预期输出。
"""

import sys
import os
from datetime import datetime, timedelta
import json
from pprint import pprint

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# 导入测试数据生成器
from tests.test_data_generator import TestDataGenerator

# 导入模型
from models.metadata_model import SourceType, FeedbackType
from models.relation_model import RelationType
from models.feedback_model import FeedbackCollection
from models.content_model import TextContent, StructuredContent

# 导入核心组件
from core.collector.collector import FeedbackCollector
from core.processor.processor import FeedbackProcessor
from core.fusion.hybrid_fusion import HybridFusionEngine
from core.utilizer.utilizer import FeedbackUtilizer

def print_separator(title):
    """
    打印分隔符
    """
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_feedback(feedback, detailed=False):
    """
    打印反馈信息
    """
    print(f"反馈ID: {feedback.feedback_id}")
    print(f"来源: {feedback.metadata.source}")
    print(f"类型: {feedback.metadata.feedback_type}")
    print(f"时间: {feedback.metadata.timestamp}")
    print(f"标签: {feedback.metadata.tags}")
    
    if hasattr(feedback.content, 'text') and feedback.content.text:
        print(f"内容: {feedback.content.text[:100]}{'...' if len(feedback.content.text) > 100 else ''}")
    elif hasattr(feedback.content, 'data') and feedback.content.data:
        print(f"结构化数据: {json.dumps(feedback.content.data, ensure_ascii=False)[:100]}{'...' if len(json.dumps(feedback.content.data, ensure_ascii=False)) > 100 else ''}")
    
    if feedback.relations and detailed:
        print(f"关系数量: {len(feedback.relations)}")
        for relation in feedback.relations:
            print(f"  - 关系类型: {relation.relation_type}, 目标ID: {relation.target_id}, 强度: {relation.strength:.2f}")
    
    print()

def test_case_1_basic_feedback_generation():
    """
    测试用例1：基本反馈生成
    
    测试内容：
    - 生成随机反馈
    - 生成指定类型的反馈
    - 验证反馈的基本属性
    
    预期输出：
    - 随机反馈应包含有效的ID、元数据和内容
    - 指定类型的反馈应符合指定的来源和类型
    """
    print_separator("测试用例1：基本反馈生成")
    
    generator = TestDataGenerator()
    
    # 生成随机反馈
    print("1.1 生成随机反馈:")
    feedback = generator.generate_random_feedback()
    print_feedback(feedback)
    print("验证结果:")
    print(f"  - 反馈ID是否有效: {'是' if feedback.feedback_id else '否'}")
    print(f"  - 元数据是否完整: {'是' if feedback.metadata and feedback.metadata.source and feedback.metadata.feedback_type else '否'}")
    print(f"  - 内容是否有效: {'是' if feedback.content else '否'}")
    
    # 生成指定类型的反馈
    print("\n1.2 生成指定类型的反馈:")
    source_type = SourceType.HUMAN_DOCTOR
    feedback_type = FeedbackType.DIAGNOSTIC
    timestamp = datetime.now()
    
    feedback = generator.generate_random_feedback(
        source_type=source_type,
        feedback_type=feedback_type,
        timestamp=timestamp
    )
    print_feedback(feedback)
    print("验证结果:")
    print(f"  - 来源是否符合预期: {'是' if feedback.metadata.source == source_type else '否'}")
    print(f"  - 类型是否符合预期: {'是' if feedback.metadata.feedback_type == feedback_type else '否'}")
    print(f"  - 时间戳是否符合预期: {'是' if feedback.metadata.timestamp == timestamp else '否'}")

def test_case_2_feedback_set_generation():
    """
    测试用例2：反馈集合生成
    
    测试内容：
    - 生成无关系的反馈集合
    - 生成有关系的反馈集合
    - 验证反馈集合的属性和关系
    
    预期输出：
    - 无关系的反馈集合中每个反馈的relations应为空
    - 有关系的反馈集合中至少有一个反馈包含关系
    """
    print_separator("测试用例2：反馈集合生成")
    
    generator = TestDataGenerator()
    
    # 生成无关系的反馈集合
    print("2.1 生成无关系的反馈集合:")
    count = 3
    feedbacks = generator.generate_feedback_set(count=count, with_relations=False)
    
    print(f"生成的反馈数量: {len(feedbacks)}")
    for i, feedback in enumerate(feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 验证无关系
    all_no_relations = all(len(feedback.relations) == 0 for feedback in feedbacks)
    print("验证结果:")
    print(f"  - 所有反馈都没有关系: {'是' if all_no_relations else '否'}")
    
    # 生成有关系的反馈集合
    print("\n2.2 生成有关系的反馈集合:")
    feedbacks = generator.generate_feedback_set(count=count, with_relations=True)
    
    print(f"生成的反馈数量: {len(feedbacks)}")
    for i, feedback in enumerate(feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback, detailed=True)
    
    # 验证有关系
    has_relations = any(len(feedback.relations) > 0 for feedback in feedbacks)
    print("验证结果:")
    print(f"  - 至少有一个反馈包含关系: {'是' if has_relations else '否'}")

def test_case_3_diverse_feedback_set():
    """
    测试用例3：多样性反馈集合
    
    测试内容：
    - 生成具有不同来源、类型和时间的反馈集合
    - 验证反馈集合的多样性和时间跨度
    
    预期输出：
    - 反馈集合应包含不同的来源和类型
    - 反馈的时间戳应分布在指定的时间跨度内
    """
    print_separator("测试用例3：多样性反馈集合")
    
    generator = TestDataGenerator()
    
    # 生成多样性反馈集合
    print("3.1 生成多样性反馈集合:")
    count = 5
    time_span_days = 10
    feedbacks = generator.generate_diverse_feedback_set(count=count, time_span_days=time_span_days)
    
    # 按时间排序
    feedbacks.sort(key=lambda x: x.metadata.timestamp)
    
    print(f"生成的反馈数量: {len(feedbacks)}")
    for i, feedback in enumerate(feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 验证多样性
    source_types = set(str(feedback.metadata.source) for feedback in feedbacks)
    feedback_types = set(str(feedback.metadata.feedback_type) for feedback in feedbacks)
    
    # 验证时间跨度
    time_diff = feedbacks[-1].metadata.timestamp - feedbacks[0].metadata.timestamp
    
    print("验证结果:")
    print(f"  - 不同来源类型数量: {len(source_types)}")
    print(f"  - 不同反馈类型数量: {len(feedback_types)}")
    print(f"  - 时间跨度: {time_diff.days}天 {time_diff.seconds//3600}小时")
    print(f"  - 时间跨度是否接近预期: {'是' if time_diff.days <= time_span_days + 1 else '否'}")

def test_case_4_medical_scenarios():
    """
    测试用例4：医疗场景生成
    
    测试内容：
    - 生成急诊场景
    - 生成慢性病场景
    - 生成复杂病例场景
    - 验证各场景的特征和关系
    
    预期输出：
    - 急诊场景应包含急诊相关标签和内容
    - 慢性病场景应包含慢性病相关标签和内容
    - 复杂病例场景应包含多种来源的反馈和复杂病例相关标签
    """
    print_separator("测试用例4：医疗场景生成")
    
    generator = TestDataGenerator()
    
    # 生成急诊场景
    print("4.1 生成急诊场景:")
    emergency_feedbacks = generator.generate_medical_scenario(scenario_type="emergency")
    
    print(f"生成的反馈数量: {len(emergency_feedbacks)}")
    for i, feedback in enumerate(emergency_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 验证急诊场景特征
    has_emergency_tag = any("emergency" in feedback.metadata.tags or "urgent" in feedback.metadata.tags 
                          for feedback in emergency_feedbacks)
    
    print("验证结果:")
    print(f"  - 包含急诊相关标签: {'是' if has_emergency_tag else '否'}")
    
    # 生成慢性病场景
    print("\n4.2 生成慢性病场景:")
    chronic_feedbacks = generator.generate_medical_scenario(scenario_type="chronic")
    
    print(f"生成的反馈数量: {len(chronic_feedbacks)}")
    for i, feedback in enumerate(chronic_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 验证慢性病场景特征
    has_chronic_tag = any("diabetes" in feedback.metadata.tags or "follow_up" in feedback.metadata.tags 
                         for feedback in chronic_feedbacks)
    
    print("验证结果:")
    print(f"  - 包含慢性病相关标签: {'是' if has_chronic_tag else '否'}")
    
    # 生成复杂病例场景
    print("\n4.3 生成复杂病例场景:")
    complex_feedbacks = generator.generate_medical_scenario(scenario_type="complex")
    
    print(f"生成的反馈数量: {len(complex_feedbacks)}")
    for i, feedback in enumerate(complex_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 验证复杂病例场景特征
    has_complex_tag = any("autoimmune" in feedback.metadata.tags or "SLE" in feedback.metadata.tags 
                         for feedback in complex_feedbacks)
    
    source_types = set(str(feedback.metadata.source) for feedback in complex_feedbacks)
    
    print("验证结果:")
    print(f"  - 包含复杂病例相关标签: {'是' if has_complex_tag else '否'}")
    print(f"  - 不同来源类型数量: {len(source_types)}")
    print(f"  - 来源类型数量是否>=3: {'是' if len(source_types) >= 3 else '否'}")

def test_case_5_edge_cases():
    """
    测试用例5：边界情况测试
    
    测试内容：
    - 生成空内容反馈
    - 生成极长内容反馈
    - 生成特殊字符内容反馈
    - 生成未来时间戳反馈
    - 生成非常旧的时间戳反馈
    
    预期输出：
    - 各种边界情况的反馈应符合预期特征
    """
    print_separator("测试用例5：边界情况测试")
    
    generator = TestDataGenerator()
    
    # 生成空内容反馈
    print("5.1 生成空内容反馈:")
    empty_feedback = generator.generate_edge_case_feedback(case_type="empty")
    print_feedback(empty_feedback)
    
    print("验证结果:")
    print(f"  - 内容是否为空: {'是' if empty_feedback.content.text == '' else '否'}")
    
    # 生成极长内容反馈
    print("\n5.2 生成极长内容反馈:")
    long_feedback = generator.generate_edge_case_feedback(case_type="long")
    print_feedback(long_feedback)
    
    print("验证结果:")
    print(f"  - 内容长度: {len(long_feedback.content.text)}字符")
    print(f"  - 内容是否超过500字符: {'是' if len(long_feedback.content.text) > 500 else '否'}")
    
    # 生成特殊字符内容反馈
    print("\n5.3 生成特殊字符内容反馈:")
    special_chars_feedback = generator.generate_edge_case_feedback(case_type="special_chars")
    print_feedback(special_chars_feedback)
    
    has_special_chars = any(c in special_chars_feedback.content.text for c in "!@#$%^&*()_+{}")
    print("验证结果:")
    print(f"  - 是否包含特殊字符: {'是' if has_special_chars else '否'}")
    
    # 生成未来时间戳反馈
    print("\n5.4 生成未来时间戳反馈:")
    future_feedback = generator.generate_edge_case_feedback(case_type="future")
    print_feedback(future_feedback)
    
    is_future = future_feedback.metadata.timestamp > datetime.now()
    print("验证结果:")
    print(f"  - 时间戳是否在未来: {'是' if is_future else '否'}")
    
    # 生成非常旧的时间戳反馈
    print("\n5.5 生成非常旧的时间戳反馈:")
    old_feedback = generator.generate_edge_case_feedback(case_type="old")
    print_feedback(old_feedback)
    
    days_old = (datetime.now() - old_feedback.metadata.timestamp).days
    print("验证结果:")
    print(f"  - 时间戳距今天数: {days_old}天")
    print(f"  - 是否超过3000天: {'是' if days_old > 3000 else '否'}")

def test_case_6_feedback_collection():
    """
    测试用例6：反馈集合功能测试
    
    测试内容：
    - 创建反馈集合并添加反馈
    - 按来源查询反馈
    - 按类型查询反馈
    - 按时间范围查询反馈
    
    预期输出：
    - 查询结果应符合查询条件
    """
    print_separator("测试用例6：反馈集合功能测试")
    
    generator = TestDataGenerator()
    collection = FeedbackCollection()
    
    # 生成多样性反馈集合并添加到集合中
    print("6.1 生成反馈并添加到集合:")
    feedbacks = generator.generate_diverse_feedback_set(count=10, time_span_days=30)
    for feedback in feedbacks:
        collection.add_feedback(feedback)
    
    print(f"添加的反馈数量: {len(feedbacks)}")
    
    # 按来源查询
    print("\n6.2 按来源查询(HUMAN_DOCTOR):")
    doctor_feedbacks = collection.get_feedbacks_by_source("human.doctor")
    
    print(f"查询结果数量: {len(doctor_feedbacks)}")
    for i, feedback in enumerate(doctor_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    print("验证结果:")
    all_doctor = all("human.doctor" in str(feedback.metadata.source) for feedback in doctor_feedbacks)
    print(f"  - 所有反馈来源是否都包含'human.doctor': {'是' if all_doctor else '否'}")
    
    # 按类型查询
    print("\n6.3 按类型查询(DIAGNOSTIC):")
    diagnostic_feedbacks = collection.get_feedbacks_by_type("diagnostic")
    
    print(f"查询结果数量: {len(diagnostic_feedbacks)}")
    for i, feedback in enumerate(diagnostic_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    print("验证结果:")
    all_diagnostic = all("diagnostic" in str(feedback.metadata.feedback_type) for feedback in diagnostic_feedbacks)
    print(f"  - 所有反馈类型是否都是'diagnostic': {'是' if all_diagnostic else '否'}")
    
    # 按时间范围查询
    print("\n6.4 按时间范围查询(最近15天):")
    start_time = datetime.now() - timedelta(days=15)
    end_time = datetime.now()
    recent_feedbacks = collection.get_feedbacks_by_time_range(start_time, end_time)
    
    print(f"查询结果数量: {len(recent_feedbacks)}")
    for i, feedback in enumerate(recent_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    print("验证结果:")
    all_in_range = all(start_time <= feedback.metadata.timestamp <= end_time for feedback in recent_feedbacks)
    print(f"  - 所有反馈时间是否都在指定范围内: {'是' if all_in_range else '否'}")

def test_case_7_system_pipeline():
    """
    测试用例7：系统完整流程测试
    
    测试内容：
    - 生成复杂医疗场景数据
    - 使用反馈收集器收集反馈
    - 使用反馈处理器处理反馈
    - 使用融合引擎融合反馈
    - 使用反馈利用器生成行动计划
    
    预期输出：
    - 系统应能完成从数据生成到行动计划生成的完整流程
    """
    print_separator("测试用例7：系统完整流程测试")
    
    # 初始化测试数据生成器
    generator = TestDataGenerator()
    
    # 生成复杂医疗场景数据
    print("7.1 生成复杂医疗场景数据:")
    feedbacks = generator.generate_medical_scenario(scenario_type="complex")
    print(f"生成的反馈数量: {len(feedbacks)}")
    
    # 初始化反馈系统组件
    collector = FeedbackCollector()
    processor = FeedbackProcessor()
    fusion_engine = HybridFusionEngine()
    utilizer = FeedbackUtilizer()
    
    # 收集反馈
    print("\n7.2 收集反馈:")
    for feedback in feedbacks:
        collector.collect(feedback)
    
    collected_feedbacks = collector.get_all_feedbacks()
    print(f"收集的反馈数量: {len(collected_feedbacks)}")
    
    # 处理反馈
    print("\n7.3 处理反馈:")
    processed_feedbacks = []
    for feedback in collected_feedbacks:
        processed_feedback = processor.process(feedback)
        processed_feedbacks.append(processed_feedback)
        print(f"处理反馈: {feedback.feedback_id}")
        print(f"  - 可靠性评分: {processed_feedback.get_reliability():.2f}")
    
    # 融合反馈
    print("\n7.4 融合反馈:")
    fused_result = fusion_engine.fuse(processed_feedbacks)
    print("融合结果:")
    pprint(fused_result)
    
    # 利用反馈
    print("\n7.5 利用反馈:")
    action_plan = utilizer.utilize(fused_result)
    print("生成的行动计划:")
    pprint(action_plan)
    
    print("\n验证结果:")
    print(f"  - 是否完成完整流程: {'是' if action_plan else '否'}")

def main():
    """
    主函数
    """
    print("反馈系统综合测试示例")
    print("该脚本提供了一个详细的测试示例，展示如何使用TestDataGenerator生成各种类型的反馈数据，")
    print("并验证反馈系统的各个组件功能。通过运行该脚本，可以直观地了解反馈系统的工作原理和预期输出。")
    print("\n可以通过命令行参数选择要运行的测试用例，例如：python comprehensive_test_example.py 1 2 3")
    print("如果不提供参数，则运行所有测试用例。")
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        test_cases = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    else:
        test_cases = range(1, 8)  # 默认运行所有测试用例
    
    # 运行选定的测试用例
    test_functions = {
        1: test_case_1_basic_feedback_generation,
        2: test_case_2_feedback_set_generation,
        3: test_case_3_diverse_feedback_set,
        4: test_case_4_medical_scenarios,
        5: test_case_5_edge_cases,
        6: test_case_6_feedback_collection,
        7: test_case_7_system_pipeline
    }
    
    for case_num in test_cases:
        if case_num in test_functions:
            test_functions[case_num]()

if __name__ == "__main__":
    main()