# -*- coding: utf-8 -*-
"""
执行优化模块

该模块负责基于反馈优化执行策略，实现自适应的工具选择和参数调整机制。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
import json
from datetime import datetime
import numpy as np

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel, SourceType, FeedbackType
from ...models.content_model import ContentModel, TextContent, StructuredContent

class ExecutionOptimizer:
    """
    执行优化模块
    
    基于反馈优化执行策略，实现自适应的工具选择和参数调整机制。
    """
    
    def __init__(self):
        """
        初始化执行优化模块
        """
        self.tool_performance = {}  # 工具性能记录
        self.execution_patterns = {}  # 执行模式记录
        self.optimization_history = []
    
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
        if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
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
            
            # 记录优化历史
            self.optimization_history.append({
                'feedback_id': feedback.feedback_id,
                'timestamp': datetime.now().isoformat(),
                'operation': 'tool_selection_optimization',
                'selected_tool': best_tool_id,
                'score': tool_scores[best_tool_id]
            })
            
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
        if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
            param_suggestions = feedback.content.data.get('parameter_suggestions', {})
        
        # 如果没有针对该工具的建议，则使用默认参数
        if tool_id not in param_suggestions:
            return default_params
        
        # 合并默认参数和建议参数
        optimized_params = default_params.copy()
        for param_name, suggestion in param_suggestions[tool_id].items():
            if param_name in optimized_params:
                # 根据建议类型更新参数
                if isinstance(suggestion, dict) and 'value' in suggestion:
                    optimized_params[param_name] = suggestion['value']
                else:
                    optimized_params[param_name] = suggestion
        
        # 记录优化历史
        self.optimization_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'parameter_optimization',
            'tool_id': tool_id,
            'parameters_updated': list(param_suggestions[tool_id].keys())
        })
        
        return optimized_params
    
    def learn_execution_patterns(self, execution_sequence: List[Dict[str, Any]], feedback: FeedbackModel) -> None:
        """
        学习执行模式
        
        Args:
            execution_sequence: 执行序列
            feedback: 反馈模型实例
        """
        # 提取执行序列中的工具ID序列
        tool_sequence = [step['tool_id'] for step in execution_sequence if 'tool_id' in step]
        
        # 如果序列太短，则不进行学习
        if len(tool_sequence) < 2:
            return
        
        # 提取执行模式（简单实现，使用n-gram模型）
        for n in range(2, min(4, len(tool_sequence) + 1)):
            for i in range(len(tool_sequence) - n + 1):
                pattern = tuple(tool_sequence[i:i+n])
                if pattern not in self.execution_patterns:
                    self.execution_patterns[pattern] = {
                        'count': 0,
                        'success_count': 0,
                        'feedback_ids': []
                    }
                
                self.execution_patterns[pattern]['count'] += 1
                self.execution_patterns[pattern]['feedback_ids'].append(feedback.feedback_id)
                
                # 如果反馈是积极的，增加成功计数
                if isinstance(feedback.content, StructuredContent) and isinstance(feedback.content.data, dict):
                    sentiment = feedback.content.data.get('sentiment', 0)
                    if sentiment > 0:
                        self.execution_patterns[pattern]['success_count'] += 1
        
        # 记录学习历史
        self.optimization_history.append({
            'feedback_id': feedback.feedback_id,
            'timestamp': datetime.now().isoformat(),
            'operation': 'execution_pattern_learning',
            'sequence_length': len(tool_sequence),
            'patterns_updated': len(self.execution_patterns)
        })
    
    def suggest_next_tool(self, current_sequence: List[str], available_tools: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        根据当前执行序列和学习到的模式，建议下一个工具
        
        Args:
            current_sequence: 当前执行的工具ID序列
            available_tools: 可用工具列表
            
        Returns:
            Optional[Dict[str, Any]]: 建议的下一个工具，如果没有建议则返回None
        """
        # 如果当前序列为空，则无法提供建议
        if not current_sequence:
            return None
        
        # 查找匹配的模式
        matching_patterns = {}
        for pattern, stats in self.execution_patterns.items():
            for i in range(1, len(pattern)):
                prefix = pattern[:i]
                suffix = pattern[i:]
                if tuple(current_sequence[-i:]) == prefix:
                    next_tool_id = suffix[0]
                    success_rate = stats['success_count'] / stats['count'] if stats['count'] > 0 else 0
                    
                    if next_tool_id not in matching_patterns or matching_patterns[next_tool_id]['success_rate'] < success_rate:
                        matching_patterns[next_tool_id] = {
                            'success_rate': success_rate,
                            'count': stats['count'],
                            'pattern': pattern
                        }
        
        # 如果没有匹配的模式，则无法提供建议
        if not matching_patterns:
            return None
        
        # 选择成功率最高的下一个工具
        best_next_tool_id = max(matching_patterns, key=lambda x: matching_patterns[x]['success_rate'])
        best_tool = next((tool for tool in available_tools if tool['id'] == best_next_tool_id), None)
        
        if best_tool:
            return {
                'tool': best_tool,
                'success_rate': matching_patterns[best_next_tool_id]['success_rate'],
                'pattern_count': matching_patterns[best_next_tool_id]['count'],
                'pattern': matching_patterns[best_next_tool_id]['pattern']
            }
        else:
            return None
    
    def optimize_execution(self, available_tools: List[Dict[str, Any]], context: Dict[str, Any], 
                          execution_history: List[Dict[str, Any]], feedback: FeedbackModel) -> Dict[str, Any]:
        """
        综合优化执行策略
        
        Args:
            available_tools: 可用工具列表
            context: 执行上下文
            execution_history: 执行历史
            feedback: 反馈模型实例
            
        Returns:
            Dict[str, Any]: 优化结果
        """
        result = {
            'tool_selection_optimized': False,
            'parameters_optimized': False,
            'execution_patterns_learned': False,
            'next_tool_suggested': False
        }
        
        # 优化工具选择
        tool_selection = self.optimize_tool_selection(available_tools, context, feedback)
        if tool_selection['selected_tool']:
            result['tool_selection_optimized'] = True
            result['selected_tool'] = tool_selection['selected_tool']
        
        # 优化执行参数（假设使用选定的工具）
        if tool_selection['selected_tool']:
            tool_id = tool_selection['selected_tool']['id']
            default_params = tool_selection['selected_tool'].get('default_params', {})
            optimized_params = self.optimize_execution_parameters(tool_id, default_params, feedback)
            
            if optimized_params != default_params:
                result['parameters_optimized'] = True
                result['optimized_params'] = optimized_params
        
        # 学习执行模式
        self.learn_execution_patterns(execution_history, feedback)
        result['execution_patterns_learned'] = True
        result['pattern_count'] = len(self.execution_patterns)
        
        # 提供下一步工具建议
        current_sequence = [step['tool_id'] for step in execution_history if 'tool_id' in step]
        next_tool_suggestion = self.suggest_next_tool(current_sequence, available_tools)
        
        if next_tool_suggestion:
            result['next_tool_suggested'] = True
            result['suggested_next_tool'] = next_tool_suggestion['tool']
            result['suggestion_confidence'] = next_tool_suggestion['success_rate']
        
        return result