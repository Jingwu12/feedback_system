# -*- coding: utf-8 -*-
"""
混合融合引擎

该模块实现了混合融合引擎，能够根据任务特性和反馈特性自动选择最适合的融合策略。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent
from ...models.relation_model import RelationModel, RelationType

from .graph_fusion import GraphBasedFusion
from .attention_fusion import AttentionBasedFusion
from .rl_fusion import RLBasedFusion

class HybridFusionEngine:
    """
    混合融合引擎
    
    根据任务特性和反馈特性自动选择最适合的融合策略。
    """
    
    def __init__(self):
        """
        初始化混合融合引擎
        """
        self.fusion_strategies = {
            "graph": GraphBasedFusion(),
            "attention": AttentionBasedFusion(),
            "rl": RLBasedFusion()
        }
        
        # 策略选择历史记录，用于学习最佳策略
        self.strategy_history = []
    
    def select_strategy(self, feedbacks: List[FeedbackModel], task_type: str = None) -> str:
        """
        选择最适合的融合策略
        
        Args:
            feedbacks: 反馈列表
            task_type: 任务类型
            
        Returns:
            str: 选择的策略名称
        """
        # 检查反馈数量
        if len(feedbacks) <= 2:
            return "attention"  # 反馈较少时使用注意力机制
        
        # 检查反馈关系
        has_relations = any(len(f.relations) > 0 for f in feedbacks)
        if has_relations:
            return "graph"  # 存在明确关系时使用图结构
        
        # 检查反馈来源多样性
        sources = set()
        for feedback in feedbacks:
            source = feedback.metadata.source
            source_value = source.value if hasattr(source, 'value') else str(source)
            sources.add(source_value)
        
        # 来源多样性高时使用图结构
        if len(sources) >= 3:
            return "graph"
        
        # 检查任务类型
        if task_type == "long_term_optimization" or task_type == "sequential_decision":
            return "rl"  # 长期优化任务使用强化学习
        elif task_type == "diagnostic" or task_type == "therapeutic":
            # 医疗相关任务使用图结构，因为关系很重要
            return "graph"
        elif task_type == "information_retrieval" or task_type == "question_answering":
            # 信息检索任务使用注意力机制
            return "attention"
        
        # 检查反馈类型
        types = set()
        for feedback in feedbacks:
            feedback_type = feedback.metadata.feedback_type
            type_value = feedback_type.value if hasattr(feedback_type, 'value') else str(feedback_type)
            types.add(type_value)
        
        # 反馈类型多样性高时使用图结构
        if len(types) >= 3:
            return "graph"
        
        # 默认使用注意力机制
        return "attention"
    
    def fuse(self, feedbacks: List[FeedbackModel], task_type: str = None) -> FeedbackModel:
        """
        融合反馈
        
        Args:
            feedbacks: 待融合的反馈列表
            task_type: 任务类型
            
        Returns:
            FeedbackModel: 融合后的反馈
        """
        if not feedbacks:
            raise ValueError("No feedbacks to fuse")
        
        # 选择融合策略
        strategy_name = self.select_strategy(feedbacks, task_type)
        strategy = self.fusion_strategies[strategy_name]
        
        # 记录策略选择
        self.strategy_history.append({
            "timestamp": datetime.now(),
            "strategy": strategy_name,
            "task_type": task_type,
            "num_feedbacks": len(feedbacks),
            "feedback_types": [f.metadata.feedback_type.value if hasattr(f.metadata.feedback_type, 'value') 
                              else str(f.metadata.feedback_type) for f in feedbacks],
            "feedback_sources": [f.metadata.source.value if hasattr(f.metadata.source, 'value') 
                               else str(f.metadata.source) for f in feedbacks]
        })
        
        # 执行融合
        fused_feedback = strategy.fuse(feedbacks)
        
        # 添加融合策略信息
        if fused_feedback.metadata.tags is None:
            fused_feedback.metadata.tags = []
        fused_feedback.metadata.tags.append(f"fusion_strategy:{strategy_name}")
        
        return fused_feedback
    
    def analyze_strategy_performance(self) -> Dict[str, Any]:
        """
        分析不同策略的性能
        
        Returns:
            Dict[str, Any]: 策略性能分析结果
        """
        if not self.strategy_history:
            return {"message": "No strategy history available"}
        
        # 统计各策略使用次数
        strategy_counts = {}
        for record in self.strategy_history:
            strategy = record["strategy"]
            if strategy not in strategy_counts:
                strategy_counts[strategy] = 0
            strategy_counts[strategy] += 1
        
        # 统计各策略在不同任务类型上的使用次数
        task_strategy_counts = {}
        for record in self.strategy_history:
            task_type = record["task_type"] or "unknown"
            strategy = record["strategy"]
            
            if task_type not in task_strategy_counts:
                task_strategy_counts[task_type] = {}
            
            if strategy not in task_strategy_counts[task_type]:
                task_strategy_counts[task_type][strategy] = 0
            
            task_strategy_counts[task_type][strategy] += 1
        
        return {
            "strategy_counts": strategy_counts,
            "task_strategy_counts": task_strategy_counts,
            "total_fusions": len(self.strategy_history)
        }
    
    def get_strategy_recommendation(self, task_type: str, num_feedbacks: int, 
                                  has_relations: bool = False) -> str:
        """
        获取策略推荐
        
        Args:
            task_type: 任务类型
            num_feedbacks: 反馈数量
            has_relations: 是否存在明确关系
            
        Returns:
            str: 推荐的策略名称
        """
        # 根据历史记录和规则推荐策略
        if has_relations:
            return "graph"  # 存在明确关系时使用图结构
        
        if num_feedbacks <= 2:
            return "attention"  # 反馈较少时使用注意力机制
        
        # 查找历史记录中相似任务的策略选择
        similar_records = [record for record in self.strategy_history 
                          if record["task_type"] == task_type and 
                          abs(record["num_feedbacks"] - num_feedbacks) <= 2]
        
        if similar_records:
            # 统计各策略在相似任务上的使用次数
            strategy_counts = {}
            for record in similar_records:
                strategy = record["strategy"]
                if strategy not in strategy_counts:
                    strategy_counts[strategy] = 0
                strategy_counts[strategy] += 1
            
            # 返回使用最多的策略
            return max(strategy_counts, key=strategy_counts.get)
        
        # 默认策略
        if task_type == "long_term_optimization" or task_type == "sequential_decision":
            return "rl"
        elif task_type == "diagnostic" or task_type == "therapeutic":
            return "graph"
        else:
            return "attention"

    def evaluate_strategy_performance(self, feedback: FeedbackModel, actual_outcome: float) -> None:
        """
        评估策略性能
        
        Args:
            feedback: 融合后的反馈
            actual_outcome: 实际结果评分（0-1之间的值，越高表示效果越好）
        """
        # 从反馈标签中提取融合策略
        strategy = None
        for tag in feedback.metadata.tags:
            if tag.startswith("fusion_strategy:"):
                strategy = tag.split(":")[1]
                break
        
        if not strategy or not self.strategy_history:
            return
        
        # 更新最近一次使用该策略的记录
        for i in range(len(self.strategy_history) - 1, -1, -1):
            if self.strategy_history[i]["strategy"] == strategy:
                self.strategy_history[i]["outcome"] = actual_outcome
                break
    
    def get_medical_domain_recommendation(self, feedbacks: List[FeedbackModel]) -> str:
        """
        获取医疗领域特定的策略推荐
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            str: 推荐的策略名称
        """
        # 检查是否存在医生反馈
        has_doctor_feedback = False
        has_patient_feedback = False
        has_knowledge_feedback = False
        
        for feedback in feedbacks:
            if hasattr(feedback.metadata.source, 'value'):
                source_value = feedback.metadata.source.value
                if 'doctor' in source_value:
                    has_doctor_feedback = True
                elif 'patient' in source_value:
                    has_patient_feedback = True
                elif 'knowledge' in source_value:
                    has_knowledge_feedback = True
        
        # 如果同时存在医生和患者反馈，使用图结构
        if has_doctor_feedback and has_patient_feedback:
            return "graph"
        
        # 如果存在知识库反馈和医生反馈，使用图结构
        if has_knowledge_feedback and has_doctor_feedback:
            return "graph"
        
        # 如果只有医生反馈，使用注意力机制
        if has_doctor_feedback and not has_patient_feedback and not has_knowledge_feedback:
            return "attention"
        
        # 如果只有患者反馈，使用注意力机制
        if has_patient_feedback and not has_doctor_feedback and not has_knowledge_feedback:
            return "attention"
        
        # 默认返回None，表示没有特定推荐
        return None
    
    def analyze_feedback_patterns(self, feedbacks: List[FeedbackModel]) -> Dict[str, Any]:
        """
        分析反馈模式
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            Dict[str, Any]: 反馈模式分析结果
        """
        if not feedbacks:
            return {"message": "No feedbacks to analyze"}
        
        # 分析反馈来源分布
        source_distribution = {}
        for feedback in feedbacks:
            source = feedback.metadata.source
            source_value = source.value if hasattr(source, 'value') else str(source)
            if source_value not in source_distribution:
                source_distribution[source_value] = 0
            source_distribution[source_value] += 1
        
        # 分析反馈类型分布
        type_distribution = {}
        for feedback in feedbacks:
            feedback_type = feedback.metadata.feedback_type
            type_value = feedback_type.value if hasattr(feedback_type, 'value') else str(feedback_type)
            if type_value not in type_distribution:
                type_distribution[type_value] = 0
            type_distribution[type_value] += 1
        
        # 分析反馈关系
        relation_counts = {
            "support": 0,
            "oppose": 0,
            "complement": 0,
            "other": 0
        }
        
        for feedback in feedbacks:
            for relation in feedback.relations:
                if relation.relation_type == RelationType.SUPPORT:
                    relation_counts["support"] += 1
                elif relation.relation_type == RelationType.OPPOSE:
                    relation_counts["oppose"] += 1
                elif relation.relation_type == RelationType.COMPLEMENT:
                    relation_counts["complement"] += 1
                else:
                    relation_counts["other"] += 1
        
        # 分析反馈时间分布
        timestamps = [feedback.metadata.timestamp for feedback in feedbacks]
        time_range = max(timestamps) - min(timestamps) if timestamps else datetime.timedelta(0)
        
        return {
            "source_distribution": source_distribution,
            "type_distribution": type_distribution,
            "relation_counts": relation_counts,
            "feedback_count": len(feedbacks),
            "time_range_seconds": time_range.total_seconds(),
            "average_reliability": sum(f.get_reliability() for f in feedbacks) / len(feedbacks) if feedbacks else 0
        }