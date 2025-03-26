# -*- coding: utf-8 -*-
"""
反馈系统集成测试示例

该脚本展示了如何使用测试数据生成器生成各种类型的反馈数据，并测试反馈系统的各个组件。
"""

import sys
import os
from datetime import datetime
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

def test_generate_random_feedback():
    """
    测试随机反馈生成
    """
    print_separator("测试随机反馈生成")
    
    generator = TestDataGenerator()
    
    # 生成默认随机反馈
    print("生成默认随机反馈:")
    feedback = generator.generate_random_feedback()
    print_feedback(feedback)
    
    # 生成指定类型的反馈
    print("生成指定类型的反馈:")
    feedback = generator.generate_random_feedback(
        source_type=SourceType.HUMAN_DOCTOR,
        feedback_type=FeedbackType.DIAGNOSTIC,
        timestamp=datetime.now()
    )
    print_feedback(feedback)

def test_generate_feedback_set():
    """
    测试反馈集合生成
    """
    print_separator("测试反馈集合生成")
    
    generator = TestDataGenerator()
    
    # 生成无关系的反馈集合
    print("生成无关系的反馈集合:")
    feedbacks = generator.generate_feedback_set(count=3, with_relations=False)
    for feedback in feedbacks:
        print_feedback(feedback)
    
    # 生成有关系的反馈集合
    print("生成有关系的反馈集合:")
    feedbacks = generator.generate_feedback_set(count=3, with_relations=True)
    for feedback in feedbacks:
        print_feedback(feedback, detailed=True)

def test_generate_diverse_feedback_set():
    """
    测试多样性反馈集合生成
    """
    print_separator("测试多样性反馈集合生成")
    
    generator = TestDataGenerator()
    
    # 生成多样性反馈集合
    print("生成多样性反馈集合:")
    feedbacks = generator.generate_diverse_feedback_set(count=5, time_span_days=10)
    
    # 按时间排序
    feedbacks.sort(key=lambda x: x.metadata.timestamp)
    
    for feedback in feedbacks:
        print_feedback(feedback)
    
    # 验证时间跨度
    time_diff = feedbacks[-1].metadata.timestamp - feedbacks[0].metadata.timestamp
    print(f"时间跨度: {time_diff.days}天 {time_diff.seconds//3600}小时")
    print(f"预期时间跨度: 10天")

def test_medical_scenarios():
    """
    测试医疗场景生成
    """
    print_separator("测试医疗场景生成")
    
    generator = TestDataGenerator()
    
    # 测试急诊场景
    print("生成急诊场景:")
    emergency_feedbacks = generator.generate_medical_scenario(scenario_type="emergency")
    print(f"生成的反馈数量: {len(emergency_feedbacks)}")
    for feedback in emergency_feedbacks:
        print_feedback(feedback)
    
    # 测试慢性病场景
    print("\n生成慢性病场景:")
    chronic_feedbacks = generator.generate_medical_scenario(scenario_type="chronic")
    print(f"生成的反馈数量: {len(chronic_feedbacks)}")
    for feedback in chronic_feedbacks:
        print_feedback(feedback)
    
    # 测试复杂病例场景
    print("\n生成复杂病例场景:")
    complex_feedbacks = generator.generate_medical_scenario(scenario_type="complex")
    print(f"生成的反馈数量: {len(complex_feedbacks)}")
    for feedback in complex_feedbacks:
        print_feedback(feedback)

def test_edge_cases():
    """
    测试边界情况
    """
    print_separator("测试边界情况")
    
    generator = TestDataGenerator()
    
    # 测试空内容反馈
    print("生成空内容反馈:")
    empty_feedback = generator.generate_edge_case_feedback(case_type="empty")
    print_feedback(empty_feedback)
    
    # 测试极长内容反馈
    print("生成极长内容反馈:")
    long_feedback = generator.generate_edge_case_feedback(case_type="long")
    print_feedback(long_feedback)
    
    # 测试特殊字符内容反馈
    print("生成特殊字符内容反馈:")
    special_chars_feedback = generator.generate_edge_case_feedback(case_type="special_chars")
    print_feedback(special_chars_feedback)
    
    # 测试未来时间戳反馈
    print("生成未来时间戳反馈:")
    future_feedback = generator.generate_edge_case_feedback(case_type="future")
    print_feedback(future_feedback)
    
    # 测试非常旧的时间戳反馈
    print("生成非常旧的时间戳反馈:")
    old_feedback = generator.generate_edge_case_feedback(case_type="old")
    print_feedback(old_feedback)

