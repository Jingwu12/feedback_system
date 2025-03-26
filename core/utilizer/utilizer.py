# -*- coding: utf-8 -*-
"""
反馈利用器

该模块负责将融合后的反馈信息应用于系统的不同环节，指导系统的行为调整。
"""

from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod
import json
from datetime import datetime

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent

class FeedbackUtilizer(ABC):
    """
    反馈利用器基类
    
    定义反馈利用的通用接口，所有具体利用器都应继承此类。
    """
    
    @abstractmethod
    def utilize(self, feedback: FeedbackModel) -> Dict[str, Any]:
        """
        利用反馈
        
        Args:
            feedback: 融合后的反馈
            
        Returns:
            Dict[str, Any]: 利用结果
        """
        pass

class PlanningAdjuster(FeedbackUtilizer):
    """
    规划调整器
    
    基于反馈调整任务规划，实现反馈驱动的规划优化。
    """
    
    def __init__(self):
        """
        初始化规划调整器
        """
        self.error_patterns = {
            "concept_error": r"诊断路径(错误|不当|不正确)",
            "operation_error": r"(检查|操作)顺序(不合理|错误)",
            "resource_error": r"(工具|资源)(选择|分配)(不当|错误)"
        }
    
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
        if hasattr(feedback.content, 'text'):
            text = feedback.content.text
            import re
            
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
        if hasattr(feedback.content, 'data'):
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
        if hasattr(feedback.content, 'data') and isinstance(feedback.content.data, dict):
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
        if hasattr(feedback.metadata.feedback_type, 'value'):
            feedback_type = feedback.metadata.feedback_type.value
            task_type = task.get('type', '')
            
            if feedback_type in task_type or task_type in feedback_type:
                relevance += 0.3
        
        # 检查任务标签与反馈标签的重叠度
        task_tags = set(task.get('tags', []))
        feedback_tags = set(feedback.metadata.tags)
        overlap = len(task_tags.intersection(feedback_tags))
        if task_tags and feedback_tags:
            relevance += 0.2 * (overlap / len(task_tags.union(feedback_tags)))
        
        
        return min(1.0, relevance)
    
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
        if hasattr(feedback.content, 'data') and isinstance(feedback.content.data, dict):
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
        
        return new_allocation
    
    def utilize(self, feedback: FeedbackModel) -> Dict[str, Any]:
        """
        利用反馈调整任务规划
        
        Args:
            feedback: 融合后的反馈
            
        Returns:
            Dict[str, Any]: 调整结果
        """
        result = {
            'planning_errors': self.detect_planning_errors(feedback),
            'priority_adjusted': False,
            'resources_reallocated': False
        }
        
        # 模拟任务列表和资源分配
        # 实际应用中，这些数据应该从规划系统获取
        task_list = [
            {'id': 'task1', 'type': 'diagnostic', 'priority': 0.7, 'tags': ['urgent', 'cardiac']},
            {'id': 'task2', 'type': 'therapeutic', 'priority': 0.5, 'tags': ['routine', 'medication']},
            {'id': 'task3', 'type': 'monitoring', 'priority': 0.3, 'tags': ['continuous', 'vital_signs']}
        ]
        
        resource_allocation = {
            'task1': ['doctor1', 'device2'],
            'task2': ['nurse1', 'medication3'],
            'task3': ['monitor1']
        }
        
        # 调整任务优先级
        adjusted_tasks = self.adjust_task_priority(task_list, feedback)
        if adjusted_tasks != task_list:
            result['priority_adjusted'] = True
            result['adjusted_tasks'] = adjusted_tasks
        
        # 重新分配资源
        new_allocation = self.reallocate_resources(resource_allocation, feedback)
        if new_allocation != resource_allocation:
            result['resources_reallocated'] = True
            result['new_allocation'] = new_allocation
        
        return result

