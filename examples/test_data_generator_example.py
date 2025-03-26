# -*- coding: utf-8 -*-
"""
测试数据生成器示例

该脚本展示了如何使用TestDataGenerator生成各种类型的测试数据，并提供了预期的输出结果。
"""

import sys
import os
from datetime import datetime
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# 导入测试数据生成器
from tests.test_data_generator import TestDataGenerator

# 导入模型
from models.metadata_model import SourceType, FeedbackType
from models.relation_model import RelationType

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

def example_1_random_feedback():
    """
    示例1：生成随机反馈
    
    预期输出：
    - 一个随机生成的反馈，包含随机的来源、类型和内容
    - 一个指定来源和类型的反馈
    """
    print_separator("示例1：生成随机反馈")
    
    generator = TestDataGenerator()
    
    print("1.1 生成默认随机反馈:")
    feedback = generator.generate_random_feedback()
    print_feedback(feedback)
    print("预期结果: 一个随机生成的反馈，包含随机的来源、类型和内容")
    
    print("\n1.2 生成指定类型的反馈:")
    feedback = generator.generate_random_feedback(
        source_type=SourceType.HUMAN_DOCTOR,
        feedback_type=FeedbackType.DIAGNOSTIC,
        timestamp=datetime.now()
    )
    print_feedback(feedback)
    print("预期结果: 一个来源为医生、类型为诊断的反馈，内容应该是医生的诊断信息")

