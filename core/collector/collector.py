# -*- coding: utf-8 -*-
"""
反馈收集器

该模块负责从多种来源收集反馈信息，是反馈闭环系统的入口。
"""

from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod
import json
import requests
from datetime import datetime

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, ScalarContent, StructuredContent, MultimodalContent

class FeedbackCollector(ABC):
    """
    反馈收集器基类
    
    定义反馈收集的通用接口，所有具体收集器都应继承此类。
    """
    
    @abstractmethod
    def collect(self, **kwargs) -> List[FeedbackModel]:
        """
        收集反馈
        
        Args:
            **kwargs: 收集参数
            
        Returns:
            List[FeedbackModel]: 收集到的反馈列表
        """
        pass

class HumanFeedbackCollector(FeedbackCollector):
    """
    人类反馈收集器
    
    负责收集来自医生、患者等人类用户的反馈。
    """
    
    def __init__(self, source_type: SourceType = SourceType.HUMAN_DOCTOR):
        """
        初始化人类反馈收集器
        
        Args:
            source_type: 人类反馈来源类型，默认为医生
        """
        self.source_type = source_type
    
    def collect(self, text: str, feedback_type: FeedbackType = FeedbackType.TEXTUAL, **kwargs) -> List[FeedbackModel]:
        """
        收集人类反馈
        
        Args:
            text: 反馈文本
            feedback_type: 反馈类型
            **kwargs: 其他参数，如情感极性、标签等
            
        Returns:
            List[FeedbackModel]: 收集到的反馈列表
        """
        # 创建元数据
        metadata = MetadataModel(
            source=self.source_type,
            feedback_type=feedback_type,
            timestamp=kwargs.get('timestamp', datetime.now()),
            tags=kwargs.get('tags', [])
        )
        
        # 创建内容
        content = TextContent(
            text=text,
            language=kwargs.get('language', 'zh-CN'),
            sentiment=kwargs.get('sentiment')
        )
        
        # 创建反馈模型
        feedback = FeedbackModel(metadata, content)
        
        return [feedback]

class ToolFeedbackCollector(FeedbackCollector):
    """
    工具反馈收集器
    
    负责收集来自医学影像分析系统、临床决策支持系统等外部工具的反馈。
    """
    
    def __init__(self, tool_name: str, source_type: SourceType = SourceType.SYSTEM_IMAGING):
        """
        初始化工具反馈收集器
        
        Args:
            tool_name: 工具名称
            source_type: 工具反馈来源类型
        """
        self.tool_name = tool_name
        self.source_type = source_type
    
    def collect(self, data: Dict[str, Any], feedback_type: FeedbackType = FeedbackType.STRUCTURED, **kwargs) -> List[FeedbackModel]:
        """
        收集工具反馈
        
        Args:
            data: 工具反馈数据
            feedback_type: 反馈类型
            **kwargs: 其他参数
            
        Returns:
            List[FeedbackModel]: 收集到的反馈列表
        """
        # 创建元数据
        metadata = MetadataModel(
            source=self.source_type,
            feedback_type=feedback_type,
            timestamp=kwargs.get('timestamp', datetime.now()),
            tags=[self.tool_name] + kwargs.get('tags', [])
        )
        
        # 创建内容
        content = StructuredContent(
            data=data,
            schema=kwargs.get('schema')
        )
        
        # 创建反馈模型
        feedback = FeedbackModel(metadata, content)
        
        return [feedback]