class ExecutionOptimizer(FeedbackUtilizer):
    """
    执行优化器
    
    基于反馈优化执行策略，实现反馈增强的执行优化。
    """
    
    def __init__(self):
        """
        初始化执行优化器
        """
        self.tool_performance = {}  # 工具性能记录
        self.execution_patterns = {}  # 执行模式记录
    
    def optimize_tool_selection(self, available_tools: List[Dict[str, Any]], context: Dict[str, Any], feedback: FeedbackModel) -> Dict[str, Any]:
        """
        优化工具选择
        
        Args:
            available_tools: 可用工具列表
            context: 执行上下文
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 工具选择结果
        """
        # 更新工具性能记录
        if hasattr(feedback.content, 'data') and isinstance(feedback.content.data, dict):
            tool_feedback = feedback.content.data.get('tool_performance', {})
            for tool_id, performance in tool_feedback.items():
                if tool_id not in self.tool_performance:
                    self.tool_performance[tool_id] = []
                self.tool_performance[tool_id].append({
                    'performance': performance,
                    'context': context,
                    'timestamp': datetime.now().isoformat(),
                    'feedback_id': feedback.feedback_id
                })
        
        # 计算每个工具的性能得分
        tool_scores = {}
        for tool in available_tools:
            tool_id = tool['id']
            
            # 如果有历史性能记录，计算加权平均分
            if tool_id in self.tool_performance and self.tool_performance[tool_id]:
                performances = [record['performance'] for record in self.tool_performance[tool_id]]
                # 最近的性能记录权重更高
                weights = [0.5 ** i for i in range(len(performances))]
                weighted_sum = sum(p * w for p, w in zip(performances, weights))
                weight_sum = sum(weights)
                avg_performance = weighted_sum / weight_sum
                
                # 考虑上下文相似度
                context_similarity = self._calculate_context_similarity(context, self.tool_performance[tool_id])
                
                # 计算最终得分
                tool_scores[tool_id] = avg_performance * (0.7 + 0.3 * context_similarity)
            else:
                # 没有历史记录，使用默认得分
                tool_scores[tool_id] = 0.5
        
        # 选择得分最高的工具
        if tool_scores:
            best_tool_id = max(tool_scores, key=tool_scores.get)
            best_tool = next((tool for tool in available_tools if tool['id'] == best_tool_id), None)
            
            return {
                'selected_tool': best_tool,
                'score': tool_scores[best_tool_id],
                'alternatives': sorted([
                    {'tool': tool, 'score': tool_scores[tool['id']]}
                    for tool in available_tools if tool['id'] != best_tool_id
                ], key=lambda x: x['score'], reverse=True)
            }
        else:
            return {'selected_tool': None, 'score': 0.0, 'alternatives': []}
    
    def _calculate_context_similarity(self, context: Dict[str, Any], performance_records: List[Dict[str, Any]]) -> float:
        """
        计算上下文相似度
        
        Args:
            context: 当前上下文
            performance_records: 性能记录列表
            
        Returns:
            float: 相似度得分，范围[0,1]
        """
        # 简单实现，实际应用中可以使用更复杂的相似度计算方法
        # 例如，使用向量空间模型、余弦相似度等
        
        if not performance_records:
            return 0.0
        
        # 计算上下文特征的重叠度
        similarities = []
        for record in performance_records:
            record_context = record.get('context', {})
            
            # 计算键的重叠度
            context_keys = set(context.keys())
            record_keys = set(record_context.keys())
            key_overlap = len(context_keys.intersection(record_keys)) / len(context_keys.union(record_keys)) if context_keys or record_keys else 0.0
            
            # 计算值的相似度（简化版，只考虑字符串值）
            value_similarity = 0.0
            common_keys = context_keys.intersection(record_keys)
            if common_keys:
                value_matches = sum(1 for k in common_keys if str(context.get(k)) == str(record_context.get(k)))
                value_similarity = value_matches / len(common_keys)
            
            # 综合相似度
            similarity = 0.5 * key_overlap + 0.5 * value_similarity
            similarities.append(similarity)
        
        # 返回最大相似度
        return max(similarities) if similarities else 0.0
    
    def optimize_execution_parameters(self, tool_id: str, default_params: Dict[str, Any], feedback: FeedbackModel) -> Dict[str, Any]:
        """
        优化执行参数
        
        Args:
            tool_id: 工具ID
            default_params: 默认参数
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 优化后的参数
        """
        # 提取参数优化建议
        param_suggestions = {}
        if hasattr(feedback.content, 'data') and isinstance(feedback.content.data, dict):
            param_suggestions = feedback.content.data.get('parameter_suggestions', {})
        
        # 如果没有针对该工具的建议，则使用默认参数
        if tool_id not in param_suggestions:
            return default_params
        
        # 合并默认参数和建议参数
        optimized_params = default_params.copy()
        for param, value in param_suggestions[tool_id].items():
            if param in optimized_params:
                # 根据反馈可靠性决定是否采纳建议
                reliability = feedback.get_reliability()
                if reliability > 0.7:  # 只有当可靠性较高时才采纳建议
                    optimized_params[param] = value
        
        return optimized_params
    
    def learn_execution_patterns(self, execution_history: List[Dict[str, Any]], feedback: FeedbackModel) -> Dict[str, Any]:
        """
        学习执行模式
        
        Args:
            execution_history: 执行历史记录
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 学习结果
        """
        # 提取成功/失败标记
        success = False
        if hasattr(feedback.content, 'data') and isinstance(feedback.content.data, dict):
            success = feedback.content.data.get('execution_success', False)
        
        # 如果执行历史为空，则无法学习模式
        if not execution_history:
            return {'patterns_learned': False}
        
        # 提取执行序列
        sequence = []
        for step in execution_history:
            sequence.append({
                'tool_id': step.get('tool_id'),
                'params': step.get('params'),
                'context': step.get('context')
            })
        
        # 生成模式标识符
        import hashlib
        sequence_str = json.dumps(sequence, sort_keys=True)
        pattern_id = hashlib.md5(sequence_str.encode()).hexdigest()
        
        # 更新执行模式记录
        if pattern_id not in self.execution_patterns:
            self.execution_patterns[pattern_id] = {
                'sequence': sequence,
                'success_count': 0,
                'failure_count': 0,
                'feedback_ids': []
            }
        
        # 更新成功/失败计数
        if success:
            self.execution_patterns[pattern_id]['success_count'] += 1
        else:
            self.execution_patterns[pattern_id]['failure_count'] += 1
        
        # 记录反馈ID
        self.execution_patterns[pattern_id]['feedback_ids'].append(feedback.feedback_id)
        
        return {
            'patterns_learned': True,
            'pattern_id': pattern_id,
            'success_rate': self.execution_patterns[pattern_id]['success_count'] / 
                          (self.execution_patterns[pattern_id]['success_count'] + 
                           self.execution_patterns[pattern_id]['failure_count'])
        }
    
    def utilize(self, feedback: FeedbackModel) -> Dict[str, Any]:
        """
        利用反馈优化执行策略
        
        Args:
            feedback: 融合后的反馈
            
        Returns:
            Dict[str, Any]: 优化结果
        """
        result = {
            'tool_selection_optimized': False,
            'parameters_optimized': False,
            'patterns_learned': False
        }
        
        # 模拟可用工具和执行上下文
        # 实际应用中，这些数据应该从执行系统获取
        available_tools = [
            {'id': 'tool1', 'name': 'Blood Pressure Monitor', 'type': 'diagnostic'},
            {'id': 'tool2', 'name': 'ECG Analyzer', 'type': 'diagnostic'},
            {'id': 'tool3', 'name': 'Medication Dispenser', 'type': 'therapeutic'}
        ]
        
        context = {
            'patient_id': '12345',
            'task_type': 'diagnostic',
            'urgency': 'high',
            'location': 'emergency_room'
        }
        
        default_params = {
            'sensitivity': 0.8,
            'specificity': 0.9,
            'timeout': 30
        }
        
        execution_history = [
            {'tool_id': 'tool1', 'params': {'sensitivity': 0.7}, 'context': {'urgency': 'high'}},
            {'tool_id': 'tool2', 'params': {'timeout': 20}, 'context': {'urgency': 'high'}}
        ]
        
        # 优化工具选择
        tool_selection = self.optimize_tool_selection(available_tools, context, feedback)
        if tool_selection['selected_tool']:
            result['tool_selection_optimized'] = True
            result['selected_tool'] = tool_selection['selected_tool']
            result['tool_score'] = tool_selection['score']
        
        # 优化执行参数
        if tool_selection['selected_tool']:
            tool_id = tool_selection['selected_tool']['id']
            optimized_params = self.optimize_execution_parameters(tool_id, default_params, feedback)
            if optimized_params != default_params:
                result['parameters_optimized'] = True
                result['optimized_params'] = optimized_params
        
        # 学习执行模式
        pattern_result = self.learn_execution_patterns(execution_history, feedback)
        if pattern_result['patterns_learned']:
            result['patterns_learned'] = True
            result['pattern_id'] = pattern_result['pattern_id']
            result['success_rate'] = pattern_result['success_rate']
        
        return result

