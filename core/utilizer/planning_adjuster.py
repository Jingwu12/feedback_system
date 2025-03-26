# -*- coding: utf-8 -*-
"""
规划调整模块

该模块负责基于反馈调整任务规划，实现反馈驱动的规划优化机制。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
import json
from datetime import datetime
import re

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent

class PlanningAdjuster:
    """
    规划调整模块
    
    基于反馈调整任务规划，实现反馈驱动的规划优化机制。
    """
    
    def __init__(self):
        """
        初始化规划调整模块
        """
        self.error_patterns = {
            "concept_error": r"诊断路径(错误|不当|不正确)",
            "operation_error": r"(检查|操作)顺序(不合理|错误)",
            "resource_error": r"(工具|资源)(选择|分配)(不当|错误)"
        }
        self.adjustment_history = []
    
    def detect_planning_errors(self, feedback: FeedbackModel) -> List[Dict[str, Any]]:
        """
        检测规划中的潜在错误
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            List[Dict[str, Any]]: 检测到的错误列表
        """
        errors = []
        
        # 检查文本反馈中的错误模式
        if isinstance(feedback.content, TextContent):
            text = feedback.content.text
            
            for error_type, pattern in self.error_patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    errors.append({
                        'type': error_type,
                        'position': match.span(),
                        'text': match.group(),
                        'confidence': 0.8  # 简单实现，可以根据匹配度等因素计算置信度
                    })
        
        # 检查结构化反馈中的错误标记
        elif isinstance(feedback.content, StructuredContent):
            data = feedback.content.data
            if isinstance(data, dict) and 'planning_errors' in data:
                errors.extend(data['planning_errors'])
        
        return errors
    
    def adjust_task_priority(self, task_list: List[Dict[str, Any]], feedback: FeedbackModel) -> List[Dict[str, Any]]:
        """
        根据反馈调整任务优先级
        
        Args:
            task_list: 任务列表
            feedback: 反馈模型实例
            
        Returns:
            List[Dict[str, Any]]: 调整后的任务列表
        """
        # 提取反馈中的紧急程度信息
        urgency = 0.0
        if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
            urgency = feedback.content.data.get('urgency', 0.0)
        
        # 根据反馈可靠性和紧急程度计算优先级调整因子
        adjustment_factor = feedback.get_reliability() * urgency
        
        # 调整任务优先级
        for task in task_list:
            # 根据任务类型和反馈内容计算相关性
            relevance = self._calculate_task_relevance(task, feedback)
            
            # 更新优先级
            original_priority = task.get('priority', 0.5)
            task['priority'] = min(1.0, original_priority + adjustment_factor * relevance)
            
            # 记录调整原因
            if 'adjustments' not in task:
                task['adjustments'] = []
            task['adjustments'].append({
                'feedback_id': feedback.feedback_id,
                'original_priority': original_priority,
                'new_priority': task['priority'],
                'adjustment_factor': adjustment_factor,
                'relevance': relevance,
                'timestamp': datetime.now().isoformat()
            })
        
        # 记录调整历史
        self.adjustment_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'task_priority_adjustment',
            'tasks_adjusted': len(task_list)
        })
        
        # 根据优先级重新排序任务列表
        return sorted(task_list, key=lambda x: x.get('priority', 0.0), reverse=True)
    
    def _calculate_task_relevance(self, task: Dict[str, Any], feedback: FeedbackModel) -> float:
        """
        计算任务与反馈的相关性
        
        Args:
            task: 任务信息
            feedback: 反馈模型实例
            
        Returns:
            float: 相关性得分，范围[0,1]
        """
        # 简单实现，实际应用中可以使用更复杂的相关性计算方法
        # 例如，使用文本相似度、知识图谱关联度等
        relevance = 0.5  # 默认中等相关性
        
        # 检查任务类型与反馈类型的匹配度
        if hasattr(feedback.metadata, 'feedback_type') and hasattr(feedback.metadata.feedback_type, 'value'):
            feedback_type = feedback.metadata.feedback_type.value
            task_type = task.get('type', '')
            
            if feedback_type in task_type or task_type in feedback_type:
                relevance += 0.3
        
        # 检查任务标签与反馈标签的重叠度
        task_tags = set(task.get('tags', []))
        feedback_tags = set(feedback.metadata.tags) if hasattr(feedback.metadata, 'tags') else set()
        overlap = len(task_tags.intersection(feedback_tags))
        if task_tags and feedback_tags:
            relevance += 0.2 * (overlap / len(task_tags.union(feedback_tags)))
        
        return min(1.0, relevance)
    
    def adjust_task_sequence(self, task_sequence: List[Dict[str, Any]], feedback: FeedbackModel) -> List[Dict[str, Any]]:
        """
        根据反馈调整任务执行顺序
        
        Args:
            task_sequence: 任务序列
            feedback: 反馈模型实例
            
        Returns:
            List[Dict[str, Any]]: 调整后的任务序列
        """
        # 提取顺序调整建议
        sequence_suggestions = {}
        if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
            sequence_suggestions = feedback.content.data.get('sequence_suggestions', {})
        
        # 如果没有顺序调整建议，则不进行调整
        if not sequence_suggestions:
            return task_sequence
        
        # 创建任务ID到索引的映射
        task_id_to_index = {task.get('id'): i for i, task in enumerate(task_sequence)}
        
        # 应用顺序调整建议
        for before_id, after_ids in sequence_suggestions.items():
            if before_id not in task_id_to_index:
                continue
                
            before_index = task_id_to_index[before_id]
            
            for after_id in after_ids:
                if after_id not in task_id_to_index:
                    continue
                    
                after_index = task_id_to_index[after_id]
                
                # 如果顺序已经正确，则跳过
                if before_index < after_index:
                    continue
                
                # 调整顺序
                task = task_sequence.pop(after_index)
                task_sequence.insert(before_index, task)
                
                # 更新索引映射
                task_id_to_index = {task.get('id'): i for i, task in enumerate(task_sequence)}
        
        # 记录调整历史
        self.adjustment_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'task_sequence_adjustment',
            'sequence_suggestions': sequence_suggestions
        })
        
        return task_sequence
    
    def reallocate_resources(self, resource_allocation: Dict[str, List[str]], feedback: FeedbackModel) -> Dict[str, List[str]]:
        """
        根据反馈重新分配资源
        
        Args:
            resource_allocation: 资源分配方案，键为任务ID，值为分配的资源ID列表
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, List[str]]: 调整后的资源分配方案
        """
        # 提取反馈中的资源效用信息
        resource_utility = {}
        if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
            resource_utility = feedback.content.data.get('resource_utility', {})
        
        # 如果没有资源效用信息，则不进行调整
        if not resource_utility:
            return resource_allocation
        
        # 计算资源-任务匹配矩阵
        tasks = list(resource_allocation.keys())
        resources = set()
        for res_list in resource_allocation.values():
            resources.update(res_list)
        resources = list(resources)
        
        # 构建效用矩阵
        utility_matrix = []
        for task in tasks:
            row = []
            for resource in resources:
                # 获取资源对任务的效用
                utility = resource_utility.get(f"{resource}_{task}", 0.5)
                row.append(utility)
            utility_matrix.append(row)
        
        # 使用匈牙利算法求解最优分配（简化版）
        # 实际应用中可以使用更复杂的算法，如考虑多资源分配等
        new_allocation = {}
        for i, task in enumerate(tasks):
            # 选择效用最高的资源
            if utility_matrix[i]:
                best_resource_idx = utility_matrix[i].index(max(utility_matrix[i]))
                new_allocation[task] = [resources[best_resource_idx]]
            else:
                new_allocation[task] = []
        
        # 记录调整历史
        self.adjustment_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'resource_reallocation',
            'tasks_affected': len(tasks)
        })
        
        return new_allocation
    
    def adjust_planning(self, task_list: List[Dict[str, Any]], task_sequence: List[Dict[str, Any]], 
                       resource_allocation: Dict[str, List[str]], feedback: FeedbackModel) -> Dict[str, Any]:
        """
        综合调整任务规划
        
        Args:
            task_list: 任务列表
            task_sequence: 任务序列
            resource_allocation: 资源分配方案
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 调整结果
        """
        result = {
            'planning_errors': self.detect_planning_errors(feedback),
            'priority_adjusted': False,
            'sequence_adjusted': False,
            'resources_reallocated': False
        }
        
        # 调整任务优先级
        adjusted_tasks = self.adjust_task_priority(task_list, feedback)
        if adjusted_tasks != task_list:
            result['priority_adjusted'] = True
            result['adjusted_tasks'] = adjusted_tasks
        
        # 调整任务顺序
        adjusted_sequence = self.adjust_task_sequence(task_sequence, feedback)
        if adjusted_sequence != task_sequence:
            result['sequence_adjusted'] = True
            result['adjusted_sequence'] = adjusted_sequence
        
        # 重新分配资源
        new_allocation = self.reallocate_resources(resource_allocation, feedback)
        if new_allocation != resource_allocation:
            result['resources_reallocated'] = True
            result['new_allocation'] = new_allocation
        
        return result