class KnowledgeFeedbackCollector(FeedbackCollector):
    """
    知识反馈收集器
    
    负责收集来自医学知识图谱、文献库等知识源的反馈。
    """
    
    def __init__(self, knowledge_source: str, source_type: SourceType = SourceType.KNOWLEDGE_GRAPH):
        """
        初始化知识反馈收集器
        
        Args:
            knowledge_source: 知识源名称
            source_type: 知识反馈来源类型
        """
        self.knowledge_source = knowledge_source
        self.source_type = source_type
    
    def collect(self, query: str, results: List[Dict[str, Any]], feedback_type: FeedbackType = FeedbackType.TEXTUAL, **kwargs) -> List[FeedbackModel]:
        """
        收集知识反馈
        
        Args:
            query: 查询内容
            results: 查询结果列表
            feedback_type: 反馈类型
            **kwargs: 其他参数
            
        Returns:
            List[FeedbackModel]: 收集到的反馈列表
        """
        feedbacks = []
        
        for result in results:
            # 创建元数据
            metadata = MetadataModel(
                source=self.source_type,
                feedback_type=feedback_type,
                timestamp=kwargs.get('timestamp', datetime.now()),
                tags=[self.knowledge_source, query] + kwargs.get('tags', [])
            )
            
            # 根据结果类型创建不同的内容模型
            if isinstance(result.get('content'), str):
                content = TextContent(
                    text=result['content'],
                    language=result.get('language', 'zh-CN')
                )
            else:
                content = StructuredContent(
                    data=result,
                    schema=kwargs.get('schema')
                )
            
            # 创建反馈模型
            feedback = FeedbackModel(metadata, content)
            feedbacks.append(feedback)
        
        return feedbacks

class SelfFeedbackCollector(FeedbackCollector):
    """
    自我反馈收集器
    
    负责收集系统自身生成的反馈。
    """
    
    def __init__(self):
        """
        初始化自我反馈收集器
        """
        self.source_type = SourceType.SELF_ASSESSMENT
    
    def collect(self, assessment_type: str, assessment_result: Any, confidence: float, feedback_type: FeedbackType = FeedbackType.STRUCTURED, **kwargs) -> List[FeedbackModel]:
        """
        收集自我反馈
        
        Args:
            assessment_type: 评估类型，如'consistency_check', 'self_critique'
            assessment_result: 评估结果
            confidence: 评估置信度
            feedback_type: 反馈类型
            **kwargs: 其他参数
            
        Returns:
            List[FeedbackModel]: 收集到的反馈列表
        """
        # 创建元数据
        metadata = MetadataModel(
            source=self.source_type,
            feedback_type=feedback_type,
            timestamp=kwargs.get('timestamp', datetime.now()),
            tags=[assessment_type] + kwargs.get('tags', [])
        )
        
        # 创建内容
        data = {
            'assessment_type': assessment_type,
            'assessment_result': assessment_result,
            'confidence': confidence
        }
        content = StructuredContent(data=data)
        
        # 创建反馈模型
        feedback = FeedbackModel(metadata, content)
        
        return [feedback]

class FeedbackCollectorRegistry:
    """
    反馈收集器注册表
    
    管理和注册各种反馈收集器。
    """
    
    def __init__(self):
        """
        初始化注册表
        """
        self.collectors = {}
    
    def register(self, name: str, collector: FeedbackCollector) -> None:
        """
        注册收集器
        
        Args:
            name: 收集器名称
            collector: 收集器实例
        """
        self.collectors[name] = collector
    
    def get(self, name: str) -> Optional[FeedbackCollector]:
        """
        获取收集器
        
        Args:
            name: 收集器名称
            
        Returns:
            Optional[FeedbackCollector]: 收集器实例，如不存在则返回None
        """
        return self.collectors.get(name)
    
    def collect_all(self, **kwargs) -> List[FeedbackModel]:
        """
        使用所有注册的收集器收集反馈
        
        Args:
            **kwargs: 收集参数
            
        Returns:
            List[FeedbackModel]: 收集到的反馈列表
        """
        all_feedbacks = []
        
        for collector in self.collectors.values():
            try:
                feedbacks = collector.collect(**kwargs)
                all_feedbacks.extend(feedbacks)
            except Exception as e:
                print(f"Error collecting feedback: {e}")
        
        return all_feedbacks