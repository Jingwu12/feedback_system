# -*- coding: utf-8 -*-
"""
反馈闭环系统示例

该示例展示了如何使用反馈闭环系统的各个组件进行反馈收集、处理、融合和利用。
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.metadata_model import MetadataModel, SourceType, FeedbackType
from models.content_model import TextContent, StructuredContent
from models.feedback_model import FeedbackModel, FeedbackCollection
from models.relation_model import RelationModel, RelationType

from core.collector.collector import HumanFeedbackCollector, ToolFeedbackCollector, KnowledgeFeedbackCollector, SelfFeedbackCollector
from core.processor.processor import TextNormalizationProcessor, ProcessingPipeline
from core.fusion.fusion import GraphBasedFusion, AttentionBasedFusion, HybridFusionEngine
from core.utilizer.utilizer import PlanningAdjuster, ExecutionOptimizer

def main():
    print("=== 反馈闭环系统示例 ===")
    
    # 1. 收集反馈
    print("\n1. 收集反馈")
    feedbacks = collect_feedback()
    print(f"收集到 {len(feedbacks)} 条反馈")
    
    # 2. 处理反馈
    print("\n2. 处理反馈")
    processed_feedbacks = process_feedback(feedbacks)
    print(f"处理完成 {len(processed_feedbacks)} 条反馈")
    
    # 3. 融合反馈
    print("\n3. 融合反馈")
    fused_feedback = fuse_feedback(processed_feedbacks)
    print(f"融合后的反馈ID: {fused_feedback.feedback_id}")
    print(f"融合后的反馈可靠性: {fused_feedback.get_reliability():.2f}")
    
    # 4. 利用反馈
    print("\n4. 利用反馈")
    utilize_feedback(fused_feedback)
    
    print("\n=== 示例完成 ===")

def collect_feedback():
    """收集反馈"""
    feedbacks = []
    
    # 收集医生反馈
    doctor_collector = HumanFeedbackCollector(SourceType.HUMAN_DOCTOR)
    doctor_feedback = doctor_collector.collect(
        text="患者血压持续偏高，建议调整降压药物剂量，并增加血压监测频率。",
        feedback_type=FeedbackType.THERAPEUTIC,
        tags=["hypertension", "medication_adjustment"]
    )
    feedbacks.extend(doctor_feedback)
    print("收集到医生反馈")
    
    # 收集患者反馈
    patient_collector = HumanFeedbackCollector(SourceType.HUMAN_PATIENT)
    patient_feedback = patient_collector.collect(
        text="服用新药后感到头晕，尤其是早晨起床时。",
        feedback_type=FeedbackType.THERAPEUTIC,
        tags=["side_effect", "dizziness"]
    )
    feedbacks.extend(patient_feedback)
    print("收集到患者反馈")
    
    # 收集工具反馈
    tool_collector = ToolFeedbackCollector("blood_pressure_monitor", SourceType.SYSTEM_LAB)
    tool_feedback = tool_collector.collect(
        data={
            "systolic": 158,
            "diastolic": 95,
            "heart_rate": 76,
            "timestamp": datetime.now().isoformat(),
            "status": "abnormal"
        },
        feedback_type=FeedbackType.DIAGNOSTIC,
        tags=["vital_signs", "hypertension"]
    )
    feedbacks.extend(tool_feedback)
    print("收集到工具反馈")
    
    # 收集知识反馈
    knowledge_collector = KnowledgeFeedbackCollector("medical_knowledge_graph", SourceType.KNOWLEDGE_GRAPH)
    knowledge_feedback = knowledge_collector.collect(
        query="高血压药物副作用",
        results=[
            {
                "content": "钙通道阻滞剂可能导致头晕、头痛和踝部水肿。",
                "confidence": 0.85
            },
            {
                "content": "血管紧张素转换酶抑制剂可能导致干咳和血管性水肿。",
                "confidence": 0.9
            }
        ],
        feedback_type=FeedbackType.THERAPEUTIC
    )
    feedbacks.extend(knowledge_feedback)
    print("收集到知识反馈")
    
    # 收集自我反馈
    self_collector = SelfFeedbackCollector()
    self_feedback = self_collector.collect(
        assessment_type="consistency_check",
        assessment_result={
            "inconsistency_detected": True,
            "description": "患者报告的副作用与当前药物已知副作用一致，但与治疗方案不一致。"
        },
        confidence=0.75,
        feedback_type=FeedbackType.STRUCTURED
    )
    feedbacks.extend(self_feedback)
    print("收集到自我反馈")
    
    return feedbacks

def process_feedback(feedbacks):
    """处理反馈"""
    # 创建处理流水线
    pipeline = ProcessingPipeline([
        TextNormalizationProcessor()
        # 可以添加更多处理器
    ])
    
    # 处理反馈
    processed_feedbacks = pipeline.process_batch(feedbacks)
    
    # 添加反馈之间的关系
    # 假设第一条反馈（医生反馈）和第二条反馈（患者反馈）之间存在补充关系
    if len(processed_feedbacks) >= 2:
        relation = RelationModel(
            source_id=processed_feedbacks[1].feedback_id,  # 患者反馈
            target_id=processed_feedbacks[0].feedback_id,  # 医生反馈
            relation_type=RelationType.COMPLEMENT,
            strength=0.8,
            metadata={"aspect": "medication_effect"}
        )
        processed_feedbacks[1].add_relation(relation)
        print("添加了反馈之间的补充关系")
    
    # 假设第三条反馈（工具反馈）和第一条反馈（医生反馈）之间存在支持关系
    if len(processed_feedbacks) >= 3:
        relation = RelationModel(
            source_id=processed_feedbacks[2].feedback_id,  # 工具反馈
            target_id=processed_feedbacks[0].feedback_id,  # 医生反馈
            relation_type=RelationType.SUPPORT,
            strength=0.9
        )
        processed_feedbacks[2].add_relation(relation)
        print("添加了反馈之间的支持关系")
    
    return processed_feedbacks

def fuse_feedback(feedbacks):
    """融合反馈"""
    # 创建混合融合引擎
    fusion_engine = HybridFusionEngine()
    
    # 融合反馈
    fused_feedback = fusion_engine.fuse(feedbacks, task_type="therapeutic_adjustment")
    
    # 输出融合策略
    strategy = next((tag.split(":")[1] for tag in fused_feedback.metadata.tags 
                    if tag.startswith("fusion_strategy:")), "unknown")
    print(f"使用的融合策略: {strategy}")
    
    # 输出融合后的内容
    if hasattr(fused_feedback.content, 'text'):
        print(f"融合后的内容: {fused_feedback.content.text}")
    elif hasattr(fused_feedback.content, 'data'):
        print(f"融合后的内容: {json.dumps(fused_feedback.content.data, indent=2)}")
    
    return fused_feedback

def utilize_feedback(feedback):
    """利用反馈"""
    # 使用规划调整器
    planning_adjuster = PlanningAdjuster()
    planning_result = planning_adjuster.utilize(feedback)
    
    print("规划调整结果:")
    print(f"- 检测到 {len(planning_result['planning_errors'])} 个规划错误")
    print(f"- 任务优先级调整: {planning_result['priority_adjusted']}")
    print(f"- 资源重新分配: {planning_result['resources_reallocated']}")
    
    # 使用执行优化器
    execution_optimizer = ExecutionOptimizer()
    execution_result = execution_optimizer.utilize(feedback)
    
    print("执行优化结果:")
    print(f"- 工具选择优化: {execution_result['tool_selection_optimized']}")
    print(f"- 参数优化: {execution_result['parameters_optimized']}")
    print(f"- 模式学习: {execution_result['patterns_learned']}")
    
    if execution_result['tool_selection_optimized'] and 'selected_tool' in execution_result:
        print(f"- 选择的工具: {execution_result['selected_tool']['name']}")

if __name__ == "__main__":
    main()