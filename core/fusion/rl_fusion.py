# -*- coding: utf-8 -*-
"""
基于强化学习的反馈融合策略

该模块实现了基于强化学习的反馈融合策略，适用于长期优化和序列决策任务。
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import random

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent
from ...models.relation_model import RelationModel, RelationType
from .fusion import FeedbackFusion

class RLBasedFusion(FeedbackFusion):
    """
    基于强化学习的反馈融合
    
    使用强化学习方法动态调整反馈权重，适用于长期优化和序列决策任务。
    """
    
    def __init__(self, learning_rate: float = 0.01, discount_factor: float = 0.9, 
                 exploration_rate: float = 0.1, history_window: int = 10):
        """
        初始化基于强化学习的融合器
        
        Args:
            learning_rate: 学习率，控制Q值更新速度
            discount_factor: 折扣因子，控制未来奖励的重要性
            exploration_rate: 探索率，控制探索与利用的平衡
            history_window: 历史窗口大小，用于存储历史状态和动作
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.history_window = history_window
        
        # Q值表，用于存储状态-动作对的价值估计
        self.q_table = {}
        
        # 历史记录，用于存储过去的状态、动作和奖励
        self.history = []
        
        # 反馈特征提取器
        self.feature_extractors = {
            'reliability': lambda f: f.get_reliability(),
            'recency': self._extract_recency,
            'source_type': self._extract_source_type,
            'feedback_type': self._extract_feedback_type,
            'relation_count': lambda f: min(1.0, len(f.relations) * 0.2),
            'content_length': self._extract_content_length
        }
    
    def _extract_recency(self, feedback: FeedbackModel) -> float:
        """
        提取反馈的时效性特征
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            float: 时效性特征值，范围[0,1]，越新的反馈值越高
        """
        time_diff = (datetime.now() - feedback.metadata.timestamp).total_seconds() / 86400  # 转换为天数
        return max(0, 1 - (time_diff / 30))  # 一个月内的反馈时效性从1线性降至0
    
    def _extract_source_type(self, feedback: FeedbackModel) -> float:
        """
        提取反馈来源类型特征
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            float: 来源类型特征值，范围[0,1]
        """
        if hasattr(feedback.metadata.source, 'value'):
            source_value = feedback.metadata.source.value
            if 'doctor' in source_value:
                return 0.9
            elif 'patient' in source_value:
                return 0.7
            elif 'system' in source_value:
                return 0.8
            elif 'knowledge' in source_value:
                return 0.85
        return 0.5  # 默认值
    
    def _extract_feedback_type(self, feedback: FeedbackModel) -> float:
        """
        提取反馈类型特征
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            float: 反馈类型特征值，范围[0,1]
        """
        if hasattr(feedback.metadata.feedback_type, 'value'):
            type_value = feedback.metadata.feedback_type.value
            if 'diagnostic' in type_value:
                return 0.85
            elif 'therapeutic' in type_value:
                return 0.9
            elif 'prognostic' in type_value:
                return 0.8
        return 0.5  # 默认值
    
    def _extract_content_length(self, feedback: FeedbackModel) -> float:
        """
        提取内容长度特征
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            float: 内容长度特征值，范围[0,1]
        """
        if hasattr(feedback.content, 'text'):
            return min(1.0, len(feedback.content.text) / 1000)  # 文本长度归一化
        elif hasattr(feedback.content, 'data'):
            return min(1.0, len(str(feedback.content.data)) / 1000)  # 数据复杂度归一化
        return 0.5  # 默认值
    
    def _extract_state(self, feedbacks: List[FeedbackModel]) -> str:
        """
        从反馈列表中提取状态表示
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            str: 状态表示，用于Q表索引
        """
        # 提取反馈类型分布
        feedback_types = {}
        for feedback in feedbacks:
            if hasattr(feedback.metadata.feedback_type, 'value'):
                type_value = feedback.metadata.feedback_type.value
                if type_value not in feedback_types:
                    feedback_types[type_value] = 0
                feedback_types[type_value] += 1
        
        # 提取反馈来源分布
        source_types = {}
        for feedback in feedbacks:
            if hasattr(feedback.metadata.source, 'value'):
                source_value = feedback.metadata.source.value
                if source_value not in source_types:
                    source_types[source_value] = 0
                source_types[source_value] += 1
        
        # 计算反馈关系密度
        relation_count = sum(len(f.relations) for f in feedbacks)
        relation_density = relation_count / (len(feedbacks) * (len(feedbacks) - 1)) if len(feedbacks) > 1 else 0
        
        # 构建状态字符串
        state_parts = [
            f"types:{','.join(f'{k}:{v}' for k, v in sorted(feedback_types.items())[:3])}",
            f"sources:{','.join(f'{k}:{v}' for k, v in sorted(source_types.items())[:3])}",
            f"density:{int(relation_density * 10)}",
            f"count:{len(feedbacks)}"
        ]
        
        return "|".join(state_parts)
    
    def _get_possible_actions(self, feedbacks: List[FeedbackModel]) -> List[Tuple[str, List[float]]]:
        """
        获取可能的动作列表
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            List[Tuple[str, List[float]]]: 动作列表，每个动作是一个元组，包含动作名称和权重列表
        """
        n = len(feedbacks)
        
        # 定义几种权重分配策略
        actions = [
            ("uniform", [1.0/n] * n),  # 均匀分配
            ("reliability", [self.feature_extractors['reliability'](f) for f in feedbacks]),  # 按可靠性分配
            ("recency", [self.feature_extractors['recency'](f) for f in feedbacks]),  # 按时效性分配
            ("source", [self.feature_extractors['source_type'](f) for f in feedbacks]),  # 按来源分配
            ("feedback_type", [self.feature_extractors['feedback_type'](f) for f in feedbacks])  # 按反馈类型分配
        ]
        
        # 归一化权重
        normalized_actions = []
        for name, weights in actions:
            sum_weights = sum(weights)
            if sum_weights > 0:
                normalized_weights = [w / sum_weights for w in weights]
            else:
                normalized_weights = [1.0/n] * n  # 如果所有权重都为0，则均匀分配
            normalized_actions.append((name, normalized_weights))
        
        return normalized_actions
    
    def _select_action(self, state: str, possible_actions: List[Tuple[str, List[float]]]) -> Tuple[str, List[float]]:
        """
        选择动作
        
        Args:
            state: 当前状态
            possible_actions: 可能的动作列表
            
        Returns:
            Tuple[str, List[float]]: 选择的动作，包含动作名称和权重列表
        """
        # 探索：随机选择动作
        if random.random() < self.exploration_rate:
            return random.choice(possible_actions)
        
        # 利用：选择Q值最高的动作
        if state not in self.q_table:
            self.q_table[state] = {action[0]: 0.0 for action in possible_actions}
        
        q_values = self.q_table[state]
        best_action_name = max(q_values, key=q_values.get)
        
        # 找到对应的动作
        for action_name, weights in possible_actions:
            if action_name == best_action_name:
                return (action_name, weights)
        
        # 如果找不到（可能是因为动作空间变化），则随机选择
        return random.choice(possible_actions)
    
    def _calculate_reward(self, feedbacks: List[FeedbackModel], weights: List[float]) -> float:
        """
        计算奖励
        
        Args:
            feedbacks: 反馈列表
            weights: 权重列表
            
        Returns:
            float: 奖励值
        """
        # 这里使用一个简单的启发式方法计算奖励
        # 实际应用中可以使用更复杂的方法，例如用户满意度或任务成功率
        
        reward = 0.0
        
        # 奖励高可靠性反馈的高权重
        for i, feedback in enumerate(feedbacks):
            reliability = self.feature_extractors['reliability'](feedback)
            reward += weights[i] * reliability
        
        # 奖励关系一致性
        for i, feedback1 in enumerate(feedbacks):
            for j, feedback2 in enumerate(feedbacks):
                if i != j:
                    # 检查是否存在支持关系
                    support_relation = False
                    for relation in feedback1.relations:
                        if relation.target_id == feedback2.feedback_id and relation.relation_type == RelationType.SUPPORT:
                            support_relation = True
                            # 如果存在支持关系，权重应该相近
                            weight_diff = abs(weights[i] - weights[j])
                            reward -= weight_diff * relation.strength
                    
                    # 检查是否存在反对关系
                    oppose_relation = False
                    for relation in feedback1.relations:
                        if relation.target_id == feedback2.feedback_id and relation.relation_type == RelationType.OPPOSE:
                            oppose_relation = True
                            # 如果存在反对关系，权重应该差异大
                            weight_diff = abs(weights[i] - weights[j])
                            reward += weight_diff * relation.strength
        
        return reward
    
    def _update_q_value(self, state: str, action_name: str, reward: float, next_state: str) -> None:
        """
        更新Q值
        
        Args:
            state: 当前状态
            action_name: 动作名称
            reward: 奖励
            next_state: 下一个状态
        """
        if state not in self.q_table:
            self.q_table[state] = {}
        
        if action_name not in self.q_table[state]:
            self.q_table[state][action_name] = 0.0
        
        # 计算下一个状态的最大Q值
        if next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        else:
            max_next_q = 0.0
        
        # Q-learning更新公式
        current_q = self.q_table[state][action_name]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action_name] = new_q
    
    def _fuse_content(self, feedbacks: List[FeedbackModel], weights: List[float]) -> ContentModel:
        """
        根据权重融合反馈内容
        
        Args:
            feedbacks: 反馈列表
            weights: 每个反馈的权重
            
        Returns:
            ContentModel: 融合后的内容
        """
        # 检查内容类型
        content_types = set(f.content.content_type for f in feedbacks)
        
        # 如果所有反馈都是文本类型
        if len(content_types) == 1 and list(content_types)[0] == 'text':
            # 加权融合文本内容
            text_parts = []
            for i, feedback in enumerate(feedbacks):
                if weights[i] > 0.05:  # 只考虑权重大于阈值的反馈
                    text = feedback.content.text
                    text_parts.append(f"({weights[i]:.2f}) {text}")
            
            fused_text = "\n\n".join(text_parts)
            return TextContent(text=fused_text)
        
        # 如果所有反馈都是结构化数据类型
        elif len(content_types) == 1 and list(content_types)[0] == 'structured':
            # 加权融合结构化数据
            fused_data = {}
            for i, feedback in enumerate(feedbacks):
                if weights[i] > 0.05:  # 只考虑权重大于阈值的反馈
                    data = feedback.content.data
                    for key, value in data.items():
                        if key not in fused_data:
                            fused_data[key] = value * weights[i]
                        else:
                            fused_data[key] += value * weights[i]
            
            return StructuredContent(data=fused_data)
        
        # 如果反馈类型混合，转换为文本进行融合
        else:
            text_parts = []
            for i, feedback in enumerate(feedbacks):
                if weights[i] > 0.05:  # 只考虑权重大于阈值的反馈
                    if hasattr(feedback.content, 'text'):
                        text = feedback.content.text
                    elif hasattr(feedback.content, 'data'):
                        text = str(feedback.content.data)
                    else:
                        text = str(feedback.content)
                    
                    text_parts.append(f"({weights[i]:.2f}) {text}")
            
            fused_text = "\n\n".join(text_parts)
            return TextContent(text=fused_text)
    
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
        
        # 提取当前状态
        current_state = self._extract_state(feedbacks)
        
        # 获取可能的动作
        possible_actions = self._get_possible_actions(feedbacks)
        
        # 选择动作
        action_name, weights = self._select_action(current_state, possible_actions)
        
        # 计算奖励
        reward = self._calculate_reward(feedbacks, weights)
        
        # 更新历史记录
        self.history.append((current_state, action_name, reward))
        if len(self.history) > self.history_window:
            self.history.pop(0)
        
        # 如果历史记录中有足够的数据，更新Q值
        if len(self.history) >= 2:
            for i in range(len(self.history) - 1):
                prev_state, prev_action, prev_reward = self.history[i]
                next_state, _, _ = self.history[i + 1]
                self._update_q_value(prev_state, prev_action, prev_reward, next_state)
        
        # 融合内容
        fused_content = self._fuse_content(feedbacks, weights)
        
        # 创建融合后的反馈
        fused_feedback = FeedbackModel(
            feedback_id=f"fused_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            content=fused_content,
            metadata=MetadataModel(
                timestamp=datetime.now(),
                source=SourceType.SYSTEM,
                feedback_type=FeedbackType.FUSED,
                reliability=sum(f.get_reliability() * w for f, w in zip(feedbacks, weights)),
                tags=[f"fusion_method:rl", f"action:{action_name}", f"reward:{reward:.2f}"]
            ),
            relations=[]
        )
        
        # 添加与原始反馈的关系
        for feedback in feedbacks:
            relation = RelationModel(
                source_id=fused_feedback.feedback_id,
                target_id=feedback.feedback_id,
                relation_type=RelationType.DERIVED_FROM,
                strength=1.0
            )
            fused_feedback.relations.append(relation)
        
        return fused_feedback
    
    def get_q_table_summary(self) -> Dict[str, Any]:
        """
        获取Q表摘要
        
        Returns:
            Dict[str, Any]: Q表摘要信息
        """
        if not self.q_table:
            return {"message": "Q表为空"}
        
        # 计算每个状态的最佳动作
        best_actions = {}
        for state, actions in self.q_table.items():
            if actions:
                best_action = max(actions.items(), key=lambda x: x[1])
                best_actions[state] = {
                    "action": best_action[0],
                    "q_value": best_action[1]
                }
        
        # 计算每个动作被选为最佳的次数
        action_counts = {}
        for state_info in best_actions.values():
            action = state_info["action"]
            if action not in action_counts:
                action_counts[action] = 0
            action_counts[action] += 1
        
        return {
            "total_states": len(self.q_table),
            "best_actions": best_actions,
            "action_counts": action_counts
        }
    
    def adjust_learning_parameters(self, learning_rate: float = None, 
                                 discount_factor: float = None,
                                 exploration_rate: float = None) -> None:
        """
        调整学习参数
        
        Args:
            learning_rate: 新的学习率
            discount_factor: 新的折扣因子
            exploration_rate: 新的探索率
        """
        if learning_rate is not None:
            self.learning_rate = learning_rate
        
        if discount_factor is not None:
            self.discount_factor = discount_factor
        
        if exploration_rate is not None:
            self.exploration_rate = exploration_rate