def example_2_feedback_set():
    """
    示例2：生成反馈集合
    
    预期输出：
    - 3个无关系的反馈
    - 3个有关系的反馈，每个反馈至少有一个关系
    """
    print_separator("示例2：生成反馈集合")
    
    generator = TestDataGenerator()
    
    print("2.1 生成无关系的反馈集合:")
    feedbacks = generator.generate_feedback_set(count=3, with_relations=False)
    for i, feedback in enumerate(feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    print("预期结果: 3个无关系的反馈，每个反馈的relations列表应该为空")
    
    print("\n2.2 生成有关系的反馈集合:")
    feedbacks = generator.generate_feedback_set(count=3, with_relations=True)
    for i, feedback in enumerate(feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback, detailed=True)
    print("预期结果: 3个有关系的反馈，至少有一个反馈的relations列表不为空")

def example_3_diverse_feedback_set():
    """
    示例3：生成多样性反馈集合
    
    预期输出：
    - 5个不同来源、不同类型、不同时间的反馈
    - 时间跨度应该接近10天
    """
    print_separator("示例3：生成多样性反馈集合")
    
    generator = TestDataGenerator()
    
    print("3.1 生成多样性反馈集合:")
    feedbacks = generator.generate_diverse_feedback_set(count=5, time_span_days=10)
    
    # 按时间排序
    feedbacks.sort(key=lambda x: x.metadata.timestamp)
    
    for i, feedback in enumerate(feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 验证时间跨度
    time_diff = feedbacks[-1].metadata.timestamp - feedbacks[0].metadata.timestamp
    print(f"时间跨度: {time_diff.days}天 {time_diff.seconds//3600}小时")
    print(f"预期时间跨度: 10天")
    print("预期结果: 5个不同来源、不同类型的反馈，时间跨度接近10天")

def example_4_medical_scenarios():
    """
    示例4：生成医疗场景
    
    预期输出：
    - 急诊场景：包含患者反馈、医生诊断、检查结果等
    - 慢性病场景：包含患者反馈、医生建议、监测数据等
    - 复杂病例场景：包含多个医生的会诊、多种检查结果等
    """
    print_separator("示例4：生成医疗场景")
    
    generator = TestDataGenerator()
    
    print("4.1 生成急诊场景:")
    emergency_feedbacks = generator.generate_medical_scenario(scenario_type="emergency")
    print(f"生成的反馈数量: {len(emergency_feedbacks)}")
    for i, feedback in enumerate(emergency_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    print("预期结果: 一组描述急诊场景的反馈，包含患者反馈、医生诊断、检查结果等")
    
    print("\n4.2 生成慢性病场景:")
    chronic_feedbacks = generator.generate_medical_scenario(scenario_type="chronic")
    print(f"生成的反馈数量: {len(chronic_feedbacks)}")
    for i, feedback in enumerate(chronic_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    print("预期结果: 一组描述慢性病场景的反馈，包含患者反馈、医生建议、监测数据等")
    
    print("\n4.3 生成复杂病例场景:")
    complex_feedbacks = generator.generate_medical_scenario(scenario_type="complex")
    print(f"生成的反馈数量: {len(complex_feedbacks)}")
    for i, feedback in enumerate(complex_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    print("预期结果: 一组描述复杂病例场景的反馈，包含多个医生的会诊、多种检查结果等")

def example_5_edge_cases():
    """
    示例5：生成边界情况
    
    预期输出：
    - 空内容反馈
    - 极长内容反馈
    - 特殊字符内容反馈
    - 未来时间戳反馈
    - 非常旧的时间戳反馈
    """
    print_separator("示例5：生成边界情况")
    
    generator = TestDataGenerator()
    
    print("5.1 生成空内容反馈:")
    empty_feedback = generator.generate_edge_case_feedback(case_type="empty")
    print_feedback(empty_feedback)
    print("预期结果: 一个内容为空的反馈")
    
    print("\n5.2 生成极长内容反馈:")
    long_feedback = generator.generate_edge_case_feedback(case_type="long")
    print_feedback(long_feedback)
    print("预期结果: 一个内容非常长的反馈")
    
    print("\n5.3 生成特殊字符内容反馈:")
    special_chars_feedback = generator.generate_edge_case_feedback(case_type="special_chars")
    print_feedback(special_chars_feedback)
    print("预期结果: 一个包含特殊字符的反馈")
    
    print("\n5.4 生成未来时间戳反馈:")
    future_feedback = generator.generate_edge_case_feedback(case_type="future")
    print_feedback(future_feedback)
    print("预期结果: 一个时间戳在未来的反馈")
    
    print("\n5.5 生成非常旧的时间戳反馈:")
    old_feedback = generator.generate_edge_case_feedback(case_type="old")
    print_feedback(old_feedback)
    print("预期结果: 一个时间戳非常旧的反馈")

def example_6_feedback_by_type():
    """
    示例6：生成特定类型的反馈
    
    预期输出：
    - 4个诊断类型的反馈，包含关系
    - 3个治疗类型的反馈，不包含关系
    """
    print_separator("示例6：生成特定类型的反馈")
    
    generator = TestDataGenerator()
    
    print("6.1 生成诊断类型的反馈:")
    diagnostic_feedbacks = generator.generate_feedback_by_type(
        feedback_type=FeedbackType.DIAGNOSTIC,
        count=4,
        with_relations=True
    )
    
    print(f"生成的反馈数量: {len(diagnostic_feedbacks)}")
    for i, feedback in enumerate(diagnostic_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback, detailed=True)
    
    # 检查是否生成了关系
    has_relations = False
    for feedback in diagnostic_feedbacks:
        if len(feedback.relations) > 0:
            has_relations = True
            break
    
    print(f"是否包含关系: {has_relations}")
    print("预期结果: 4个诊断类型的反馈，至少有一个反馈包含关系")
    
    print("\n6.2 生成治疗类型的反馈:")
    therapeutic_feedbacks = generator.generate_feedback_by_type(
        feedback_type=FeedbackType.THERAPEUTIC,
        count=3,
        with_relations=False
    )
    
    print(f"生成的反馈数量: {len(therapeutic_feedbacks)}")
    for i, feedback in enumerate(therapeutic_feedbacks, 1):
        print(f"反馈 {i}:")
        print_feedback(feedback)
    
    # 检查是否生成了关系
    has_relations = False
    for feedback in therapeutic_feedbacks:
        if len(feedback.relations) > 0:
            has_relations = True
            break
    
    print(f"是否包含关系: {has_relations}")
    print("预期结果: 3个治疗类型的反馈，不包含关系")

def main():
    """
    主函数
    """
    print("测试数据生成器示例")
    print("该脚本展示了如何使用TestDataGenerator生成各种类型的测试数据，并提供了预期的输出结果。")
    print("运行这些示例可以验证TestDataGenerator的功能是否正常。")
    print("\n可以通过命令行参数选择要运行的示例，例如：python test_data_generator_example.py 1 2 3")
    print("如果不提供参数，则运行所有示例。")
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        examples = [int(arg) for arg in sys.argv[1:] if arg.isdigit()]
    else:
        examples = range(1, 7)  # 默认运行所有示例
    
    # 运行选定的示例
    example_functions = {
        1: example_1_random_feedback,
        2: example_2_feedback_set,
        3: example_3_diverse_feedback_set,
        4: example_4_medical_scenarios,
        5: example_5_edge_cases,
        6: example_6_feedback_by_type
    }
    
    for example_num in examples:
        if example_num in example_functions:
            example_functions[example_num]()

if __name__ == "__main__":
    main()