def test_feedback_collection():
    """
    测试反馈集合功能
    """
    print_separator("测试反馈集合功能")
    
    generator = TestDataGenerator()
    collection = FeedbackCollection()
    
    # 生成多样性反馈集合并添加到集合中
    feedbacks = generator.generate_diverse_feedback_set(count=10, time_span_days=30)
    for feedback in feedbacks:
        collection.add_feedback(feedback)
    
    # 测试按来源查询
    print("按来源查询(HUMAN_DOCTOR):")
    doctor_feedbacks = collection.get_feedbacks_by_source("human.doctor")
    print(f"查询结果数量: {len(doctor_feedbacks)}")
    for feedback in doctor_feedbacks:
        print_feedback(feedback)
    
    # 测试按类型查询
    print("\n按类型查询(DIAGNOSTIC):")
    diagnostic_feedbacks = collection.get_feedbacks_by_type("diagnostic")
    print(f"查询结果数量: {len(diagnostic_feedbacks)}")
    for feedback in diagnostic_feedbacks:
        print_feedback(feedback)
    
    # 测试按时间范围查询
    print("\n按时间范围查询(最近15天):")
    start_time = datetime.now() - datetime.timedelta(days=15)
    end_time = datetime.now()
    recent_feedbacks = collection.get_feedbacks_by_time_range(start_time, end_time)
    print(f"查询结果数量: {len(recent_feedbacks)}")
    for feedback in recent_feedbacks:
        print_feedback(feedback)

def test_feedback_system_pipeline():
    """
    测试反馈系统完整流程
    """
    print_separator("测试反馈系统完整流程")
    
    # 初始化测试数据生成器
    generator = TestDataGenerator()
    
    # 生成复杂医疗场景数据
    print("生成复杂医疗场景数据...")
    feedbacks = generator.generate_medical_scenario(scenario_type="complex")
    print(f"生成的反馈数量: {len(feedbacks)}")
    
    # 初始化反馈系统组件
    collector = FeedbackCollector()
    processor = FeedbackProcessor()
    fusion_engine = HybridFusionEngine()
    utilizer = FeedbackUtilizer()
    
    # 收集反馈
    print("\n收集反馈...")
    for feedback in feedbacks:
        collector.collect(feedback)
    
    # 处理反馈
    print("\n处理反馈...")
    processed_feedbacks = []
    for feedback in collector.get_all_feedbacks():
        processed_feedback = processor.process(feedback)
        processed_feedbacks.append(processed_feedback)
        print(f"处理反馈: {feedback.feedback_id}")
        print(f"  - 可靠性评分: {processed_feedback.get_reliability():.2f}")
    
    # 融合反馈
    print("\n融合反馈...")
    fused_result = fusion_engine.fuse(processed_feedbacks)
    print("融合结果:")
    pprint(fused_result)
    
    # 利用反馈
    print("\n利用反馈...")
    action_plan = utilizer.utilize(fused_result)
    print("生成的行动计划:")
    pprint(action_plan)

def main():
    """
    主函数
    """
    # 测试随机反馈生成
    test_generate_random_feedback()
    
    # 测试反馈集合生成
    test_generate_feedback_set()
    
    # 测试多样性反馈集合生成
    test_generate_diverse_feedback_set()
    
    # 测试医疗场景生成
    test_medical_scenarios()
    
    # 测试边界情况
    test_edge_cases()
    
    # 测试反馈集合功能
    test_feedback_collection()
    
    # 测试反馈系统完整流程
    test_feedback_system_pipeline()

if __name__ == "__main__":
    main()