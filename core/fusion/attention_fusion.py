# -*- coding: utf-8 -*-
"""
基于注意力机制的反馈融合策略

该模块实现了基于注意力机制的反馈融合策略，使用多头自注意力机制计算反馈之间的相关性。
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent
from ...models.relation_model import RelationModel, RelationType
from .fusion import FeedbackFusion

class AttentionBasedFusion(FeedbackFusion):
    """
    基于注意力机制的反馈融合
    
    使用多头自注意力机制计算反馈之间的相关性，动态分配权重。
    """
    
    def __init__(self, attention_heads: int = 4, attention_dropout: float = 0.1, feature_dim: int = 10):
        """
        初始化基于注意力机制的融合器
        
        Args:
            attention_heads: 注意力头数量
            attention_dropout: 注意力dropout率
            feature_dim: 特征维度
        """
        self.attention_heads = attention_heads
        self.attention_dropout = attention_dropout
        self.feature_dim = feature_dim
        
        # 初始化注意力权重矩阵
        self.query_weights = np.random.randn(attention_heads, feature_dim, feature_dim // attention_heads)
        self.key_weights = np.random.randn(attention_heads, feature_dim, feature_dim // attention_heads)
        self.value_weights = np.random.randn(attention_heads, feature_dim, feature_dim // attention_heads)
        self.output_weights = np.random.randn(feature_dim, feature_dim)
    
    def _extract_features(self, feedback: FeedbackModel) -> np.ndarray:
        """
        从反馈中提取特征向量
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            np.ndarray: 特征向量
        """
        features = np.zeros(self.feature_dim)
        
        # 添加可靠性特征
        features[0] = feedback.get_reliability()
        
        # 添加时间特征（越新的反馈权重越高）
        time_diff = (datetime.now() - feedback.metadata.timestamp).total_seconds() / 86400  # 转换为天数
        features[1] = max(0, 1 - (time_diff / 30))  # 一个月内的反馈时效性从1线性降至0
        
        # 添加来源特征
        if hasattr(feedback.metadata.source, 'value'):
            source_value = feedback.metadata.source.value
            if 'doctor' in source_value:
                features[2] = 0.9  # 医生反馈可靠性高
            elif 'patient' in source_value:
                features[2] = 0.7  # 患者反馈可靠性中等
            elif 'system' in source_value:
                features[2] = 0.8  # 系统反馈可靠性较高
            elif 'knowledge' in source_value:
                features[2] = 0.85  # 知识库反馈可靠性较高
            elif 'specialist' in source_value:
                features[2] = 0.95  # 专科医生反馈可靠性最高
            elif 'literature' in source_value:
                features[2] = 0.88  # 文献反馈可靠性较高
        
        # 添加反馈类型特征
        if hasattr(feedback.metadata.feedback_type, 'value'):
            type_value = feedback.metadata.feedback_type.value
            if 'diagnostic' in type_value:
                features[3] = 0.85  # 诊断反馈
            elif 'therapeutic' in type_value:
                features[3] = 0.9   # 治疗反馈
            elif 'prognostic' in type_value:
                features[3] = 0.8   # 预后反馈
            elif 'preventive' in type_value:
                features[3] = 0.75  # 预防反馈
            elif 'monitoring' in type_value:
                features[3] = 0.82  # 监测反馈
            elif 'emergency' in type_value:
                features[3] = 0.95  # 紧急反馈优先级最高
        
        # 添加关系特征
        features[4] = min(1.0, len(feedback.relations) * 0.2)  # 关系越多，特征值越高，最大为1
        
        # 添加内容特征
        if hasattr(feedback.content, 'text'):
            # 文本长度特征
            features[5] = min(1.0, len(feedback.content.text) / 1000)  # 文本长度归一化
            
            # 医疗术语密度特征
            medical_terms = ['诊断', '治疗', '症状', '病因', '预后', '用药', '剂量', '副作用', 
                           '禁忌症', '适应症', '检查', '手术', '康复', '随访', '并发症',
                           'diagnosis', 'treatment', 'symptom', 'etiology', 'prognosis',
                           'medication', 'dosage', 'side effect', 'contraindication',
                           'indication', 'examination', 'surgery', 'rehabilitation']
            
            text = feedback.content.text.lower()
            term_count = sum(1 for term in medical_terms if term in text)
            features[6] = min(1.0, term_count / 10)  # 医疗术语密度归一化
            
        elif hasattr(feedback.content, 'data'):
            # 结构化数据复杂度
            features[5] = min(1.0, len(str(feedback.content.data)) / 1000)  # 数据复杂度归一化
            
            # 医疗数据特征
            medical_keys = ['诊断', '治疗', '症状', '病因', '预后', '用药', '剂量', '副作用',
                          'diagnosis', 'treatment', 'symptom', 'etiology', 'prognosis',
                          'medication', 'dosage', 'side_effect']
            
            data = feedback.content.data
            medical_key_count = sum(1 for key in medical_keys if any(med_key in str(k) for k in data.keys() for med_key in medical_keys))
            features[6] = min(1.0, medical_key_count / 5)  # 医疗数据特征归一化
        
        # 添加标签特征
        if hasattr(feedback.metadata, 'tags') and feedback.metadata.tags:
            features[7] = min(1.0, len(feedback.metadata.tags) / 10)  # 标签数量归一化
            
            # 紧急程度特征
            urgency_tags = ['urgent', 'emergency', 'critical', 'important', '紧急', '重要', '关键']
            has_urgency = any(tag in urgency_tags for tag in feedback.metadata.tags)
            features[8] = 1.0 if has_urgency else 0.0
        
        # 添加医疗领域特定特征
        features[9] = self._extract_medical_domain_feature(feedback)
        
        return features
    
    def _extract_medical_domain_feature(self, feedback: FeedbackModel) -> float:
        """
        提取医疗领域特定特征
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            float: 医疗领域特征值，范围[0,1]
        """
        score = 0.5  # 默认中等分数
        
        # 检查来源是否为医疗专业人员
        if hasattr(feedback.metadata.source, 'value'):
            source_value = feedback.metadata.source.value.lower()
            if 'doctor' in source_value or 'physician' in source_value:
                score += 0.2
            if 'specialist' in source_value:
                score += 0.1
            if 'professor' in source_value or 'expert' in source_value:
                score += 0.1
        
        # 检查内容中的医疗术语密度
        if hasattr(feedback.content, 'text'):
            text = feedback.content.text.lower()
            
            # 高级医疗术语列表
            advanced_medical_terms = [
                '病理生理', '分子机制', '信号通路', '基因表达', '免疫应答',
                '药物动力学', '药效学', '临床 Trial', '循证医学', '系统综述',
                'pathophysiology', 'molecular mechanism', 'signaling pathway',
                'gene expression', 'immune response', 'pharmacokinetics',
                'pharmacodynamics', 'clinical trial', 'evidence-based',
                'systematic review', 'meta-analysis'
            ]
            
            # 计算高级术语出现次数
            term_count = sum(1 for term in advanced_medical_terms if term in text)
            score += min(0.2, term_count * 0.05)  # 每个高级术语增加0.05分，最多0.2分
        
        return min(1.0, score)  # 确保分数不超过1

    def compute_medical_attention_weights(self, feedbacks: List[FeedbackModel]) -> np.ndarray:
        """
        计算医疗领域特定的注意力权重
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            np.ndarray: 注意力权重矩阵，形状为 [len(feedbacks)]
        """
        n = len(feedbacks)
        if n == 0:
            return np.array([])
        
        # 初始化权重
        weights = np.ones(n)
        
        # 根据来源调整权重
        for i, feedback in enumerate(feedbacks):
            if hasattr(feedback.metadata.source, 'value'):
                source = feedback.metadata.source.value.lower()
                
                # 医生反馈权重提升
                if 'doctor' in source:
                    weights[i] *= 1.5
                
                # 专科医生反馈权重进一步提升
                if 'specialist' in source:
                    weights[i] *= 1.2
                
                # 患者反馈权重降低
                if 'patient' in source:
                    weights[i] *= 0.8
        
        # 根据反馈类型调整权重
        for i, feedback in enumerate(feedbacks):
            if hasattr(feedback.metadata.feedback_type, 'value'):
                feedback_type = feedback.metadata.feedback_type.value.lower()
                
                # 紧急反馈权重提升
                if 'emergency' in feedback_type:
                    weights[i] *= 2.0
                
                # 治疗反馈权重提升
                if 'therapeutic' in feedback_type:
                    weights[i] *= 1.3
                
                # 诊断反馈权重提升
                if 'diagnostic' in feedback_type:
                    weights[i] *= 1.2
        
        # 根据内容调整权重
        for i, feedback in enumerate(feedbacks):
            if hasattr(feedback.content, 'text'):
                text = feedback.content.text.lower()
                
                # 包含关键医疗术语的反馈权重提升
                critical_terms = ['危重', '紧急', '立即', '生命危险', '不良反应', '严重并发症',
                                'critical', 'emergency', 'immediate', 'life-threatening',
                                'adverse reaction', 'severe complication']
                
                for term in critical_terms:
                    if term in text:
                        weights[i] *= 1.5
                        break
        
        # 归一化权重
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        else:
            weights = np.ones(n) / n
        
        return weights

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
        
        # 提取反馈特征
        n = len(feedbacks)
        features = np.zeros((n, self.feature_dim))
        for i, feedback in enumerate(feedbacks):
            features[i] = self._extract_features(feedback)
        
        # 计算注意力权重
        attention_weights = self._multi_head_attention(features)
        
        # 计算最终权重（每个反馈的权重是其所有注意力权重的平均值）
        weights = np.mean(attention_weights, axis=0)
        
        # 医疗领域特定处理：检查是否需要使用医疗特定权重
        medical_domain = False
        for feedback in feedbacks:
            if hasattr(feedback.metadata.source, 'value'):
                source = feedback.metadata.source.value.lower()
                if any(term in source for term in ['doctor', 'patient', 'hospital', 'clinic', 'medical']):
                    medical_domain = True
                    break
            
            if hasattr(feedback.metadata.feedback_type, 'value'):
                feedback_type = feedback.metadata.feedback_type.value.lower()
                if any(term in feedback_type for term in ['diagnostic', 'therapeutic', 'clinical']):
                    medical_domain = True
                    break
        
        # 如果是医疗领域，结合医疗特定权重
        if medical_domain:
            medical_weights = self.compute_medical_attention_weights(feedbacks)
            # 医疗权重和注意力权重各占50%
            weights = 0.5 * weights + 0.5 * medical_weights
        
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
                tags=["fusion_method:attention"]
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
        
        # 如果是医疗领域，添加标签
        if medical_domain:
            fused_feedback.metadata.tags.append("medical_domain_specific")
        
        return fused_feedback
    
    def _apply_dropout(self, matrix: np.ndarray) -> np.ndarray:
        """
        应用dropout
        
        Args:
            matrix: 输入矩阵
            
        Returns:
            np.ndarray: 应用dropout后的矩阵
        """
        if self.attention_dropout <= 0:
            return matrix
            
        mask = np.random.binomial(1, 1 - self.attention_dropout, size=matrix.shape)
        return matrix * mask / (1 - self.attention_dropout)  # 缩放以保持期望值不变
    
    def _multi_head_attention(self, features: np.ndarray) -> np.ndarray:
        """
        计算多头自注意力
        
        Args:
            features: 特征矩阵，形状为 [n_feedbacks, feature_dim]
            
        Returns:
            np.ndarray: 注意力输出，形状为 [n_feedbacks, feature_dim]
        """
        n_feedbacks = features.shape[0]
        head_dim = self.feature_dim // self.attention_heads
        
        # 初始化输出
        attention_output = np.zeros((n_feedbacks, self.feature_dim))
        
        # 计算每个注意力头
        for h in range(self.attention_heads):
            # 计算查询、键、值
            queries = np.dot(features, self.query_weights[h])  # [n_feedbacks, head_dim]
            keys = np.dot(features, self.key_weights[h])  # [n_feedbacks, head_dim]
            values = np.dot(features, self.value_weights[h])  # [n_feedbacks, head_dim]
            
            # 计算注意力分数
            scores = np.dot(queries, keys.T) / np.sqrt(head_dim)  # [n_feedbacks, n_feedbacks]
            
            # 应用softmax
            exp_scores = np.exp(scores - np.max(scores, axis=1, keepdims=True))  # 数值稳定性
            attention_weights = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)  # [n_feedbacks, n_feedbacks]
            
            # 应用dropout
            attention_weights = self._apply_dropout(attention_weights)
            
            # 计算加权和
            head_output = np.dot(attention_weights, values)  # [n_feedbacks, head_dim]
            
            # 拼接到输出
            attention_output[:, h*head_dim:(h+1)*head_dim] = head_output
        
        # 应用输出投影
        output = np.dot(attention_output, self.output_weights)
        
        return output
    
    def compute_attention_weights(self, feedbacks: List[FeedbackModel]) -> np.ndarray:
        """
        计算反馈之间的注意力权重
        
        Args:
            feedbacks: 反馈列表
            
        Returns:
            np.ndarray: 注意力权重矩阵，形状为 [len(feedbacks), len(feedbacks)]
        """
        n = len(feedbacks)
        
        # 提取反馈特征
        features = np.zeros((n, self.feature_dim))
        for i, feedback in enumerate(feedbacks):
            features[i] = self._extract_features(feedback)
        
        # 计算注意力分数
        queries = features  # [n, feature_dim]
        keys = features  # [n, feature_dim]
        
        # 计算点积注意力
        scores = np.dot(queries, keys.T) / np.sqrt(self.feature_dim)  # [n, n]
        
        # 应用softmax归一化
        attention_weights = np.zeros((n, n))
        for i in range(n):
            exp_scores = np.exp(scores[i] - np.max(scores[i]))  # 数值稳定性
            attention_weights[i] = exp_scores / np.sum(exp_scores)
        
        return attention_weights
    
    def _fuse_content(self, feedbacks: List[FeedbackModel], weights: np.ndarray) -> ContentModel:
        """
        根据权重融合反馈内容
        
        Args:
            feedbacks: 反馈列表
            weights: 每个反馈的权重
            
        Returns:
            ContentModel: 融合后的内容
        """
        # 确定主要反馈类型
        text_feedbacks = [f for f in feedbacks if hasattr(f.content, 'text')]
        structured_feedbacks = [f for f in feedbacks if hasattr(f.content, 'data')]
        
        # 如果主要是文本反馈
        if len(text_feedbacks) >= len(structured_feedbacks):
            # 获取所有文本反馈
            texts = []
            for i, feedback in enumerate(feedbacks):
                if hasattr(feedback.content, 'text'):
                    weight = weights[i]
                    if weight > 0.1:  # 只考虑权重较高的反馈
                        texts.append(f"[权重: {weight:.2f}] {feedback.content.text}")
            
            # 融合文本
            if texts:
                fused_text = "\n\n".join(texts)
                return TextContent(text=fused_text, language="zh-CN")
            else:
                return feedbacks[np.argmax(weights)].content
        
        # 如果主要是结构化反馈
        else:
            # 融合结构化数据
            fused_data = {}
            for i, feedback in enumerate(feedbacks):
                if hasattr(feedback.content, 'data'):
                    weight = weights[i]
                    if weight > 0.1:  # 只考虑权重较高的反馈
                        for key, value in feedback.content.data.items():
                            if key not in fused_data:
                                fused_data[key] = value
                            else:
                                # 对于已存在的键，根据权重决定是否覆盖
                                for j, other_feedback in enumerate(feedbacks):
                                    if j < i and hasattr(other_feedback.content, 'data') and key in other_feedback.content.data:
                                        if weights[i] > weights[j]:
                                            fused_data[key] = value
                                        break
            
            return StructuredContent(data=fused_data)
    
    def fuse(self, feedbacks: List[FeedbackModel], task_context: Dict[str, Any] = None) -> FeedbackModel:
        """
        融合反馈
        
        Args:
            feedbacks: 待融合的反馈列表
            task_context: 任务上下文信息
            
        Returns:
            FeedbackModel: 融合后的反馈
        """
        if not feedbacks:
            raise ValueError("No feedbacks to fuse")
        
        # 提取特征
        features = np.zeros((len(feedbacks), self.feature_dim))
        for i, feedback in enumerate(feedbacks):
            features[i] = self._extract_features(feedback)
        
        # 应用多头注意力
        attention_output = self._multi_head_attention(features)
        
        # 计算每个反馈的综合权重（使用注意力输出的第一个特征作为权重）
        weights = np.abs(attention_output[:, 0])
        weights = weights / np.sum(weights)  # 归一化
        
        # 选择权重最高的反馈类型作为融合结果的类型
        best_idx = np.argmax(weights)
        best_feedback = feedbacks[best_idx]
        
        # 创建融合后的元数据
        metadata = MetadataModel(
            source="fusion.attention_based",
            feedback_type=best_feedback.metadata.feedback_type,
            timestamp=datetime.now(),
            tags=["fused", "attention_fusion"] + best_feedback.metadata.tags,
            reliability=np.sum([f.get_reliability() * w for f, w in zip(feedbacks, weights)])
        )
        
        # 融合内容
        content = self._fuse_content(feedbacks, weights)
        
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