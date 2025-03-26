# -*- coding: utf-8 -*-
"""
反馈融合器

该模块负责将处理后的多源反馈进行融合，生成综合性的反馈信息。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime

from ...models.feedback_model import FeedbackModel, FeedbackCollection
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent
from ...models.relation_model import RelationModel, RelationType, RelationGraph

class FeedbackFusion(ABC):
    """
    反馈融合基类
    
    定义反馈融合的通用接口，所有具体融合器都应继承此类。
    """
    
    @abstractmethod
    def fuse(self, feedbacks: List[FeedbackModel]) -> FeedbackModel:
        """
        融合反馈
        
        Args:
            feedbacks: 待融合的反馈列表
            
        Returns:
            FeedbackModel: 融合后的反馈
        """
        pass

class GraphBasedFusion(FeedbackFusion):
    """
    基于图结构的反馈融合
    
    将反馈表示为图中的节点，通过图算法进行信息传递和融合。
    """
    
    def __init__(self, relation_threshold: float = 0.5, max_iterations: int = 3):
        """
        初始化基于图结构的融合器
        
        Args:
            relation_threshold: 关系强度阈值，只有强度超过阈值的关系才会被考虑
            max_iterations: 最大迭代次数，控制信息传播的轮数
        """
        self.relation_threshold = relation_threshold
        self.max_iterations = max_iterations
        self.relation_graph = RelationGraph()
    
    def build_relation_graph(self, feedbacks: List[FeedbackModel]) -> None:
        """
        构建反馈关系图
        
        Args:
            feedbacks: 反馈列表
        """
        # 清空现有关系图
        self.relation_graph = RelationGraph()
        
        # 添加现有关系
        for feedback in feedbacks:
            for relation in feedback.relations:
                self.relation_graph.add_relation(relation)
        
        # 检测并添加新关系
        for i, feedback1 in enumerate(feedbacks):
            for j, feedback2 in enumerate(feedbacks[i+1:], i+1):
                # 检测支持关系
                support_strength = self._detect_support_relation(feedback1, feedback2)
                if support_strength > self.relation_threshold:
                    relation = RelationModel(
                        source_id=feedback1.feedback_id,
                        target_id=feedback2.feedback_id,
                        relation_type=RelationType.SUPPORT,
                        strength=support_strength
                    )
                    self.relation_graph.add_relation(relation)
                
                # 检测反对关系
                oppose_strength = self._detect_oppose_relation(feedback1, feedback2)
                if oppose_strength > self.relation_threshold:
                    relation = RelationModel(
                        source_id=feedback1.feedback_id,
                        target_id=feedback2.feedback_id,
                        relation_type=RelationType.OPPOSE,
                        strength=oppose_strength
                    )
                    self.relation_graph.add_relation(relation)
                
                # 检测补充关系
                complement_strength = self._detect_complement_relation(feedback1, feedback2)
                if complement_strength > self.relation_threshold:
                    relation = RelationModel(
                        source_id=feedback1.feedback_id,
                        target_id=feedback2.feedback_id,
                        relation_type=RelationType.COMPLEMENT,
                        strength=complement_strength
                    )
                    self.relation_graph.add_relation(relation)
    
    def _detect_support_relation(self, feedback1: FeedbackModel, feedback2: FeedbackModel) -> float:
        """
        检测两个反馈之间的支持关系强度
        
        Args:
            feedback1: 第一个反馈
            feedback2: 第二个反馈
            
        Returns:
            float: 支持关系强度，范围[0,1]
        """
        # 简单实现，实际应用中可以使用更复杂的算法
        # 例如，使用自然语言推理模型计算两个文本之间的蕴含关系
        if feedback1.content.content_type != feedback2.content.content_type:
            return 0.0
        
        if hasattr(feedback1.content, 'text') and hasattr(feedback2.content, 'text'):
            # 文本相似度作为支持关系的简单估计
            # 实际应用中可以使用更复杂的语义相似度算法
            text1 = feedback1.content.text.lower()
            text2 = feedback2.content.text.lower()
            
            # 计算词集合的Jaccard相似度
            words1 = set(text1.split())
            words2 = set(text2.split())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
        
        return 0.0
    
    def _detect_oppose_relation(self, feedback1: FeedbackModel, feedback2: FeedbackModel) -> float:
        """
        检测两个反馈之间的反对关系强度
        
        Args:
            feedback1: 第一个反馈
            feedback2: 第二个反馈
            
        Returns:
            float: 反对关系强度，范围[0,1]
        """
        # 简单实现，实际应用中可以使用更复杂的算法
        # 例如，使用自然语言推理模型计算两个文本之间的矛盾关系
        # 这里仅作为示例，返回一个较低的值
        return 0.1
    
    def _detect_complement_relation(self, feedback1: FeedbackModel, feedback2: FeedbackModel) -> float:
        """
        检测两个反馈之间的补充关系强度
        
        Args:
            feedback1: 第一个反馈
            feedback2: 第二个反馈
            
        Returns:
            float: 补充关系强度，范围[0,1]
        """
        # 简单实现，实际应用中可以使用更复杂的算法
        # 例如，计算信息增益或互补性
        # 这里仅作为示例，返回一个中等的值
        return 0.3
    
    def propagate_information(self, feedbacks: List[FeedbackModel]) -> Dict[str, Dict[str, float]]:
        """
        在关系图中传播信息
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            Dict[str, Dict[str, float]]: 信息传播结果，外层键为反馈ID，内层键为属性名，值为属性值
        """
        # 初始化节点状态
        node_states = {}
        for feedback in feedbacks:
            reliability = feedback.get_reliability()
            node_states[feedback.feedback_id] = {
                'reliability': reliability,
                'importance': 1.0,  # 初始重要性为1
                'content_vector': self._extract_content_vector(feedback)
            }
        
        # 迭代传播信息
        for _ in range(self.max_iterations):
            new_states = {}
            for feedback_id, state in node_states.items():
                # 获取与当前反馈相关的所有关系
                relations = self.relation_graph.get_relations_by_feedback(feedback_id)
                
                # 初始化新状态
                new_state = state.copy()
                
                # 根据关系更新状态
                for relation in relations:
                    other_id = relation.target_id if relation.source_id == feedback_id else relation.source_id
                    other_state = node_states.get(other_id)
                    
                    if other_state is None:
                        continue
                    
                    # 根据关系类型和强度更新状态
                    if relation.relation_type == RelationType.SUPPORT:
                        # 支持关系增强可靠性
                        new_state['reliability'] = min(1.0, new_state['reliability'] + 
                                                     relation.strength * other_state['reliability'] * 0.1)
                        # 支持关系增强重要性
                        new_state['importance'] = min(2.0, new_state['importance'] + 
                                                    relation.strength * other_state['importance'] * 0.1)
                    
                    elif relation.relation_type == RelationType.OPPOSE:
                        # 反对关系降低可靠性
                        new_state['reliability'] = max(0.0, new_state['reliability'] - 
                                                     relation.strength * other_state['reliability'] * 0.1)
                        # 反对关系可能增加或降低重要性，取决于具体应用
                    
                    elif relation.relation_type == RelationType.COMPLEMENT:
                        # 补充关系不影响可靠性，但增加重要性
                        new_state['importance'] = min(2.0, new_state['importance'] + 
                                                    relation.strength * 0.05)
                        # 补充关系可能影响内容向量，这里简化处理
                
                new_states[feedback_id] = new_state
            
            # 更新节点状态
            node_states = new_states
        
        return node_states
    
    def _extract_content_vector(self, feedback: FeedbackModel) -> List[float]:
        """
        从反馈内容中提取向量表示
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            List[float]: 内容的向量表示
        """
        # 简单实现，实际应用中可以使用更复杂的表示方法
        # 例如，使用预训练的语言模型生成文本嵌入
        # 这里仅返回一个随机向量作为示例
        return [0.5] * 10  # 10维向量，所有元素为0.5
    
    def fuse(self, feedbacks: List[FeedbackModel]) -> FeedbackModel:
        """
        融合反馈
        
        Args:
            feedbacks: 待融合的反馈列表
            
        Returns:
            FeedbackModel: 融合后的反馈
        """
        if not feedbacks:
            raise ValueError("No feedbacks to fuse")
        
        # 构建关系图
        self.build_relation_graph(feedbacks)
        
        # 传播信息
        node_states = self.propagate_information(feedbacks)
        
        # 根据节点状态计算权重
        weights = {}
        total_weight = 0.0
        for feedback_id, state in node_states.items():
            weight = state['reliability'] * state['importance']
            weights[feedback_id] = weight
            total_weight += weight
        
        if total_weight == 0.0:
            # 如果总权重为0，使用均匀权重
            for feedback_id in weights:
                weights[feedback_id] = 1.0 / len(feedbacks)
        else:
            # 归一化权重
            for feedback_id in weights:
                weights[feedback_id] /= total_weight
        
        # 根据权重融合反馈
        # 这里简单地选择权重最高的反馈作为基础，然后融合其他反馈的信息
        best_feedback_id = max(weights, key=weights.get)
        best_feedback = next(f for f in feedbacks if f.feedback_id == best_feedback_id)
        
        # 创建融合后的元数据
        metadata = MetadataModel(
            source="fusion.graph_based",
            feedback_type=best_feedback.metadata.feedback_type,
            timestamp=datetime.now(),
            tags=["fused"] + best_feedback.metadata.tags,
            reliability=sum(state['reliability'] * weights[fid] for fid, state in node_states.items())
        )
        
        # 创建融合后的内容
        # 这里简单地使用权重最高的反馈的内容，实际应用中可以进行更复杂的内容融合
        content = best_feedback.content
        
        # 创建融合后的反馈模型
        fused_feedback = FeedbackModel(metadata, content)
        
        # 添加与原始反馈的关系
        for feedback in feedbacks:
            relation = RelationModel(
                source_id=fused_feedback.feedback_id,
                target_id=feedback.feedback_id,
                relation_type=RelationType.REFINE,
                strength=weights[feedback.feedback_id],
                metadata={"fusion_weight": weights[feedback.feedback_id]}
            )
            fused_feedback.add_relation(relation)
        
        return fused_feedback

class AttentionBasedFusion(FeedbackFusion):
    """
    基于注意力机制的反馈融合
    
    使用注意力机制计算反馈之间的相关性，动态分配权重。
    """
    
    def __init__(self, attention_heads: int = 4, attention_dropout: float = 0.1):
        """
        初始化基于注意力机制的融合器
        
        Args:
            attention_heads: 注意力头数量
            attention_dropout: 注意力dropout率
        """
        self.attention_heads = attention_heads
        self.attention_dropout = attention_dropout
    
    def compute_attention(self, feedbacks: List[FeedbackModel]) -> np.ndarray:
        """
        计算反馈之间的注意力权重
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            np.ndarray: 注意力权重矩阵，形状为 [len(feedbacks), len(feedbacks)]
        """
        n = len(feedbacks)
        
        # 提取反馈特征
        features = np.zeros((n, 10))  # 假设每个反馈有10维特征
        for i, feedback in enumerate(feedbacks):
            features[i] = self._extract_features(feedback)
        
        # 计算注意力分数
        # 简化的自注意力机制，实际应用中可以使用更复杂的实现
        scores = np.dot(features, features.T)  # [n, n]
        
        # 应用softmax归一化
        attention_weights = np.zeros((n, n))
        for i in range(n):
            exp_scores = np.exp(scores[i] - np.max(scores[i]))  # 数值稳定性
            attention_weights[i] = exp_scores / np.sum(exp_scores)
        
        return attention_weights
    
    def _extract_features(self, feedback: FeedbackModel) -> np.ndarray:
        """
        从反馈中提取特征
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            np.ndarray: 特征向量
        """
        # 简单实现，实际应用中可以使用更复杂的特征提取方法
        features = np.zeros(10)
        
        # 添加可靠性特征
        features[0] = feedback.get_reliability()
        
        # 添加时间特征（越新的反馈权重越高）
        time_diff = (datetime.now() - feedback.metadata.timestamp).total_seconds() / 86400  # 转换为天数
        features[1] = max(0, 1 - (time_diff / 30))  # 一个月内的反馈时效性从1线性降至0
        
        # 添加来源特征
        if hasattr(feedback.metadata.source, 'value'):
            source_value = feedback.metadata.source.value
            if 'doctor' in source_value:
                features[2] = 0.9
            elif 'patient' in source_value:
                features[2] = 0.7
            elif 'system' in source_value:
                features[2] = 0.8
            elif 'knowledge' in source_value:
                features[2] = 0.85
        
        # 其他特征可以根据具体应用添加
        
        return features
    
    def fuse(self, feedbacks: List[FeedbackModel]) -> FeedbackModel:
        """
        融合反馈
        
        Args:
            feedbacks: 待融合的反馈列表
            
        Returns:
            FeedbackModel: 融合后的反馈
        """
        if not feedbacks:
            raise ValueError("No feedbacks to fuse")
        
        # 计算注意力权重
        attention_weights = self.compute_attention(feedbacks)
        
        # 计算每个反馈的综合权重（列和）
        weights = np.sum(attention_weights, axis=0)
        weights = weights / np.sum(weights)  # 归一化
        
        # 选择权重最高的反馈类型作为融合结果的类型
        best_idx = np.argmax(weights)
        best_feedback = feedbacks[best_idx]
        
        # 创建融合后的元数据
        metadata = MetadataModel(
            source="fusion.attention_based",
            feedback_type=best_feedback.metadata.feedback_type,
            timestamp=datetime.now(),
            tags=["fused"] + best_feedback.metadata.tags,
            reliability=np.sum([f.get_reliability() * w for f, w in zip(feedbacks, weights)])
        )
        
        # 创建融合后的内容
        # 这里简单地使用权重最高的反馈的内容，实际应用中可以进行更复杂的内容融合
        content = best_feedback.content
        
        # 创建融合后的反馈模型
        fused_feedback = FeedbackModel(metadata, content)
        
        # 添加与原始反馈的关系
        for i, feedback in enumerate(feedbacks):
            relation = RelationModel(
                source_id=fused_feedback.feedback_id,
                target_id=feedback.feedback_id,
                relation_type=RelationType.REFINE,
                strength=float(weights[i]),
                metadata={"attention_weight": float(weights[i])}
            )
            fused_feedback.add_relation(relation)
        
        return fused_feedback

class RLBasedFusion(FeedbackFusion):
    """
    基于强化学习的反馈融合
    
    将反馈融合视为一个序列决策问题，通过强化学习算法学习最优的融合策略。
    """
    
    def __init__(self, learning_rate: float = 0.01, discount_factor: float = 0.9):
        """
        初始化基于强化学习的融合器
        
        Args:
            learning_rate: 学习率
            discount_factor: 折扣因子
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_table = {}  # 状态-动作价值表
    
    def _get_state(self, feedbacks: List[FeedbackModel]) -> str:
        """
        获取当前状态的表示
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            str: 状态表示
        """
        # 简单实现，实际应用中可以使用更复杂的状态表示
        # 这里使用反馈类型和来源的组合作为状态
        state_parts = []
        for feedback in feedbacks:
            source = feedback.metadata.source
            source_value = source.value if hasattr(source, 'value') else str(source)
            
            feedback_type = feedback.metadata.feedback_type
            type_value = feedback_type.value if hasattr(feedback_type, 'value') else str(feedback_type)
            
            state_parts.append(f"{source_value}_{type_value}")
        
        # 排序以确保相同组合的反馈产生相同的状态
        state_parts.sort()
        return "_".join(state_parts)
    
    def _get_actions(self, feedbacks: List[FeedbackModel]) -> List[int]:
        """
        获取可用的动作列表
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            List[int]: 动作列表，每个动作对应选择一个反馈作为基础
        """
        return list(range(len(feedbacks)))
    
    def _get_reward(self, selected_feedback: FeedbackModel, feedbacks: List[FeedbackModel]) -> float:
        """
        计算选择特定反馈的奖励
        
        Args:
            selected_feedback: 选择的反馈
            feedbacks: 所有反馈
            
        Returns:
            float: 奖励值
        """
        # 简单实现，实际应用中可以使用更复杂的奖励函数
        # 这里使用反馈的可靠性作为奖励
        return selected_feedback.get_reliability()
    
    def fuse(self, feedbacks: List[FeedbackModel]) -> FeedbackModel:
        """
        融合反馈
        
        Args:
            feedbacks: 待融合的反馈列表
            
        Returns:
            FeedbackModel: 融合后的反馈
        """
        if not feedbacks:
            raise ValueError("No feedbacks to fuse")
        
        # 获取当前状态
        state = self._get_state(feedbacks)
        
        # 获取可用动作
        actions = self._get_actions(feedbacks)
        
        # 如果状态不在Q表中，初始化
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in actions}
        
        # 选择动作（使用epsilon-greedy策略）
        epsilon = 0.1  # 探索率
        if np.random.random() < epsilon:
            # 探索：随机选择动作
            action = np.random.choice(actions)
        else:
            # 利用：选择Q值最高的动作
            action = max(self.q_table[state], key=self.q_table[state].get)
        
        # 执行动作，选择基础反馈
        selected_feedback = feedbacks[action]
        
        # 计算奖励
        reward = self._get_reward(selected_feedback, feedbacks)
        
        # 更新Q值（简化版，实际应用中可以使用更复杂的更新规则）
        self.q_table[state][action] = (1 - self.learning_rate) * self.q_table[state][action] + \
                                     self.learning_rate * reward
        
        # 创建融合后的元数据
        metadata = MetadataModel(
            source="fusion.rl_based",
            feedback_type=selected_feedback.metadata.feedback_type,
            timestamp=datetime.now(),
            tags=["fused"] + selected_feedback.metadata.tags,
            reliability=selected_feedback.get_reliability()
        )
        
        # 创建融合后的内容
        # 这里简单地使用选定的反馈的内容，实际应用中可以进行更复杂的内容融合
        content = selected_feedback.content
        
        # 创建融合后的反馈模型
        fused_feedback = FeedbackModel(metadata, content)
        
        # 添加与原始反馈的关系
        for i, feedback in enumerate(feedbacks):
            strength = 1.0 if i == action else 0.1  # 选中的反馈关系强度更高
            relation = RelationModel(
                source_id=fused_feedback.feedback_id,
                target_id=feedback.feedback_id,
                relation_type=RelationType.REFINE,
                strength=strength,
                metadata={"selected": i == action}
            )
            fused_feedback.add_relation(relation)
        
        return fused_feedback

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
    
    def select_strategy(self, feedbacks: List[FeedbackModel], task_type: str = None) -> str:
        """
        选择最适合的融合策略
        
        Args:
            feedbacks: 反馈列表
            task_type: 任务类型
            
        Returns:
            str: 选择的策略名称
        """
        # 简单实现，实际应用中可以使用更复杂的策略选择算法
        # 例如，基于元学习或历史性能
        
        # 检查反馈数量
        if len(feedbacks) <= 2:
            return "attention"  # 反馈较少时使用注意力机制
        
        # 检查反馈关系
        has_relations = any(len(f.relations) > 0 for f in feedbacks)
        if has_relations:
            return "graph"  # 存在明确关系时使用图结构
        
        # 检查任务类型
        if task_type == "long_term_optimization":
            return "rl"  # 长期优化任务使用强化学习
        
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
        
        # 执行融合
        fused_feedback = strategy.fuse(feedbacks)
        
        # 添加融合策略信息
        if fused_feedback.metadata.tags is None:
            fused_feedback.metadata.tags = []
        fused_feedback.metadata.tags.append(f"fusion_strategy:{strategy_name}")
        
        return fused_feedback