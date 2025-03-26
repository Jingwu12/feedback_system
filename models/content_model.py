# -*- coding: utf-8 -*-
"""
反馈内容模型

该模块定义了不同类型反馈的表示方式，支持多种形式的反馈内容。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum

class ContentType(Enum):
    """
    反馈内容类型枚举
    """
    SCALAR = "scalar"           # 标量反馈，如数值型测量结果
    TEXT = "text"              # 文本反馈，如医生诊断意见
    STRUCTURED = "structured"  # 结构化反馈，如表单数据
    MULTIMODAL = "multimodal"  # 多模态反馈，如包含文本和图像的反馈

class ContentModel:
    """
    反馈内容模型基类
    
    所有具体内容模型的基类，提供通用接口。
    """
    
    def __init__(self, content_type: ContentType):
        """
        初始化内容模型
        
        Args:
            content_type: 内容类型
        """
        self.content_type = content_type
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将内容模型转换为字典表示
        
        Returns:
            Dict: 内容的字典表示
        """
        return {
            'content_type': self.content_type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentModel':
        """
        从字典创建内容模型实例
        
        Args:
            data: 内容的字典表示
            
        Returns:
            ContentModel: 内容模型实例
        """
        content_type = ContentType(data['content_type'])
        
        if content_type == ContentType.SCALAR:
            return ScalarContent.from_dict(data)
        elif content_type == ContentType.TEXT:
            return TextContent.from_dict(data)
        elif content_type == ContentType.STRUCTURED:
            return StructuredContent.from_dict(data)
        elif content_type == ContentType.MULTIMODAL:
            return MultimodalContent.from_dict(data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")

class ScalarContent(ContentModel):
    """
    标量反馈内容模型
    
    表示数值型反馈，如血压、血糖等测量结果。
    """
    
    def __init__(self, 
                 value: float, 
                 unit: str, 
                 reference_range: Optional[Tuple[float, float]] = None):
        """
        初始化标量内容模型
        
        Args:
            value: 数值
            unit: 单位，如 'mmHg', 'mg/dL'
            reference_range: 参考范围，如 (90, 120) 表示正常范围
        """
        super().__init__(ContentType.SCALAR)
        self.value = value
        self.unit = unit
        self.reference_range = reference_range
    
    def is_within_range(self) -> bool:
        """
        检查数值是否在参考范围内
        
        Returns:
            bool: 是否在参考范围内
        """
        if self.reference_range is None:
            return True  # 没有参考范围，默认为正常
        
        lower, upper = self.reference_range
        return lower <= self.value <= upper
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将标量内容模型转换为字典表示
        
        Returns:
            Dict: 标量内容的字典表示
        """
        result = super().to_dict()
        result.update({
            'value': self.value,
            'unit': self.unit,
            'reference_range': self.reference_range
        })
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScalarContent':
        """
        从字典创建标量内容模型实例
        
        Args:
            data: 标量内容的字典表示
            
        Returns:
            ScalarContent: 标量内容模型实例
        """
        return cls(
            value=data['value'],
            unit=data['unit'],
            reference_range=data.get('reference_range')
        )

class TextContent(ContentModel):
    """
    文本反馈内容模型
    
    表示文本型反馈，如医生诊断意见、患者描述等。
    """
    
    def __init__(self, 
                 text: str, 
                 language: str = 'zh-CN', 
                 sentiment: Optional[float] = None,
                 entities: Optional[List[Dict[str, Any]]] = None):
        """
        初始化文本内容模型
        
        Args:
            text: 文本内容
            language: 语言代码，默认为中文
            sentiment: 情感极性，范围 [-1,1]，负值表示消极，正值表示积极
            entities: 识别出的医学实体列表
        """
        super().__init__(ContentType.TEXT)
        self.text = text
        self.language = language
        self.sentiment = sentiment
        self.entities = entities if entities else []
    
    def add_entity(self, entity_type: str, entity_text: str, position: Tuple[int, int], confidence: float) -> None:
        """
        添加识别出的医学实体
        
        Args:
            entity_type: 实体类型，如 'disease', 'symptom', 'drug'
            entity_text: 实体文本
            position: 实体在原文中的位置，(start, end)
            confidence: 识别置信度
        """
        entity = {
            'type': entity_type,
            'text': entity_text,
            'position': position,
            'confidence': confidence
        }
        self.entities.append(entity)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将文本内容模型转换为字典表示
        
        Returns:
            Dict: 文本内容的字典表示
        """
        result = super().to_dict()
        result.update({
            'text': self.text,
            'language': self.language,
            'sentiment': self.sentiment,
            'entities': self.entities
        })
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextContent':
        """
        从字典创建文本内容模型实例
        
        Args:
            data: 文本内容的字典表示
            
        Returns:
            TextContent: 文本内容模型实例
        """
        return cls(
            text=data['text'],
            language=data.get('language', 'zh-CN'),
            sentiment=data.get('sentiment'),
            entities=data.get('entities')
        )

class StructuredContent(ContentModel):
    """
    结构化反馈内容模型
    
    表示结构化反馈，如表单数据、检查结果等。
    """
    
    def __init__(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]] = None):
        """
        初始化结构化内容模型
        
        Args:
            data: 结构化数据，键值对集合
            schema: 数据模式，描述数据结构和约束
        """
        super().__init__(ContentType.STRUCTURED)
        self.data = data
        self.schema = schema
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取指定键的值
        
        Args:
            key: 键名，支持点号分隔的嵌套键，如 'patient.demographics.age'
            default: 默认值，当键不存在时返回
            
        Returns:
            Any: 键对应的值或默认值
        """
        # 处理嵌套键
        if '.' in key:
            parts = key.split('.')
            current = self.data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        else:
            return self.data.get(key, default)
    
    def set_value(self, key: str, value: Any) -> None:
        """
        设置指定键的值
        
        Args:
            key: 键名，支持点号分隔的嵌套键
            value: 要设置的值
        """
        # 处理嵌套键
        if '.' in key:
            parts = key.split('.')
            current = self.data
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self.data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将结构化内容模型转换为字典表示
        
        Returns:
            Dict: 结构化内容的字典表示
        """
        result = super().to_dict()
        result.update({
            'data': self.data,
            'schema': self.schema
        })
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructuredContent':
        """
        从字典创建结构化内容模型实例
        
        Args:
            data: 结构化内容的字典表示
            
        Returns:
            StructuredContent: 结构化内容模型实例
        """
        return cls(
            data=data['data'],
            schema=data.get('schema')
        )

