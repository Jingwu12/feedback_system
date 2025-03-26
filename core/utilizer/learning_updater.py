# -*- coding: utf-8 -*-
"""
学习更新模块

该模块负责基于反馈更新系统的知识和模型，实现持续学习机制。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
import json
from datetime import datetime
import numpy as np

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent

class LearningUpdater:
    """
    学习更新模块
    
    基于反馈更新系统的知识和模型，实现持续学习机制。
    """
    
    def __init__(self, knowledge_base: Dict[str, Any] = None, model_params: Dict[str, Any] = None):
        """
        初始化学习更新模块
        
        Args:
            knowledge_base: 知识库，默认为空字典
            model_params: 模型参数，默认为空字典
        """
        self.knowledge_base = knowledge_base if knowledge_base else {}
        self.model_params = model_params if model_params else {}
        self.learning_history = []
    
    def extract_knowledge(self, feedback: FeedbackModel) -> Dict[str, Any]:
        """
        从反馈中提取知识
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 提取的知识
        """
        extracted_knowledge = {}
        
        # 从文本反馈中提取知识
        if isinstance(feedback.content, TextContent):
            extracted_knowledge = self._extract_from_text(feedback.content.text)
        
        # 从结构化反馈中提取知识
        elif isinstance(feedback.content, StructuredContent):
            extracted_knowledge = self._extract_from_structured(feedback.content.data)
        
        # 记录知识提取历史
        self.learning_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'knowledge_extraction',
            'knowledge_count': len(extracted_knowledge)
        })
        
        return extracted_knowledge
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取知识
        
        Args:
            text: 文本内容
            
        Returns:
            Dict[str, Any]: 提取的知识
        """
        # 简单实现，实际应用中可以使用更复杂的知识提取方法
        # 例如，使用命名实体识别、关系抽取等NLP技术
        
        knowledge = {}
        
        # 提取关键词和概念
        import re
        
        # 提取可能的概念定义
        concept_pattern = r"([\w\s]+)是([^，。；！？]+)[，。；！？]"
        concepts = re.findall(concept_pattern, text)
        for concept, definition in concepts:
            concept = concept.strip()
            definition = definition.strip()
            if concept and definition:
                knowledge[f"concept:{concept}"] = definition
        
        # 提取可能的规则
        rule_pattern = r"如果([^，。；！？]+)，那么([^，。；！？]+)[，。；！？]"
        rules = re.findall(rule_pattern, text)
        for condition, result in rules:
            condition = condition.strip()
            result = result.strip()
            if condition and result:
                knowledge[f"rule:{condition}->{result}"] = {
                    'condition': condition,
                    'result': result
                }
        
        return knowledge
    
    def _extract_from_structured(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从结构化数据中提取知识
        
        Args:
            data: 结构化数据
            
        Returns:
            Dict[str, Any]: 提取的知识
        """
        # 直接使用结构化数据中的知识字段
        if 'knowledge' in data:
            return data['knowledge']
        
        # 如果没有显式的知识字段，尝试从其他字段提取
        knowledge = {}
        
        # 提取实体及其属性
        if 'entities' in data:
            for entity_id, entity_data in data['entities'].items():
                for attr, value in entity_data.items():
                    knowledge[f"entity:{entity_id}.{attr}"] = value
        
        # 提取关系
        if 'relations' in data:
            for relation in data['relations']:
                if 'source' in relation and 'target' in relation and 'type' in relation:
                    key = f"relation:{relation['source']}-{relation['type']}-{relation['target']}"
                    knowledge[key] = relation
        
        return knowledge
    
    def update_knowledge_base(self, new_knowledge: Dict[str, Any], confidence: float = 0.8) -> Dict[str, Any]:
        """
        更新知识库
        
        Args:
            new_knowledge: 新知识
            confidence: 知识可信度，范围[0,1]
            
        Returns:
            Dict[str, Any]: 更新后的知识库
        """
        update_count = 0
        conflict_count = 0
        
        for key, value in new_knowledge.items():
            # 检查是否存在冲突
            if key in self.knowledge_base:
                # 如果已有知识的可信度更高，则保留原知识
                existing_confidence = self.knowledge_base[key].get('confidence', 0.5) if isinstance(self.knowledge_base[key], dict) else 0.5
                
                if confidence <= existing_confidence:
                    conflict_count += 1
                    continue
            
            # 更新知识
            if isinstance(value, dict):
                value['confidence'] = confidence
                value['last_updated'] = datetime.now().isoformat()
                self.knowledge_base[key] = value
            else:
                self.knowledge_base[key] = {
                    'value': value,
                    'confidence': confidence,
                    'last_updated': datetime.now().isoformat()
                }
            
            update_count += 1
        
        # 记录知识库更新历史
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'operation': 'knowledge_base_update',
            'update_count': update_count,
            'conflict_count': conflict_count
        })
        
        return self.knowledge_base
    
    def update_model_parameters(self, feedback: FeedbackModel, learning_rate: float = 0.1) -> Dict[str, Any]:
        """
        更新模型参数
        
        Args:
            feedback: 反馈模型实例
            learning_rate: 学习率，控制参数更新的步长
            
        Returns:
            Dict[str, Any]: 更新后的模型参数
        """
        # 提取参数更新建议
        param_updates = {}
        if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
            param_updates = feedback.content.data.get('model_parameter_updates', {})
        
        update_count = 0
        
        # 更新模型参数
        for param_name, update_info in param_updates.items():
            if param_name not in self.model_params:
                self.model_params[param_name] = 0.0
            
            # 获取更新方向和大小
            if isinstance(update_info, dict):
                direction = update_info.get('direction', 0)
                magnitude = update_info.get('magnitude', 1.0)
            else:
                direction = 1 if update_info > 0 else (-1 if update_info < 0 else 0)
                magnitude = abs(update_info) if isinstance(update_info, (int, float)) else 1.0
            
            # 应用更新
            self.model_params[param_name] += direction * magnitude * learning_rate
            update_count += 1
        
        # 记录模型参数更新历史
        self.learning_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'model_parameter_update',
            'update_count': update_count,
            'learning_rate': learning_rate
        })
        
        return self.model_params
    
    def apply_feedback_to_model(self, feedback: FeedbackModel) -> Dict[str, Any]:
        """
        将反馈应用于模型更新
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        result = {
            'knowledge_extracted': False,
            'knowledge_base_updated': False,
            'model_parameters_updated': False
        }
        
        # 提取知识
        new_knowledge = self.extract_knowledge(feedback)
        if new_knowledge:
            result['knowledge_extracted'] = True
            result['extracted_knowledge'] = new_knowledge
            
            # 更新知识库
            confidence = feedback.get_reliability()
            updated_kb = self.update_knowledge_base(new_knowledge, confidence)
            result['knowledge_base_updated'] = True
            result['knowledge_base_size'] = len(updated_kb)
        
        # 更新模型参数
        updated_params = self.update_model_parameters(feedback)
        if updated_params:
            result['model_parameters_updated'] = True
            result['updated_parameters'] = list(updated_params.keys())
        
        return result