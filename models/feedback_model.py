# -*- coding: utf-8 -*-
"""
反馈表示模型

该模块整合了元数据模型、内容模型和关系模型，形成完整的反馈表示框架。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import uuid
from datetime import datetime

from .metadata_model import MetadataModel
from .content_model import ContentModel, ContentType
from .relation_model import RelationModel

class FeedbackModel:
    """
    反馈表示模型
    
    整合元数据、内容和关系，形成完整的反馈表示。
    """
    
    def __init__(self,
                 metadata: MetadataModel,
                 content: ContentModel,
                 relations: Optional[List[RelationModel]] = None):
        """
        初始化反馈模型
        
        Args:
            metadata: 反馈元数据
            content: 反馈内容
            relations: 与其他反馈的关系列表
        """
        self.metadata = metadata
        self.content = content
        self.relations = relations if relations else []
        self.feedback_id = metadata.feedback_id
    
    def add_relation(self, relation: RelationModel) -> None:
        """
        添加与其他反馈的关系
        
        Args:
            relation: 关系模型实例
        """
        self.relations.append(relation)
    
    def get_reliability(self) -> float:
        """
        获取反馈可靠性评分
        
        Returns:
            float: 可靠性评分，范围[0,1]
        """
        if self.metadata.reliability is None:
            # 如果元数据中没有可靠性评分，则计算
            return self.metadata.calculate_reliability()
        return self.metadata.reliability
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将反馈模型转换为字典表示
        
        Returns:
            Dict: 反馈的字典表示
        """
        return {
            'feedback_id': self.feedback_id,
            'metadata': self.metadata.to_dict(),
            'content': self.content.to_dict(),
            'relations': [relation.to_dict() for relation in self.relations]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackModel':
        """
        从字典创建反馈模型实例
        
        Args:
            data: 反馈的字典表示
            
        Returns:
            FeedbackModel: 反馈模型实例
        """
        metadata = MetadataModel.from_dict(data['metadata'])
        content = ContentModel.from_dict(data['content'])
        
        relations = []
        if 'relations' in data:
            for relation_data in data['relations']:
                relations.append(RelationModel.from_dict(relation_data))
        
        return cls(metadata, content, relations)

class FeedbackCollection:
    """
    反馈集合
    
    管理多个反馈，支持反馈的添加、查询和分析。
    """
    
    def __init__(self):
        """
        初始化反馈集合
        """
        self.feedbacks = {}  # 反馈字典，键为反馈ID，值为反馈对象
        self.index_by_source = {}  # 按来源索引
        self.index_by_type = {}  # 按类型索引
        self.index_by_time = []  # 按时间索引，元素为(时间戳, 反馈ID)元组
    
    def add_feedback(self, feedback: FeedbackModel) -> None:
        """
        添加反馈
        
        Args:
            feedback: 反馈模型实例
        """
        self.feedbacks[feedback.feedback_id] = feedback
        
        # 更新索引
        source = feedback.metadata.source
        source_value = source.value if hasattr(source, 'value') else str(source)
        if source_value not in self.index_by_source:
            self.index_by_source[source_value] = []
        self.index_by_source[source_value].append(feedback.feedback_id)
        
        feedback_type = feedback.metadata.feedback_type
        type_value = feedback_type.value if hasattr(feedback_type, 'value') else str(feedback_type)
        if type_value not in self.index_by_type:
            self.index_by_type[type_value] = []
        self.index_by_type[type_value].append(feedback.feedback_id)
        
        self.index_by_time.append((feedback.metadata.timestamp, feedback.feedback_id))
        self.index_by_time.sort(key=lambda x: x[0])  # 按时间戳排序
    
    def get_feedback(self, feedback_id: str) -> Optional[FeedbackModel]:
        """
        获取反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Optional[FeedbackModel]: 反馈模型实例，如不存在则返回None
        """
        return self.feedbacks.get(feedback_id)
    
    def get_feedbacks_by_source(self, source: str) -> List[FeedbackModel]:
        """
        获取指定来源的所有反馈
        
        Args:
            source: 反馈来源
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        if source not in self.index_by_source:
            return []
        
        return [self.feedbacks[feedback_id] for feedback_id in self.index_by_source[source]]
    
    def get_feedbacks_by_type(self, feedback_type: str) -> List[FeedbackModel]:
        """
        获取指定类型的所有反馈
        
        Args:
            feedback_type: 反馈类型
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        if feedback_type not in self.index_by_type:
            return []
        
        return [self.feedbacks[feedback_id] for feedback_id in self.index_by_type[feedback_type]]
    
    def get_feedbacks_by_time_range(self, start_time: datetime, end_time: datetime) -> List[FeedbackModel]:
        """
        获取指定时间范围内的所有反馈
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        result = []
        for timestamp, feedback_id in self.index_by_time:
            if start_time <= timestamp <= end_time:
                result.append(self.feedbacks[feedback_id])
        return result
    
    def get_recent_feedbacks(self, count: int = 10) -> List[FeedbackModel]:
        """
        获取最近的反馈
        
        Args:
            count: 返回的反馈数量
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        if not self.index_by_time:
            return []
        
        recent_ids = [feedback_id for _, feedback_id in self.index_by_time[-count:]]
        return [self.feedbacks[feedback_id] for feedback_id in recent_ids]
    
    def filter_feedbacks(self, 
                        min_reliability: Optional[float] = None,
                        sources: Optional[List[str]] = None,
                        types: Optional[List[str]] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[FeedbackModel]:
        """
        根据多个条件筛选反馈
        
        Args:
            min_reliability: 最小可靠性评分
            sources: 反馈来源列表
            types: 反馈类型列表
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[FeedbackModel]: 符合条件的反馈模型实例列表
        """
        result = list(self.feedbacks.values())
        
        if min_reliability is not None:
            result = [f for f in result if f.get_reliability() >= min_reliability]
        
        if sources is not None:
            source_set = set(sources)
            result = [f for f in result if 
                     (hasattr(f.metadata.source, 'value') and f.metadata.source.value in source_set) or 
                     (str(f.metadata.source) in source_set)]
        
        if types is not None:
            type_set = set(types)
            result = [f for f in result if 
                     (hasattr(f.metadata.feedback_type, 'value') and f.metadata.feedback_type.value in type_set) or 
                     (str(f.metadata.feedback_type) in type_set)]
        
        if start_time is not None:
            result = [f for f in result if f.metadata.timestamp >= start_time]
        
        if end_time is not None:
            result = [f for f in result if f.metadata.timestamp <= end_time]
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将反馈集合转换为字典表示
        
        Returns:
            Dict: 反馈集合的字典表示
        """
        return {
            'feedbacks': {feedback_id: feedback.to_dict() for feedback_id, feedback in self.feedbacks.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackCollection':
        """
        从字典创建反馈集合实例
        
        Args:
            data: 反馈集合的字典表示
            
        Returns:
            FeedbackCollection: 反馈集合实例
        """
        collection = cls()
        
        for feedback_data in data['feedbacks'].values():
            feedback = FeedbackModel.from_dict(feedback_data)
            collection.add_feedback(feedback)
        
        return collection