class MultimodalContent(ContentModel):
    """
    多模态反馈内容模型
    
    表示多模态反馈，如包含文本和图像的反馈。
    """
    
    def __init__(self, modalities: Dict[str, Any]):
        """
        初始化多模态内容模型
        
        Args:
            modalities: 模态内容字典，键为模态类型，值为对应内容
                例如：{'text': TextContent(...), 'image': {...}}
        """
        super().__init__(ContentType.MULTIMODAL)
        self.modalities = modalities
    
    def add_modality(self, modality_type: str, content: Any) -> None:
        """
        添加模态内容
        
        Args:
            modality_type: 模态类型，如 'text', 'image', 'audio'
            content: 模态内容
        """
        self.modalities[modality_type] = content
    
    def get_modality(self, modality_type: str) -> Optional[Any]:
        """
        获取指定模态的内容
        
        Args:
            modality_type: 模态类型
            
        Returns:
            Optional[Any]: 模态内容，如不存在则返回None
        """
        return self.modalities.get(modality_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将多模态内容模型转换为字典表示
        
        Returns:
            Dict: 多模态内容的字典表示
        """
        result = super().to_dict()
        
        # 处理不同模态的序列化
        serialized_modalities = {}
        for modality_type, content in self.modalities.items():
            if hasattr(content, 'to_dict'):
                serialized_modalities[modality_type] = content.to_dict()
            else:
                serialized_modalities[modality_type] = content
        
        result['modalities'] = serialized_modalities
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultimodalContent':
        """
        从字典创建多模态内容模型实例
        
        Args:
            data: 多模态内容的字典表示
            
        Returns:
            MultimodalContent: 多模态内容模型实例
        """
        # 处理不同模态的反序列化
        modalities = {}
        for modality_type, content in data['modalities'].items():
            if modality_type == 'text' and isinstance(content, dict) and content.get('content_type') == 'text':
                modalities[modality_type] = TextContent.from_dict(content)
            elif modality_type == 'structured' and isinstance(content, dict) and content.get('content_type') == 'structured':
                modalities[modality_type] = Struct