class KnowledgeUpdater(FeedbackUtilizer):
    """
    知识更新器
    
    基于反馈更新系统的知识和模型，实现反馈驱动的知识更新。
    """
    
    def __init__(self):
        """
        初始化知识更新器
        """
        self.knowledge_base = {}  # 知识库
        self.update_history = []  # 更新历史
    
    def extract_knowledge(self, feedback: FeedbackModel) -> List[Dict[str, Any]]:
        """
        从反馈中提取知识
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            List[Dict[str, Any]]: 提取的知识列表
        """
        knowledge_items = []
        
        # 从文本反馈中提取知识
        if hasattr(feedback.content, 'text'):
            text = feedback.content.text
            
            # 提取医学实体和关系（简化版）
            # 实际应用中可以使用更复杂的信息提取方法，如命名实体识别、关系抽取等
            import re
            
            # 简单的医学实体模式
            entity_patterns = {
                'disease': r'(高血压|糖尿病|冠心病|肺炎|哮喘|癌症|抑郁症)',
                'symptom': r'(头痛|发热|咳嗽|胸痛|呕吐|腹泻|乏力)',
                'drug': r'(阿司匹林|布洛芬|青霉素|胰岛素|华法林|他汀类药物)'
            }
            
            # 简单的关系模式
            relation_patterns = {
                'treats': r'(治疗|缓解|改善)',
                'causes': r'(导致|引起|诱发)',
                'diagnoses': r'(诊断|检查|评估)'
            }
            
            # 提取实体
            entities = []
            for entity_type, pattern in entity_patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    entities.append({
                        'type': entity_type,
                        'text': match.group(),
                        'position': match.span()
                    })
            
            # 简单的关系提取（基于实体共现和关系词）
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities):
                    if i == j:
                        continue
                    
                    # 检查两个实体之间的文本
                    start = min(entity1['position'][1], entity2['position'][1])
                    end = max(entity1['position'][0], entity2['position'][0])
                    if start < end:
                        between_text = text[start:end]
                        
                        # 检查关系模式
                        for relation_type, pattern in relation_patterns.items():
                            if re.search(pattern, between_text):
                                knowledge_items.append({
                                    'subject': entity1['text'],
                                    'subject_type': entity1['type'],
                                    'relation': relation_type,
                                    'object': entity2['text'],
                                    'object_type': entity2['type'],
                                    'confidence': 0.7,  # 简单实现，可以根据匹配度等因素计算置信度
                                    'source': 'text_extraction',
                                    'feedback_id': feedback.feedback_id
                                })
        
        # 从结构化反馈中提取知识
        if hasattr(feedback.content, 'data') and isinstance(feedback.content.data, dict):
            knowledge_data = feedback.content.data.get('knowledge_items', [])
            for item in knowledge_data:
                item['feedback_id'] = feedback.feedback_id
                knowledge_items.append(item)
        
        return knowledge_items
    
    def validate_knowledge(self, knowledge_items: List[Dict[str, Any]], feedback: FeedbackModel) -> List[Dict[str, Any]]:
        """
        验证提取的知识
        
        Args:
            knowledge_items: 提取的知识列表
            feedback: 反馈模型实例
            
        Returns:
            List[Dict[str, Any]]: 验证后的知识列表
        """
        validated_items = []
        
        for item in knowledge_items:
            # 检查知识项的完整性
            if not all(k in item for k in ['subject', 'relation', 'object']):
                continue
            
            # 根据反馈可靠性调整知识置信度
            reliability = feedback.get_reliability()
            item['confidence'] = item.get('confidence', 0.5) * reliability
            
            # 只保留置信度超过阈值的知识
            if item['confidence'] >= 0.5:
                validated_items.append(item)
        
        return validated_items
    
    def update_knowledge_base(self, validated_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        更新知识库
        
        Args:
            validated_items: 验证后的知识列表
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        update_count = 0
        new_count = 0
        conflict_count = 0
        
        for item in validated_items:
            # 生成知识项的唯一标识符
            key = f"{item['subject']}_{item['relation']}_{item['object']}"
            
            if key in self.knowledge_base:
                # 更新已有知识
                existing_item = self.knowledge_base[key]
                
                # 检查是否存在冲突
                if existing_item['confidence'] > item['confidence']:
                    # 现有知识的置信度更