# -*- coding: utf-8 -*-
"""
反馈元数据模型

该模块定义了反馈的基本属性和元信息，为反馈的管理和评估提供基础。
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum

class SourceType(Enum):
    """
    反馈来源类型枚举
    """
    HUMAN_DOCTOR = "human.doctor"          # 医生
    HUMAN_PATIENT = "human.patient"        # 患者
    HUMAN_NURSE = "human.nurse"            # 护士
    SYSTEM_IMAGING = "system.imaging"      # 医学影像系统
    SYSTEM_LAB = "system.lab"              # 实验室检查系统
    SYSTEM_EHR = "system.ehr"              # 电子健康记录系统
    KNOWLEDGE_GRAPH = "knowledge.graph"    # 知识图谱
    KNOWLEDGE_LITERATURE = "knowledge.literature"  # 医学文献
    SELF_ASSESSMENT = "self.assessment"    # 系统自我评估

class FeedbackType(Enum):
    """
    反馈类型枚举
    """
    # 形式维度
    NUMERIC = "numeric"                    # 数值型反馈
    TEXTUAL = "textual"                    # 文本型反馈
    STRUCTURED = "structured"              # 结构化反馈
    MULTIMODAL = "multimodal"              # 多模态反馈
    
    # 功能维度
    DIAGNOSTIC = "diagnostic"              # 诊断反馈
    THERAPEUTIC = "therapeutic"            # 治疗反馈
    PROGNOSTIC = "prognostic"              # 预后反馈
    ADMINISTRATIVE = "administrative"      # 管理反馈

class MetadataModel:
    """
    反馈元数据模型
    
    定义反馈的基本属性和元信息，为反馈的管理和评估提供基础。
    """
    
    def __init__(self,
                 source: Union[str, SourceType],
                 feedback_type: Union[str, FeedbackType],
                 timestamp: Optional[datetime] = None,
                 feedback_id: Optional[str] = None,
                 reliability: Optional[float] = None,
                 tags: Optional[List[str]] = None,
                 context_id: Optional[str] = None):
        """
        初始化元数据模型
        
        Args:
            source: 反馈来源，可以是SourceType枚举或字符串
            feedback_type: 反馈类型，可以是FeedbackType枚举或字符串
            timestamp: 反馈时间戳，默认为当前时间
            feedback_id: 反馈ID，默认自动生成UUID
            reliability: 反馈可靠性评分，范围[0,1]
            tags: 反馈标签列表
            context_id: 上下文ID，用于关联相关反馈
        """
        # 处理反馈来源
        if isinstance(source, SourceType):
            self.source = source
        else:
            try:
                self.source = SourceType(source)
            except ValueError:
                # 如果不是预定义的枚举值，则创建自定义来源
                self.source = source
        
        # 处理反馈类型
        if isinstance(feedback_type, FeedbackType):
            self.feedback_type = feedback_type
        else:
            try:
                self.feedback_type = FeedbackType(feedback_type)
            except ValueError:
                # 如果不是预定义的枚举值，则创建自定义类型
                self.feedback_type = feedback_type
        
        # 设置其他属性
        self.timestamp = timestamp if timestamp else datetime.now()
        self.feedback_id = feedback_id if feedback_id else str(uuid.uuid4())
        self.reliability = reliability
        self.tags = tags if tags else []
        self.context_id = context_id
    
    def calculate_reliability(self, 
                             source_weight: float = 0.4, 
                             content_weight: float = 0.3, 
                             time_weight: float = 0.2, 
                             evidence_weight: float = 0.1, 
                             source_reliability: Optional[float] = None, 
                             content_consistency: Optional[float] = None, 
                             time_relevance: Optional[float] = None, 
                             evidence_support: Optional[float] = None) -> float:
        """
        计算反馈可靠性评分
        
        Args:
            source_weight: 来源可靠性权重
            content_weight: 内容一致性权重
            time_weight: 时效性权重
            evidence_weight: 证据支持度权重
            source_reliability: 来源可靠性评分，范围[0,1]
            content_consistency: 内容一致性评分，范围[0,1]
            time_relevance: 时效性评分，范围[0,1]
            evidence_support: 证据支持度评分，范围[0,1]
            
        Returns:
            float: 综合可靠性评分，范围[0,1]
        """
        # 如果已有可靠性评分，则直接返回
        if self.reliability is not None:
            return self.reliability
        
        # 计算来源可靠性
        if source_reliability is None:
            # 根据来源类型估算可靠性
            if isinstance(self.source, SourceType):
                source_map = {
                    SourceType.HUMAN_DOCTOR: 0.9,
                    SourceType.HUMAN_NURSE: 0.8,
                    SourceType.HUMAN_PATIENT: 0.7,
                    SourceType.SYSTEM_IMAGING: 0.85,
                    SourceType.SYSTEM_LAB: 0.9,
                    SourceType.SYSTEM_EHR: 0.8,
                    SourceType.KNOWLEDGE_GRAPH: 0.85,
                    SourceType.KNOWLEDGE_LITERATURE: 0.8,
                    SourceType.SELF_ASSESSMENT: 0.6
                }
                source_reliability = source_map.get(self.source, 0.5)
            else:
                source_reliability = 0.5  # 默认值
        
        # 如果缺少其他评分，使用默认值
        content_consistency = content_consistency if content_consistency is not None else 0.7
        
        # 计算时效性评分
        if time_relevance is None:
            # 根据时间戳计算时效性，越新的反馈时效性越高
            now = datetime.now()
            time_diff = (now - self.timestamp).total_seconds() / 86400  # 转换为天数
            time_relevance = max(0, 1 - (time_diff / 365))  # 一年以内的反馈时效性从1线性降至0
        
        evidence_support = evidence_support if evidence_support is not None else 0.6
        
        # 计算综合可靠性评分
        reliability = (source_weight * source_reliability + 
                      content_weight * content_consistency + 
                      time_weight * time_relevance + 
                      evidence_weight * evidence_support)
        
        # 更新并返回可靠性评分
        self.reliability = reliability
        return reliability
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将元数据模型转换为字典表示
        
        Returns:
            Dict: 元数据的字典表示
        """
        source_value = self.source.value if isinstance(self.source, SourceType) else str(self.source)
        feedback_type_value = self.feedback_type.value if isinstance(self.feedback_type, FeedbackType) else str(self.feedback_type)
        
        return {
            'feedback_id': self.feedback_id,
            'source': source_value,
            'feedback_type': feedback_type_value,
            'timestamp': self.timestamp.isoformat(),
            'reliability': self.reliability,
            'tags': self.tags,
            'context_id': self.context_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataModel':
        """
        从字典创建元数据模型实例
        
        Args:
            data: 元数据的字典表示
            
        Returns:
            MetadataModel: 元数据模型实例
        """
        # 处理时间戳
        timestamp = datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        
        return cls(
            source=data['source'],
            feedback_type=data['feedback_type'],
            timestamp=timestamp,
            feedback_id=data.get('feedback_id'),
            reliability=data.get('reliability'),
            tags=data.get('tags'),
            context_id=data.get('context_id')
        )