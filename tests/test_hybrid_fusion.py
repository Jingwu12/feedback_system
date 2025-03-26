# -*- coding: utf-8 -*-
"""
混合融合引擎测试模块

该模块测试混合融合引擎的功能，包括策略选择、融合过程和结果分析。
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fusion.hybrid_fusion import HybridFusionEngine
from models.feedback_model import FeedbackModel
from models.metadata_model import MetadataModel, SourceType, FeedbackType
from models.content_model import TextContent, StructuredContent
from models.relation_model import RelationModel, RelationType


class TestHybridFusionEngine(unittest.TestCase):
    """
    测试混合融合引擎
    """
    
    def setUp(self):
        """
        测试前准备
        """
        self.engine = HybridFusionEngine()
        
        # 创建测试用的反馈数据
        self.create_test_feedbacks()
    
    def create_test_feedbacks(self):
        """
        创建测试用的反馈数据
        """
        # 创建医生反馈
        doctor_metadata = MetadataModel(
            source=SourceType.HUMAN_DOCTOR,
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now() - timedelta(hours=2),
            tags=["urgent", "follow_up"]
        )
        doctor_content = TextContent(
            text="患者表现为持续性头痛，伴有轻度恶心，建议进行核磁共振检查排除脑部病变。"
        )
        self.doctor_feedback = FeedbackModel(doctor_metadata, doctor_content)
        
        # 创建患者反馈
        patient_metadata = MetadataModel(
            source=SourceType.HUMAN_PATIENT,
            feedback_type=FeedbackType.TEXTUAL,
            timestamp=datetime.now() - timedelta(hours=1),
            tags=["symptom"]
        )
        patient_content = TextContent(
            text="我的头痛持续了三天，主要在太阳穴位置，吃了止痛药后有所缓解，但很快又疼了。"
        )
        self.patient_feedback = FeedbackModel(patient_metadata, patient_content)
        
        # 创建系统检查反馈
        system_metadata = MetadataModel(
            source=SourceType.SYSTEM_IMAGING,
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now(),
            tags=["mri_result"]
        )
        system_content = StructuredContent(
            data={
                "examination_type": "MRI",
                "region": "Brain",
                "findings": "未见明显异常",
                "conclusion": "正常脑部影像学表现"
            }
        )
        self.system_feedback = FeedbackModel(system_metadata, system_content)
        
        # 创建知识库反馈
        knowledge_metadata = MetadataModel(
            source=SourceType.KNOWLEDGE_LITERATURE,
            feedback_type=FeedbackType.THERAPEUTIC,
            timestamp=datetime.now() - timedelta(days=30),  # 较旧的反馈
            tags=["treatment", "migraine"]
        )
        knowledge_content = TextContent(
            text="对于偏头痛患者，建议尝试以下治疗方案：1. 常规止痛药物；2. 特异性偏头痛药物（如曲普坦类）；3. 预防性药物治疗；4. 生活方式调整，包括规律作息、避免诱因等。"
        )
        self.knowledge_feedback = FeedbackModel(knowledge_metadata, knowledge_content)
        
        # 创建反馈之间的关系
        relation1 = RelationModel(
            source_id=self.patient_feedback.feedback_id,
            target_id=self.doctor_feedback.feedback_id,
            relation_type=RelationType.COMPLEMENT,
            strength=0.8
        )
        self.patient_feedback.add_relation(relation1)
        
        relation2 = RelationModel(
            source_id=self.system_feedback.feedback_id,
            target_id=self.doctor_feedback.feedback_id,
            relation_type=RelationType.SUPPORT,
            strength=0.7
        )
        self.system_feedback.add_relation(relation2)
        
        # 创建测试用的反馈列表
        self.feedbacks_with_relations = [self.doctor_feedback, self.patient_feedback, self.system_feedback]
        self.feedbacks_without_relations = [self.doctor_feedback, self.knowledge_feedback]
        self.feedbacks_diverse_sources = [self.doctor_feedback, self.patient_feedback, self.system_feedback, self.knowledge_feedback]
        self.feedbacks_few = [self.doctor_feedback, self.patient_feedback]
    
    def test_select_strategy_with_relations(self):
        """
        测试存在关系时的策略选择
        """
        strategy = self.engine.select_strategy(self.feedbacks_with_relations)
        self.assertEqual(strategy, "graph", "存在关系时应选择图结构策略")
    
    def test_select_strategy_few_feedbacks(self):
        """
        测试反馈数量少时的策略选择
        """
        strategy = self.engine.select_strategy(self.feedbacks_few)
        self.assertEqual(strategy, "attention", "反馈数量少时应选择注意力机制策略")
    
    def test_select_strategy_diverse_sources(self):
        """
        测试来源多样性高时的策略选择
        """
        strategy = self.engine.select_strategy(self.feedbacks_diverse_sources)
        self.assertEqual(strategy, "graph", "来源多样性高时应选择图结构策略")
    
    def test_select_strategy_task_type(self):
        """
        测试不同任务类型的策略选择
        """
        strategy1 = self.engine.select_strategy(self.feedbacks_without_relations, task_type="long_term_optimization")
        self.assertEqual(strategy1, "rl", "长期优化任务应选择强化学习策略")
        
        strategy2 = self.engine.select_strategy(self.feedbacks_without_relations, task_type="diagnostic")
        self.assertEqual(strategy2, "graph", "诊断任务应选择图结构策略")
        
        strategy3 = self.engine.select_strategy(self.feedbacks_without_relations, task_type="question_answering")
        self.assertEqual(strategy3, "attention", "问答任务应选择注意力机制策略")
    
    def test_fuse_with_graph_strategy(self):
        """
        测试使用图结构策略进行融合
        """
        fused_feedback = self.engine.fuse(self.feedbacks_with_relations)
        self.assertIsNotNone(fused_feedback, "融合结果不应为空")
        self.assertIn("fusion_strategy:graph", fused_feedback.metadata.tags, "融合标签应包含策略信息")
    
    def test_fuse_with_attention_strategy(self):
        """
        测试使用注意力机制策略进行融合
        """
        fused_feedback = self.engine.fuse(self.feedbacks_few)
        self.assertIsNotNone(fused_feedback, "融合结果不应为空")
        self.assertIn("fusion_strategy:attention", fused_feedback.metadata.tags, "融合标签应包含策略信息")
    
    def test_fuse_with_rl_strategy(self):
        """
        测试使用强化学习策略进行融合
        """
        fused_feedback = self.engine.fuse(self.feedbacks_without_relations, task_type="long_term_optimization")
        self.assertIsNotNone(fused_feedback, "融合结果不应为空")
        self.assertIn("fusion_strategy:rl", fused_feedback.metadata.tags, "融合标签应包含策略信息")
    
    def test_strategy_history_recording(self):
        """
        测试策略选择历史记录
        """
        # 执行多次融合
        self.engine.fuse(self.feedbacks_with_relations)
        self.engine.fuse(self.feedbacks_few)
        self.engine.fuse(self.feedbacks_without_relations, task_type="long_term_optimization")
        
        # 检查历史记录
        self.assertEqual(len(self.engine.strategy_history), 3, "应记录3次策略选择历史")
        self.assertEqual(self.engine.strategy_history[0]["strategy"], "graph", "第一次应选择图结构策略")
        self.assertEqual(self.engine.strategy_history[1]["strategy"], "attention", "第二次应选择注意力机制策略")
        self.assertEqual(self.engine.strategy_history[2]["strategy"], "rl", "第三次应选择强化学习策略")
    
    def test_analyze_strategy_performance(self):
        """
        测试策略性能分析
        """
        # 执行多次融合
        self.engine.fuse(self.feedbacks_with_relations)
        self.engine.fuse(self.feedbacks_few)
        self.engine.fuse(self.feedbacks_without_relations, task_type="long_term_optimization")
        
        # 分析策略性能
        performance = self.engine.analyze_strategy_performance()
        self.assertIn("strategy_counts", performance, "性能分析应包含策略计数")
        self.assertIn("task_strategy_counts", performance, "性能分析应包含任务类型策略计数")
        self.assertEqual(performance["total_fusions"], 3, "总融合次数应为3")
    
    def test_get_strategy_recommendation(self):
        """
        测试策略推荐
        """
        # 执行多次融合以积累历史数据
        self.engine.fuse(self.feedbacks_with_relations, task_type="diagnostic")
        self.engine.fuse(self.feedbacks_few, task_type="diagnostic")
        self.engine.fuse(self.feedbacks_without_relations, task_type="long_term_optimization")
        
        # 测试推荐
        recommendation1 = self.engine.get_strategy_recommendation("diagnostic", 3, True)
        self.assertEqual(recommendation1, "graph", "存在关系时应推荐图结构策略")
        
        recommendation2 = self.engine.get_strategy_recommendation("diagnostic", 2, False)
        self.assertEqual(recommendation2, "attention", "反馈数量少且无关系时应推荐注意力机制策略")
        
        recommendation3 = self.engine.get_strategy_recommendation("long_term_optimization", 5, False)
        self.assertEqual(recommendation3, "rl", "长期优化任务应推荐强化学习策略")
    
    def test_evaluate_strategy_performance(self):
        """
        测试策略性能评估
        """
        # 执行融合
        fused_feedback = self.engine.fuse(self.feedbacks_with_relations)
        
        # 评估性能
        self.engine.evaluate_strategy_performance(fused_feedback, 0.85)
        
        # 检查历史记录是否更新了outcome
        self.assertEqual(self.engine.strategy_history[0]["outcome"], 0.85, "应更新策略性能评估结果")
    
    def test_get_medical_domain_recommendation(self):
        """
        测试医疗领域特定的策略推荐
        """
        recommendation1 = self.engine.get_medical_domain_recommendation([self.doctor_feedback, self.patient_feedback])
        self.assertEqual(recommendation1, "graph", "医生和患者反馈应推荐图结构策略")
        
        recommendation2 = self.engine.get_medical_domain_recommendation([self.doctor_feedback, self.knowledge_feedback])
        self.assertEqual(recommendation2, "graph", "医生和知识库反馈应推荐图结构策略")
        
        recommendation3 = self.engine.get_medical_domain_recommendation([self.doctor_feedback])
        self.assertEqual(recommendation3, "attention", "仅有医生反馈应推荐注意力机制策略")
    
    def test_analyze_feedback_patterns(self):
        """
        测试反馈模式分析
        """
        patterns = self.engine.analyze_feedback_patterns(self.feedbacks_diverse_sources)
        self.assertIn("source_distribution", patterns, "模式分析应包含来源分布")
        self.assertIn("type_distribution", patterns, "模式分析应包含类型分布")
        self.assertIn("relation_counts", patterns, "模式分析应包含关系计数")
        self.assertEqual(patterns["feedback_count"], 4, "反馈数量应为4")
    
    def test_empty_feedbacks(self):
        """
        测试空反馈列表的处理
        """
        with self.assertRaises(ValueError):
            self.engine.fuse([])
    
    def test_reliability_calculation(self):
        """
        测试可靠性计算
        """
        fused_feedback = self.engine.fuse(self.feedbacks_diverse_sources)
        self.assertIsNotNone(fused_feedback.metadata.reliability, "融合结果应有可靠性评分")
        self.assertTrue(0 <= fused_feedback.metadata.reliability <= 1, "可靠性评分应在0到1之间")


class TestHybridFusionEngineIntegration(unittest.TestCase):
    """
    混合融合引擎集成测试
    """
    
    def setUp(self):
        """
        测试前准备
        """
        self.engine = HybridFusionEngine()
        
        # 创建更复杂的测试场景
        self.create_complex_test_scenario()
    
    def create_complex_test_scenario(self):
        """
        创建复杂的测试场景，模拟真实医疗环境
        """
        # 创建多个医生的反馈
        doctor1_metadata = MetadataModel(
            source="human.doctor.cardiologist",
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now() - timedelta(days=1),
            tags=["heart", "ecg"]
        )
        doctor1_content = TextContent(
            text="患者心电图显示ST段抬高，考虑急性心肌梗死可能，建议立即进行冠状动脉造影检查。"
        )
        self.doctor1_feedback = FeedbackModel(doctor1_metadata, doctor1_content)
        
        doctor2_metadata = MetadataModel(
            source="human.doctor.emergency",
            feedback_type=FeedbackType.THERAPEUTIC,
            timestamp=datetime.now() - timedelta(hours=12),
            tags=["urgent", "treatment"]
        )
        doctor2_content = TextContent(
            text="患者胸痛症状明显，已给予阿司匹林300mg口服，硝酸甘油舌下含服，建议立即转入CCU进行进一步治疗。"
        )
        self.doctor2_feedback = FeedbackModel(doctor2_metadata, doctor2_content)
        
        # 创建患者反馈
        patient_metadata = MetadataModel(
            source=SourceType.HUMAN_PATIENT,
            feedback_type=FeedbackType.TEXTUAL,
            timestamp=datetime.now() - timedelta(hours=24),
            tags=["symptom", "pain"]
        )
        patient_content = TextContent(
            text="我突然感到胸口剧烈疼痛，像是被重物压住一样，伴有出汗和呼吸困难，疼痛持续了约30分钟。"
        )
        self.patient_feedback = FeedbackModel(patient_metadata, patient_content)
        
        # 创建多个检查结果反馈
        ecg_metadata = MetadataModel(
            source=SourceType.SYSTEM_EHR,
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now() - timedelta(hours=18),
            tags=["ecg", "test_result"]
        )
        ecg_content = StructuredContent(
            data={
                "examination_type": "ECG",
                "findings": "V1-V4导联ST段抬高>2mm",
                "interpretation": "符合急性前壁心肌梗死表现",
                "recommendation": "建议紧急冠脉介入治疗"
            }
        )
        self.ecg_feedback = FeedbackModel(ecg_metadata, ecg_content)
        
        lab_metadata = MetadataModel(
            source=SourceType.SYSTEM_LAB,
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now() - timedelta(hours=16),
            tags=["lab", "cardiac_markers"]
        )
        lab_content = StructuredContent(
            data={
                "examination_type": "Blood Test",
                "troponin_I": "2.5 ng/mL (参考值: <0.04)",
                "CK-MB": "35 U/L (参考值: <25)",
                "interpretation": "心肌损伤标志物明显升高"
            }
        )
        self.lab_feedback = FeedbackModel(lab_metadata, lab_content)
        
        # 创建知识库反馈
        guideline_metadata = MetadataModel(
            source=SourceType.KNOWLEDGE_LITERATURE,
            feedback_type=FeedbackType.THERAPEUTIC,
            timestamp=datetime.now() - timedelta(days=180),  # 半年前的指南
            tags=["guideline", "STEMI"]
        )
        guideline_content = TextContent(
            text="对于ST段抬高型心肌梗死(STEMI)患者，推荐在症状发作后90分钟内进行直接经皮冠状动脉介入治疗(PCI)。如无法及时进行PCI，应考虑溶栓治疗。同时给予抗血小板、抗凝、他汀类药物等基础治疗。"
        )
        self.guideline_feedback = FeedbackModel(guideline_metadata, guideline_content)
        
        # 创建反馈之间的关系
        # 患者症状支持医生诊断
        relation1 = RelationModel(
            source_id=self.patient_feedback.feedback_id,
            target_id=self.doctor1_feedback.feedback_id,
            relation_type=RelationType.SUPPORT,
            strength=0.7
        )
        self.patient_feedback.add_relation(relation1)
        
        # 心电图结果强烈支持医生诊断
        relation2 = RelationModel(
            source_id=self.ecg_feedback.feedback_id,
            target_id=self.doctor1_feedback.feedback_id,
            relation_type=RelationType.SUPPORT,
            strength=0.9
        )
        self.ecg_feedback.add_relation(relation2)
        
        # 实验室结果支持医生诊断
        relation3 = RelationModel(
            source_id=self.lab_feedback.feedback_id,
            target_id=self.doctor1_feedback.feedback_id,
            relation_type=RelationType.SUPPORT,
            strength=0.85
        )
        self.lab_feedback.add_relation(relation3)
        
        # 指南补充医生治疗建议
        relation4 = RelationModel(
            source_id=self.guideline_feedback.feedback_id,
            target_id=self.doctor2_feedback.feedback_id,
            relation_type=RelationType.COMPLEMENT,
            strength=0.8
        )
        self.guideline_feedback.add_relation(relation4)
        
        # 创建测试用的反馈列表
        self.all_feedbacks = [
            self.doctor1_feedback, self.doctor2_feedback, self.patient_feedback,
            self.ecg_feedback, self.lab_feedback, self.guideline_feedback
        ]
        self.diagnostic_feedbacks = [
            self.doctor1_feedback, self.patient_feedback, self.ecg_feedback, self.lab_feedback
        ]
        self.therapeutic_feedbacks = [
            self.doctor2_feedback, self.guideline_feedback
        ]
    
    def test_complex_scenario_fusion(self):
        """
        测试复杂场景下的融合
        """
        fused_feedback = self.engine.fuse(self.all_feedbacks, task_type="diagnostic")
        self.assertIsNotNone(fused_feedback, "融合结果不应为空")
        self.assertIn("fusion_strategy:graph", fused_feedback.metadata.tags, "复杂场景应选择图结构策略")
    
    def test_diagnostic_therapeutic_separation(self):
        """
        测试诊断和治疗反馈的分离融合
        """
        # 诊断反馈融合
        diagnostic_fused = self.engine.fuse(self.diagnostic_feedbacks, task_type="diagnostic")
        self.assertIsNotNone(diagnostic_fused, "诊断融合结果不应为空")
        
        # 治疗反馈融合
        therapeutic_fused = self.engine.fuse(self.therapeutic_feedbacks, task_type="therapeutic")
        self.assertIsNotNone(therapeutic_fused, "治疗融合结果不应为空")
        
        # 检查融合结果是否包含关键信息
        if hasattr(diagnostic_fused.content, 'text'):
            self.assertIn("心肌梗死", diagnostic_fused.content.text, "诊断融合结果应包含关键诊断信息")
        
        if hasattr(therapeutic_fused.content, 'text'):
            self.assertIn("PCI", therapeutic_fused.content.text, "治疗融合结果应包含关键治疗信息")
    
    def test_time_weighted_fusion(self):
        """
        测试时间加权融合
        """
        # 创建新的反馈，时间更新
        new_doctor_metadata = MetadataModel(
            source="human.doctor.cardiologist",
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now(),  # 最新反馈
            tags=["update", "follow_up"]
        )
        new_doctor_content = TextContent(
            text="冠脉造影显示LAD近端90%狭窄，已成功植入支架，患者症状明显缓解。诊断确认为急性前壁心肌梗死。"
        )
        new_doctor_feedback = FeedbackModel(new_doctor_metadata, new_doctor_content)
        
        # 添加到反馈列表
        updated_feedbacks = self.diagnostic_feedbacks + [new_doctor_feedback]
        
        # 融合
        fused_feedback = self.engine.fuse(updated_feedbacks, task_type="diagnostic")
        
        # 检查融合结果是否优先考虑了最新反馈
        if hasattr(fused_feedback.content, 'text'):
            self.assertIn("支架", fused_feedback.content.text, "融合结果应包含最新反馈的关键信息")
    
    def test_conflicting_feedback_resolution(self):
        """
        测试冲突反馈的解决
        """
        # 创建冲突的反馈
        conflicting_metadata = MetadataModel(
            source="human.doctor.pulmonologist",
            feedback_type=FeedbackType.DIAGNOSTIC,
            timestamp=datetime.now() - timedelta(hours=20),
            tags=["differential", "alternative"]
        )
        conflicting_content = TextContent(
            text="患者症状可能是由急性肺栓塞引起，建议进行肺动脉CTA检查，同时给予抗凝治疗。"
        )
        conflicting_feedback = FeedbackModel(conflicting_metadata, conflicting_content)
        
        # 添加反对关系
        relation = RelationModel(
            source_id=conflicting_feedback.feedback_id,
            target_id=self.doctor1_feedback.feedback_id,
            relation_type=RelationType.OPPOSE,
            strength=0.6
        )
        conflicting_feedback.add_relation(relation)
        
        # 添加到反馈列表
        conflicting_feedbacks = self.diagnostic_feedbacks + [conflicting_feedback]
        
        # 融合
        fused_feedback = self.engine.fuse(conflicting_feedbacks, task_type="diagnostic")
        
        # 由于大多数证据支持心肌梗死诊断，融合结果应该偏向这个诊断
        if hasattr(fused_feedback.content, 'text'):
            self.assertIn("心肌梗死", fused_feedback.content.text, "融合结果应偏向主要支持的诊断")
    
    def test_feedback_pattern_analysis_in_complex_scenario(self):
        """
        测试复杂场景中的反馈模式分析
        """
        patterns = self.engine.analyze_feedback_patterns(self.all_feedbacks)
        
        # 检查分析结果
        self.assertEqual(patterns["feedback_count"], 6, "应有6条反馈")
        self.assertGreaterEqual(len(patterns["source_distribution"]), 4, "应至少有4种不同来源")
        self.assertGreaterEqual(patterns["relation_counts"]["support"], 3, "应至少有3个支持关系")


if __name__ == "__main__":
    unittest.main()