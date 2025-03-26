# -*- coding: utf-8 -*-
"""
大语言模型适配器

该模块实现了连接大语言模型反馈源的适配器，用于从LLM中获取反馈数据。
大语言模型是医疗复杂任务规划与执行系统中重要的反馈来源之一。
"""

from typing import Any, Dict, List, Optional, Union
import json
import logging
import time

from .base_adapter import BaseAdapter

class LLMAdapter(BaseAdapter):
    """
    大语言模型适配器，用于连接LLM反馈源。
    
    该适配器实现了从大语言模型中获取反馈数据的功能，支持多种查询方式，
    包括直接查询、自我批评和一致性检验等。
    """
    
    def __init__(self, logger=None):
        """
        初始化大语言模型适配器
        
        Args:
            logger: 日志记录器，如果为None则创建新的日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.connection = None
        self.llm_endpoint = None
        self.api_key = None
        self.model_name = None
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到大语言模型服务
        
        Args:
            config: 连接配置，包含LLM的访问地址、认证信息等
                - endpoint: LLM API端点
                - api_key: API密钥
                - model_name: 模型名称
                - timeout: 连接超时时间（秒）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            self.llm_endpoint = config.get('endpoint')
            self.api_key = config.get('api_key')
            self.model_name = config.get('model_name')
            timeout = config.get('timeout', 30)
            
            # 这里实现具体的连接逻辑，例如验证API密钥
            if not self.llm_endpoint or not self.api_key:
                self.logger.error("LLM端点或API密钥未指定")
                return False
                
            self.logger.info(f"成功连接到LLM服务: {self.llm_endpoint}, 模型: {self.model_name}")
            self.connection = True
            return True
        except Exception as e:
            self.logger.error(f"连接LLM服务失败: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开与LLM服务的连接
        
        Returns:
            bool: 断开连接是否成功
        """
        try:
            # 关闭连接的逻辑
            self.connection = None
            self.logger.info("已断开与LLM服务的连接")
            return True
        except Exception as e:
            self.logger.error(f"断开LLM服务连接失败: {str(e)}")
            return False
    
    def get_feedback(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从LLM获取反馈数据
        
        Args:
            query: 查询参数，指定要获取的反馈类型和条件
                - query_type: 查询类型，如'direct', 'self_critique', 'consistency_check'
                - prompt: 提示文本
                - temperature: 采样温度
                - max_tokens: 最大生成令牌数
            
        Returns:
            List[Dict[str, Any]]: 反馈数据列表，每个反馈表示为一个字典
        """
        if not self.connection:
            self.logger.error("未连接到LLM服务，无法获取反馈")
            return []
        
        try:
            query_type = query.get('query_type', 'direct')
            
            # 根据查询类型执行不同的查询逻辑
            if query_type == 'direct':
                return self._direct_query(query)
            elif query_type == 'self_critique':
                return self._self_critique_query(query)
            elif query_type == 'consistency_check':
                return self._consistency_check_query(query)
            else:
                self.logger.warning(f"不支持的查询类型: {query_type}")
                return []
        except Exception as e:
            self.logger.error(f"从LLM获取反馈失败: {str(e)}")
            return []
    
    def _direct_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        直接查询LLM
        
        Args:
            query: 查询参数
            
        Returns:
            List[Dict[str, Any]]: LLM反馈数据列表
        """
        prompt = query.get('prompt', '')
        temperature = query.get('temperature', 0.7)
        max_tokens = query.get('max_tokens', 1000)
        
        # 模拟LLM调用
        response = f"这是LLM对'{prompt}'的回答。这是一个模拟的响应，实际应用中应调用真实的LLM API。"
        
        return [{
            'response_id': f"response_{int(time.time())}",
            'prompt': prompt,
            'response': response,
            'model': self.model_name,
            'parameters': {
                'temperature': temperature,
                'max_tokens': max_tokens
            },
            'timestamp': time.time(),
            'source': 'llm'
        }]
    
    def _self_critique_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        自我批评查询
        
        Args:
            query: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 自我批评反馈数据列表
        """
        original_response = query.get('original_response', '')
        critique_prompt = f"请对以下回答进行批评和改进：\n{original_response}"
        
        # 模拟LLM自我批评调用
        critique = f"这是对原始回答的批评。这是一个模拟的批评，实际应用中应调用真实的LLM API进行自我批评。"
        improved_response = f"这是改进后的回答。这是一个模拟的改进，实际应用中应调用真实的LLM API生成改进后的回答。"
        
        return [{
            'response_id': f"critique_{int(time.time())}",
            'original_response': original_response,
            'critique': critique,
            'improved_response': improved_response,
            'model': self.model_name,
            'timestamp': time.time(),
            'source': 'llm_self_critique'
        }]
    
    def _consistency_check_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        一致性检验查询
        
        Args:
            query: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 一致性检验反馈数据列表
        """
        prompt = query.get('prompt', '')
        num_samples = query.get('num_samples', 3)
        temperature_range = query.get('temperature_range', [0.3, 0.7, 1.0])
        
        # 模拟多次LLM调用以检查一致性
        responses = []
        for i in range(min(num_samples, len(temperature_range))):
            temp = temperature_range[i] if i < len(temperature_range) else 0.7
            responses.append(f"这是温度为{temp}的第{i+1}次采样结果。这是一个模拟的响应，实际应用中应调用真实的LLM API。")
        
        # 计算一致性得分（模拟）
        consistency_score = 0.85
        
        return [{
            'response_id': f"consistency_{int(time.time())}",
            'prompt': prompt,
            'responses': responses,
            'consistency_score': consistency_score,
            'model': self.model_name,
            'parameters': {
                'num_samples': num_samples,
                'temperature_range': temperature_range
            },
            'timestamp': time.time(),
            'source': 'llm_consistency_check'
        }]
    
    def send_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        向LLM发送反馈数据（例如用于模型微调）
        
        Args:
            feedback: 要发送的反馈数据
            
        Returns:
            bool: 发送是否成功
        """
        if not self.connection:
            self.logger.error("未连接到LLM服务，无法发送反馈")
            return False
        
        try:
            # 实现发送反馈的逻辑
            feedback_type = feedback.get('feedback_type')
            
            if feedback_type == 'rating':
                # 评分反馈
                response_id = feedback.get('response_id')
                rating = feedback.get('rating')
                self.logger.info(f"为响应 {response_id} 提供评分: {rating}")
                return True
            elif feedback_type == 'correction':
                # 纠正反馈
                response_id = feedback.get('response_id')
                correction = feedback.get('correction')
                self.logger.info(f"为响应 {response_id} 提供纠正: {correction}")
                return True
            else:
                self.logger.warning(f"不支持的反馈类型: {feedback_type}")
                return False
        except Exception as e:
            self.logger.error(f"向LLM发送反馈失败: {str(e)}")
            return False
    
    def validate_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        验证反馈数据的格式和内容是否有效
        
        Args:
            feedback: 要验证的反馈数据
            
        Returns:
            bool: 反馈数据是否有效
        """
        # 验证反馈数据的基本结构
        required_fields = ['feedback_type']
        for field in required_fields:
            if field not in feedback:
                self.logger.error(f"反馈数据缺少必要字段: {field}")
                return False
        
        # 根据反馈类型验证特定字段
        feedback_type = feedback.get('feedback_type')
        if feedback_type == 'rating':
            if 'response_id' not in feedback or 'rating' not in feedback:
                self.logger.error("评分反馈缺少必要字段: response_id 或 rating")
                return False
            rating = feedback.get('rating')
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                self.logger.error("评分必须是1到5之间的数字")
                return False
        elif feedback_type == 'correction':
            if 'response_id' not in feedback or 'correction' not in feedback:
                self.logger.error("纠正反馈缺少必要字段: response_id 或 correction")
                return False
        
        return True
    
    def transform_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        将外部格式的反馈数据转换为系统内部标准格式
        
        Args:
            feedback: 外部格式的反馈数据
            
        Returns:
            Dict[str, Any]: 转换后的标准格式反馈数据
        """
        # 转换为标准格式
        standard_feedback = {
            'id': feedback.get('id', f"llm_feedback_{id(feedback)}"),
            'source': 'llm',
            'timestamp': feedback.get('timestamp', time.time()),
            'content': feedback.get('content', {}),
            'metadata': {
                'model': self.model_name,
                'source_details': {
                    'llm_endpoint': self.llm_endpoint,
                    'query_type': feedback.get('query_type', 'unknown')
                }
            }
        }
        
        return standard_feedback