# -*- coding: utf-8 -*-
"""
基于图结构的反馈融合策略

该模块实现了基于图结构的反馈融合策略，将反馈表示为图中的节点，通过图算法进行信息传递和融合。
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent
from ...models.relation_model import RelationModel, RelationType, RelationGraph
from .fusion import FeedbackFusion

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
        # 检查反馈类型是否相同
        if feedback1.content.content_type != feedback2.content.content_type:
            return 0.0
        
        # 文本反馈的支持关系检测
        if hasattr(feedback1.content, 'text') and hasattr(feedback2.content, 'text'):
            # 文本相似度作为支持关系的简单估计
            text1 = feedback1.content.text.lower()
            text2 = feedback2.content.text.lower()
            
            # 计算词集合的Jaccard相似度
            words1 = set(text1.split())
            words2 = set(text2.split())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            similarity = intersection / union
            
            # 考虑反馈来源的可靠性
            source_factor = 1.0
            if hasattr(feedback1.metadata.source, 'value') and hasattr(feedback2.metadata.source, 'value'):
                source1 = feedback1.metadata.source.value
                source2 = feedback2.metadata.source.value
                
                # 如果两个反馈来源相同，降低支持关系强度（避免信息冗余）
                if source1 == source2:
                    source_factor = 0.8
                # 如果一个是医生，一个是系统，增强支持关系强度
                elif ('doctor' in source1 and 'system' in source2) or ('system' in source1 and 'doctor' in source2):
                    source_factor = 1.2
            
            return min(1.0, similarity * source_factor)
        
        # 结构化反馈的支持关系检测
        elif hasattr(feedback1.content, 'data') and hasattr(feedback2.content, 'data'):
            data1 = feedback1.content.data
            data2 = feedback2.content.data
            
            # 检查共同键的值是否相似
            common_keys = set(data1.keys()).intersection(set(data2.keys()))
            if not common_keys:
                return 0.0
                
            # 计算值的相似度
            similarity_sum = 0.0
            for key in common_keys:
                val1 = data1[key]
                val2 = data2[key]
                
                # 数值型数据
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # 计算相对差异
                    max_val = max(abs(val1), abs(val2))
                    if max_val == 0:
                        similarity_sum += 1.0  # 两个值都为0，完全相同
                    else:
                        diff = abs(val1 - val2) / max_val
                        similarity_sum += max(0.0, 1.0 - diff)
                # 字符串型数据
                elif isinstance(val1, str) and isinstance(val2, str):
                    # 简单字符串匹配
                    if val1.lower() == val2.lower():
                        similarity_sum += 1.0
                    else:
                        # 计算字符串相似度
                        words1 = set(val1.lower().split())
                        words2 = set(val2.lower().split())
                        intersection = len(words1.intersection(words2))
                        union = len(words1.union(words2))
                        
                        if union > 0:
                            similarity_sum += intersection / union
                # 其他类型数据
                else:
                    # 简单相等判断
                    similarity_sum += 1.0 if val1 == val2 else 0.0
            
            return similarity_sum / len(common_keys)
        
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
        # 检查反馈类型是否相同
        if feedback1.content.content_type != feedback2.content.content_type:
            return 0.0
        
        # 文本反馈的反对关系检测
        if hasattr(feedback1.content, 'text') and hasattr(feedback2.content, 'text'):
            text1 = feedback1.content.text.lower()
            text2 = feedback2.content.text.lower()
            
            # 检查否定词的存在
            negation_words = ['不', '否', '非', '无', '没有', '不是', '不能', '不应', '不宜', '禁止', 'no', 'not', 'never', 'disagree']
            has_negation1 = any(word in text1 for word in negation_words)
            has_negation2 = any(word in text2 for word in negation_words)
            
            # 如果一个有否定词，一个没有，可能存在反对关系
            negation_factor = 1.0 if (has_negation1 and not has_negation2) or (not has_negation1 and has_negation2) else 0.5
            
            # 计算词集合的Jaccard相似度
            words1 = set(text1.split())
            words2 = set(text2.split())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            similarity = intersection / union
            
            # 医疗领域特定的反对关系检测
            medical_oppose_terms = {
                '增加': '减少', '升高': '降低', '提高': '降低', '加强': '减弱', 
                '促进': '抑制', '激活': '抑制', '开始': '停止', '用药': '禁用',
                '适用': '禁忌', '建议': '不建议', '推荐': '不推荐'
            }
            
            # 检查是否存在医疗领域的反义词对
            medical_oppose_score = 0.0
            for term1, term2 in medical_oppose_terms.items():
                if (term1 in text1 and term2 in text2) or (term2 in text1 and term1 in text2):
                    medical_oppose_score += 0.3  # 每找到一对反义词，增加反对关系强度
            
            # 考虑反馈来源的可靠性
            source_factor = 1.0
            if hasattr(feedback1.metadata.source, 'value') and hasattr(feedback2.metadata.source, 'value'):
                source1 = feedback1.metadata.source.value
                source2 = feedback2.metadata.source.value
                
                # 如果两个反馈来源都是医生，增强反对关系的可信度
                if 'doctor' in source1 and 'doctor' in source2:
                    source_factor = 1.2
            
            # 综合计算反对关系强度
            oppose_strength = (similarity * negation_factor + medical_oppose_score) * source_factor
            return min(1.0, oppose_strength)
        
        # 结构化反馈的反对关系检测
        elif hasattr(feedback1.content, 'data') and hasattr(feedback2.content, 'data'):
            data1 = feedback1.content.data
            data2 = feedback2.content.data
            
            # 检查共同键的值是否相反
            common_keys = set(data1.keys()).intersection(set(data2.keys()))
            if not common_keys:
                return 0.0
                
            # 计算值的差异度
            difference_sum = 0.0
            for key in common_keys:
                val1 = data1[key]
                val2 = data2[key]
                
                # 数值型数据
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # 检查数值是否有显著差异或相反趋势
                    if (val1 > 0 and val2 < 0) or (val1 < 0 and val2 > 0):  # 符号相反
                        difference_sum += 1.0
                    else:
                        # 计算相对差异
                        max_val = max(abs(val1), abs(val2))
                        if max_val == 0:
                            difference_sum += 0.0  # 两个值都为0，没有差异
                        else:
                            diff = abs(val1 - val2) / max_val
                            difference_sum += min(1.0, diff)  # 差异越大，反对关系越强
                
                # 字符串型数据
                elif isinstance(val1, str) and isinstance(val2, str):
                    # 检查是否为医疗领域的反义词对
                    medical_oppose_terms = {
                        '增加': '减少', '升高': '降低', '提高': '降低', '加强': '减弱', 
                        '促进': '抑制', '激活': '抑制', '开始': '停止', '用药': '禁用',
                        '适用': '禁忌', '建议': '不建议', '推荐': '不推荐', '阳性': '阴性'
                    }
                    
                    val1_lower = val1.lower()
                    val2_lower = val2.lower()
                    
                    # 检查是否存在医疗领域的反义词对
                    found_oppose = False
                    for term1, term2 in medical_oppose_terms.items():
                        if (term1 in val1_lower and term2 in val2_lower) or (term2 in val1_lower and term1 in val2_lower):
                            difference_sum += 1.0
                            found_oppose = True
                            break
                    
                    if not found_oppose:
                        # 如果不是明确的反义词对，检查一般的差异
                        if val1_lower != val2_lower:
                            # 计算字符串相似度
                            words1 = set(val1_lower.split())
                            words2 = set(val2_lower.split())
                            intersection = len(words1.intersection(words2))
                            union = len(words1.union(words2))
                            
                            if union > 0:
                                similarity = intersection / union
                                difference_sum += 1.0 - similarity  # 相似度越低，差异越大
                            else:
                                difference_sum += 0.5  # 默认中等差异
                
                # 其他类型数据
                else:
                    # 简单不等判断
                    difference_sum += 1.0 if val1 != val2 else 0.0
            
            return difference_sum / len(common_keys)
        
        return 0.0

    def _detect_complement_relation(self, feedback1: FeedbackModel, feedback2: FeedbackModel) -> float:
        """
        检测两个反馈之间的补充关系强度
        
        Args:
            feedback1: 第一个反馈
            feedback2: 第二个反馈
            
        Returns:
            float: 补充关系强度，范围[0,1]
        """
        # 检查反馈类型是否相同
        if feedback1.content.content_type != feedback2.content.content_type:
            # 不同类型的反馈可能互补
            return 0.6
        
        # 文本反馈的补充关系检测
        if hasattr(feedback1.content, 'text') and hasattr(feedback2.content, 'text'):
            text1 = feedback1.content.text.lower()
            text2 = feedback2.content.text.lower()
            
            # 计算词集合的差异
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            # 计算独有词的比例
            unique_words1 = words1 - words2
            unique_words2 = words2 - words1
            total_unique = len(unique_words1) + len(unique_words2)
            total_words = len(words1.union(words2))
            
            if total_words == 0:
                return 0.0
            
            # 独有词比例越高，补充关系越强
            unique_ratio = total_unique / total_words
            
            # 医疗领域特定的补充关系检测
            medical_complement_pairs = [
                ('症状', '治疗'), ('诊断', '预后'), ('检查', '结果'), 
                ('用药', '剂量'), ('病因', '预防'), ('适应症', '禁忌症'),
                ('主诉', '体征'), ('病史', '家族史'), ('既往史', '现病史'),
                ('检验', '影像'), ('治疗', '随访'), ('手术', '康复')
            ]
            
            # 检查是否存在医疗领域的补充词对
            medical_complement_score = 0.0
            for term1, term2 in medical_complement_pairs:
                if (term1 in text1 and term2 in text2) or (term2 in text1 and term1 in text2):
                    medical_complement_score += 0.2  # 每找到一对补充词，增加补充关系强度
            
            # 考虑反馈来源的互补性
            source_factor = 1.0
            if hasattr(feedback1.metadata.source, 'value') and hasattr(feedback2.metadata.source, 'value'):
                source1 = feedback1.metadata.source.value
                source2 = feedback2.metadata.source.value
                
                # 如果一个是医生，一个是患者，增强补充关系
                if ('doctor' in source1 and 'patient' in source2) or ('patient' in source1 and 'doctor' in source2):
                    source_factor = 1.5
                # 如果一个是医生，一个是知识库，增强补充关系
                elif ('doctor' in source1 and 'knowledge' in source2) or ('knowledge' in source1 and 'doctor' in source2):
                    source_factor = 1.3
            
            # 综合计算补充关系强度
            complement_strength = (unique_ratio * 0.7 + medical_complement_score) * source_factor
            return min(1.0, complement_strength)
        
        # 结构化反馈的补充关系检测
        elif hasattr(feedback1.content, 'data') and hasattr(feedback2.content, 'data'):
            data1 = feedback1.content.data
            data2 = feedback2.content.data
            
            # 检查键的互补性
            keys1 = set(data1.keys())
            keys2 = set(data2.keys())
            
            # 独有键的比例
            unique_keys1 = keys1 - keys2
            unique_keys2 = keys2 - keys1
            total_unique_keys = len(unique_keys1) + len(unique_keys2)
            total_keys = len(keys1.union(keys2))
            
            if total_keys == 0:
                return 0.0
            
            # 独有键比例越高，补充关系越强
            unique_key_ratio = total_unique_keys / total_keys
            
            # 医疗领域特定的补充关系检测
            medical_complement_keys = [
                ('症状', '治疗'), ('诊断', '预后'), ('检查', '结果'), 
                ('用药', '剂量'), ('病因', '预防'), ('适应症', '禁忌症')
            ]
            
            # 检查是否存在医疗领域的补充键对
            medical_complement_score = 0.0
            for key1, key2 in medical_complement_keys:
                if (key1 in keys1 and key2 in keys2) or (key2 in keys1 and key1 in keys2):
                    medical_complement_score += 0.2  # 每找到一对补充键，增加补充关系强度
            
            # 综合计算补充关系强度
            complement_strength = unique_key_ratio * 0.7 + medical_complement_score
            return min(1.0, complement_strength)
        
        return 0.3  # 默认中等补充关系强度
    
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
    
    def _extract_content_vector(self, feedback: FeedbackModel) -> np.ndarray:
        """
        从反馈内容中提取向量表示
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            np.ndarray: 内容的向量表示
        """
        # 提取10维特征向量
        features = np.zeros(10)
        
        # 添加可靠性特征
        features[0] = feedback.get_reliability()
        
        # 添加时间特征
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
        
        # 添加反馈类型特征
        if hasattr(feedback.metadata.feedback_type, 'value'):
            type_value = feedback.metadata.feedback_type.value
            if 'diagnostic' in type_value:
                features[3] = 0.85
            elif 'therapeutic' in type_value:
                features[3] = 0.9
            elif 'prognostic' in type_value:
                features[3] = 0.8
        
        # 添加内容特征
        if hasattr(feedback.content, 'text'):
            # 文本长度特征
            features[4] = min(1.0, len(feedback.content.text) / 1000)  # 文本长度归一化
        elif hasattr(feedback.content, 'data'):
            # 结构化数据复杂度
            features[4] = min(1.0, len(str(feedback.content.data)) / 1000)  # 数据复杂度归一化
        
        return features
    
    def _fuse_content(self, feedbacks: List[FeedbackModel], weights: Dict[str, float]) -> ContentModel:
        """
        根据权重融合反馈内容
        
        Args:
            feedbacks: 反馈列表
            weights: 每个反馈的权重，键为反馈ID
            
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
            for feedback in feedbacks:
                if hasattr(feedback.content, 'text'):
                    weight = weights.get(feedback.feedback_id, 0.0)
                    if weight > 0.1:  # 只考虑权重较高的反馈
                        texts.append(f"[权重: {weight:.2f}] {feedback.content.text}")
            
            # 融合文本
            if texts:
                fused_text = "\n\n".join(texts)
                return TextContent(text=fused_text, language="zh-CN")
            else:
                # 如果没有有效的文本反馈，使用权重最高的反馈内容
                best_feedback = max(feedbacks, key=lambda f: weights.get(f.feedback_id, 0.0))
                return best_feedback.content
        
        # 如果主要是结构化反馈
        else:
            # 融合结构化数据
            fused_data = {}
            for feedback in feedbacks:
                if hasattr(feedback.content, 'data'):
                    weight = weights.get(feedback.feedback_id, 0.0)
                    if weight > 0.1:  # 只考虑权重较高的反馈
                        for key, value in feedback.content.data.items():
                            if key not in fused_data:
                                fused_data[key] = value
                            else:
                                # 对于已存在的键，根据权重决定是否覆盖
                                for other_feedback in feedbacks:
                                    if other_feedback.feedback_id != feedback.feedback_id and \
                                       hasattr(other_feedback.content, 'data') and \
                                       key in other_feedback.content.data:
                                        other_weight = weights.get(other_feedback.feedback_id, 0.0)
                                        if weight > other_weight:
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
            for feedback in feedbacks:
                weights[feedback.feedback_id] = 1.0 / len(feedbacks)
        else:
            # 归一化权重
            for feedback_id in weights:
                weights[feedback_id] /= total_weight
        
        # 选择权重最高的反馈作为基础
        best_feedback_id = max(weights, key=weights.get)
        best_feedback = next(f for f in feedbacks if f.feedback_id == best_feedback_id)
        
        # 创建融合后的元数据
        metadata = MetadataModel(
            source="fusion.graph_based",
            feedback_type=best_feedback.metadata.feedback_type,
            timestamp=datetime.now(),
            tags=["fused", "graph_fusion"] + best_feedback.metadata.tags,
            reliability=sum(state['reliability'] * weights[fid] for fid, state in node_states.items())
        )
        
        # 融合内容
        content = self._fuse_content(feedbacks, weights)
        
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