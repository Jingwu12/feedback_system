# -*- coding: utf-8 -*-
"""
TestDataGenerator单元测试

该模块用于测试TestDataGenerator类的功能，确保其能正确生成各种类型的反馈数据。
"""

import unittest
import sys
import os
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_data_generator import TestDataGenerator
from models.metadata_model import SourceType, FeedbackType
from models.relation_model import RelationType
from models.content_model import TextContent, StructuredContent

class TestDataGeneratorTest(unittest.TestCase):
    """
    TestDataGenerator单元测试类
    """
    
    def setUp(self):
        """
        测试前准备
        """
        self.generator = TestDataGenerator()
    
    def test_generate_random_feedback(self):
        """
        测试随机反馈生成
        """
        # 测试默认参数
        feedback = self.generator.generate_random_feedback()
        self.assertIsNotNone(feedback)
        self.assertIsNotNone(feedback.feedback_id)
        self.assertIsNotNone(feedback.metadata)
        self.assertIsNotNone(feedback.content)
        
        # 测试指定参数
        source_type = SourceType.HUMAN_DOCTOR
        feedback_type = FeedbackType.DIAGNOSTIC
        timestamp = datetime.now()
        
        feedback = self.generator.generate_random_feedback(
            source_type=source_type,
            feedback_type=feedback_type,
            timestamp=timestamp
        )
        
        self.assertEqual(feedback.metadata.source, source_type)
        self.assertEqual(feedback.metadata.feedback_type, feedback_type)
        self.assertEqual(feedback.metadata.timestamp, timestamp)
    
    def test_generate_text_content(self):
        """
        测试文本内容生成
        """
        # 测试医生诊断反馈
        content = self.generator._generate_text_content(
            source_type=SourceType.HUMAN_DOCTOR,
            feedback_type=FeedbackType.DIAGNOSTIC
        )
        
        self.assertIsInstance(content, TextContent)
        self.assertTrue(len(content.text) > 0)
        
        # 测试患者反馈
        content = self.generator._generate_text_content(
            source_type=SourceType.HUMAN_PATIENT,
            feedback_type=FeedbackType.TEXTUAL
        )
        
        self.assertIsInstance(content, TextContent)
        self.assertTrue(len(content.text) > 0)
        self.assertTrue("感到" in content.text)
    
    def test_generate_structured_content(self):
        """
        测试结构化内容生成
        """
        # 测试影像系统反馈
        content = self.generator._generate_structured_content(
            source_type=SourceType.SYSTEM_IMAGING,
            feedback_type=FeedbackType.DIAGNOSTIC
        )
        
        self.assertIsInstance(content, StructuredContent)
        self.assertIn("examination_type", content.data)
        self.assertIn("region", content.data)
        self.assertIn("findings", content.data)
        
        # 测试实验室系统反馈
        content = self.generator._generate_structured_content(
            source_type=SourceType.SYSTEM_LAB,
            feedback_type=FeedbackType.DIAGNOSTIC
        )
        
        self.assertIsInstance(content, StructuredContent)
        self.assertIn("test_type", content.data)
        self.assertIn("test_items", content.data)
    
    def test_generate_feedback_set(self):
        """
        测试反馈集合生成
        """
        # 测试无关系的反馈集合
        count = 5
        feedbacks = self.generator.generate_feedback_set(count=count, with_relations=False)
        
        self.assertEqual(len(feedbacks), count)
        for feedback in feedbacks:
            self.assertEqual(len(feedback.relations), 0)
        
        # 测试有关系的反馈集合
        feedbacks = self.generator.generate_feedback_set(count=count, with_relations=True)
        
        self.assertEqual(len(feedbacks), count)
        
        # 检查是否至少有一个反馈包含关系
        has_relations = False
        for feedback in feedbacks:
            if len(feedback.relations) > 0:
                has_relations = True
                break
        
        self.assertTrue(has_relations)
    
    def test_generate_feedback_by_type(self):
        """
        测试特定类型反馈生成
        """
        # 测试诊断类型反馈
        diagnostic_feedbacks = self.generator.generate_feedback_by_type(
            feedback_type=FeedbackType.DIAGNOSTIC,
            count=4,
            with_relations=True
        )
        
        self.assertEqual(len(diagnostic_feedbacks), 4)
        for feedback in diagnostic_feedbacks:
            self.assertEqual(feedback.metadata.feedback_type, FeedbackType.DIAGNOSTIC)
        
        # 检查是否生成了关系
        has_relations = False
        for feedback in diagnostic_feedbacks:
            if len(feedback.relations) > 0:
                has_relations = True
                break
        
        self.assertTrue(has_relations)
        
        # 测试治疗类型反馈
        therapeutic_feedbacks = self.generator.generate_feedback_by_type(
            feedback_type=FeedbackType.THERAPEUTIC,
            count=3,
            with_relations=False
        )
        
        self.assertEqual(len(therapeutic_feedbacks), 3)
        for feedback in therapeutic_feedbacks:
            self.assertEqual(feedback.metadata.feedback_type, FeedbackType.THERAPEUTIC)
            self.assertEqual(len(feedback.relations), 0)  # 不应该有关系
    
    def test_complex_medical_scenario(self):
        """
        测试复杂医疗场景生成
        """
        # 测试复杂病例场景
        complex_feedbacks = self.generator.generate_medical_scenario(scenario_type="complex")
        self.assertTrue(len(complex_feedbacks) > 0)
        
        # 检查是否包含复杂病例相关标签
        has_complex_tag = False
        for feedback in complex_feedbacks:
            if "autoimmune" in feedback.metadata.tags or "SLE" in feedback.metadata.tags:
                has_complex_tag = True
                break
        
        self.assertTrue(has_complex_tag)
        
        # 检查是否包含多种来源的反馈
        source_types = set()
        for feedback in complex_feedbacks:
            source_types.add(str(feedback.metadata.source))
        
        # 复杂场景应该包含至少3种不同来源的反馈
        self.assertTrue(len(source_types) >= 3)
        
        # 测试急诊场景
        emergency_feedbacks = self.generator.generate_medical_scenario(scenario_type="emergency")
        self.assertTrue(len(emergency_feedbacks) > 0)
        
        # 检查是否包含急诊相关标签
        has_emergency_tag = False
        for feedback in emergency_feedbacks:
            if "emergency" in feedback.metadata.tags or "urgent" in feedback.metadata.tags:
                has_emergency_tag = True
                break
        
        self.assertTrue(has_emergency_tag)
        
        # 测试慢性病场景
        chronic_feedbacks = self.generator.generate_medical_scenario(scenario_type="chronic")
        self.assertTrue(len(chronic_feedbacks) > 0)
        
        # 检查是否包含慢性病相关标签
        has_chronic_tag = False
        for feedback in chronic_feedbacks:
            if "diabetes" in feedback.metadata.tags or "follow_up" in feedback.metadata.tags:
                has_chronic_tag = True
                break
        
        self.assertTrue(has_chronic_tag)

    def test_generate_diverse_feedback_set(self):
        """
        测试多样性反馈集合生成
        """
        count = 8
        time_span = 15
        feedbacks = self.generator.generate_diverse_feedback_set(count=count, time_span_days=time_span)
        
        self.assertEqual(len(feedbacks), count)
        
        # 检查是否包含不同的来源类型
        source_types = set()
        for feedback in feedbacks:
            source_types.add(str(feedback.metadata.source))
        
        # 应该至少包含3种不同的来源类型
        self.assertTrue(len(source_types) >= 3)
        
        # 检查是否包含不同的反馈类型
        feedback_types = set()
        for feedback in feedbacks:
            feedback_types.add(str(feedback.metadata.feedback_type))
        
        # 应该至少包含2种不同的反馈类型
        self.assertTrue(len(feedback_types) >= 2)
        
        # 检查时间戳是否分布在指定的时间跨度内
        timestamps = [feedback.metadata.timestamp for feedback in feedbacks]
        timestamps.sort()
        time_diff = timestamps[-1] - timestamps[0]
        
        # 时间差应该在指定的时间跨度内（允许有小误差）
        self.assertTrue(time_diff.days <= time_span + 1)

    def test_generate_edge_case_feedback(self):
        """
        测试边界情况反馈生成
        """
        # 测试空内容反馈
        empty_feedback = self.generator.generate_edge_case_feedback(case_type="empty")
        self.assertEqual(empty_feedback.content.text, "")
        
        # 测试极长内容反馈
        long_feedback = self.generator.generate_edge_case_feedback(case_type="long")
        self.assertTrue(len(long_feedback.content.text) > 500)
        
        # 测试特殊字符内容反馈
        special_chars_feedback = self.generator.generate_edge_case_feedback(case_type="special_chars")
        self.assertTrue(any(c in special_chars_feedback.content.text for c in "!@#$%^&*()_+{}"))
        
        # 测试未来时间戳反馈
        future_feedback = self.generator.generate_edge_case_feedback(case_type="future")
        self.assertTrue(future_feedback.metadata.timestamp > datetime.now())
        
        # 测试非常旧的时间戳反馈
        old_feedback = self.generator.generate_edge_case_feedback(case_type="old")
        self.assertTrue((datetime.now() - old_feedback.metadata.timestamp).days > 3000)

if __name__ == "__main__":
    unittest.main()