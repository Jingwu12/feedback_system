# -*- coding: utf-8 -*-
"""
人类反馈适配器

该模块实现了连接人类反馈源的适配器，用于获取医疗专业人员和患者的反馈数据。
人类反馈是医疗复杂任务规划与执行系统中最重要的反馈来源之一。
"""

from typing import Any, Dict, List, Optional, Union
import json
import logging
import time

from .base_adapter import BaseAdapter

class HumanFeedbackAdapter(BaseAdapter):
    """
    人类反馈适配器，用于连接人类反馈源。
    
    该适配器实现了从医疗专业人员和患者获取反馈数据的功能，支持多种反馈形式，
    包括评分、文本评价、选择题和开放式问题等。
    """
    
    def __init__(self, logger=None):
        """
        初始化人类反馈适配器
        
        Args:
            logger: 日志记录器，如果为None则创建新的日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.connection = None
        self.feedback_interface = None
        self.user_type = None  # 'professional' 或 'patient'
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到人类反馈接口
        
        Args:
            config: 连接配置，包含反馈接口的访问地址、认证信息等
                - interface_type: 接口类型，如'web', 'app', 'api'
                - endpoint: 接口端点
                - user_type: 用户类型，'professional'或'patient'
                - timeout: 连接超时时间（秒）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            interface_type = config.get('interface_type', 'web')
            endpoint = config.get('endpoint')
            self.user_type = config.get('user_type', 'professional')
            timeout = config.get('timeout', 30)
            
            # 这里实现具体的连接逻辑，例如初始化Web接口或API客户端
            if not endpoint:
                self.logger.error("反馈接口端点未指定")
                return False
                
            self.logger.info(f"成功连接到人类反馈接口: {endpoint}, 类型: {interface_type}, 用户类型: {self.user_type}")
            self.feedback_interface = interface_type
            self.connection = True
            return True
        except Exception as e:
            self.logger.error(f"连接人类反馈接口失败: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开与人类反馈接口的连接
        
        Returns:
            bool: 断开连接是否成功
        """
        try:
            # 关闭连接的逻辑
            self.connection = None
            self.logger.info("已断开与人类反馈接口的连接")
            return True
        except Exception as e:
            self.logger.error(f"断开人类反馈接口连接失败: {str(e)}")
            return False
    
    def get_feedback(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从人类获取反馈数据
        
        Args:
            query: 查询参数，指定要获取的反馈类型和条件
                - feedback_type: 反馈类型，如'rating', 'text', 'choice', 'open'
                - question: 问题或提示
                - options: 选项列表（用于选择题）
                - context: 相关上下文信息
            
        Returns:
            List[Dict[str, Any]]: 反馈数据列表，每个反馈表示为一个字典
        """
        if not self.connection:
            self.logger.error("未连接到人类反馈接口，无法获取反馈")
            return []
        
        try:
            feedback_type = query.get('feedback_type', 'text')
            question = query.get('question', '')
            options = query.get('options', [])
            context = query.get('context', {})
            
            # 根据反馈类型执行不同的获取逻辑
            if feedback_type == 'rating':
                return self._get_rating_feedback(question, context)
            elif feedback_type == 'text':
                return self._get_text_feedback(question, context)
            elif feedback_type == 'choice':
                return self._get_choice_feedback(question, options, context)
            elif feedback_type == 'open':
                return self._get_open_feedback(question, context)
            else:
                self.logger.warning(f"不支持的反馈类型: {feedback_type}")
                return []
        except Exception as e:
            self.logger.error(f"从人类获取反馈失败: {str(e)}")
            return []
    
    def _get_rating_feedback(self, question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取评分反馈
        
        Args:
            question: 评分问题
            context: 相关上下文
            
        Returns:
            List[Dict[str, Any]]: 评分反馈数据列表
        """
        # 模拟获取评分反馈
        # 实际应用中，这里应该显示评分界面，让用户进行评分
        return [{
            'feedback_id': f"rating_{int(time.time())}",
            'question': question,
            'rating': 4.5,  # 模拟评分结果
            'user_type': self.user_type,
            'timestamp': time.time(),
            'source': 'human_feedback'
        }]
    
    def _get_text_feedback(self, question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取文本反馈
        
        Args:
            question: 文本问题
            context: 相关上下文
            
        Returns:
            List[Dict[str, Any]]: 文本反馈数据列表
        """
        # 模拟获取文本反馈
        # 实际应用中，这里应该显示文本输入界面，让用户输入反馈
        return [{
            'feedback_id': f"text_{int(time.time())}",
            'question': question,
            'text': f"这是对'{question}'的文本反馈。这是一个模拟的反馈，实际应用中应由真实用户提供。",
            'user_type': self.user_type,
            'timestamp': time.time(),
            'source': 'human_feedback'
        }]
    
    def _get_choice_feedback(self, question: str, options: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取选择题反馈
        
        Args:
            question: 选择题问题
            options: 选项列表
            context: 相关上下文
            
        Returns:
            List[Dict[str, Any]]: 选择题反馈数据列表
        """
        # 模拟获取选择题反馈
        # 实际应用中，这里应该显示选择题界面，让用户选择选项
        selected_option = options[0] if options else "无选项"
        return [{
            'feedback_id': f"choice_{int(time.time())}",
            'question': question,
            'options': options,
            'selected_option': selected_option,  # 模拟选择结果
            'user_type': self.user_type,
            'timestamp': time.time(),
            'source': 'human_feedback'
        }]
    
    def _get_open_feedback(self, question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取开放式问题反馈
        
        Args:
            question: 开放式问题
            context: 相关上下文
            
        Returns:
            List[Dict[str, Any]]: 开放式问题反馈数据列表
        """
        # 模拟获取开放式问题反馈
        # 实际应用中，这里应该显示开放式问题界面，让用户提供详细反馈
        return [{
            'feedback_id': f"open_{int(time.time())}",
            'question': question,
            'response': f"这是对开放式问题'{question}'的详细反馈。这是一个模拟的反馈，实际应用中应由真实用户提供详细的意见和建议。",
            'user_type': self.user_type,
            'timestamp': time.time(),
            'source': 'human_feedback'
        }]
    
    def send_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        向人类发送反馈数据（例如确认收到反馈或请求额外信息）
        
        Args:
            feedback: 要发送的反馈数据
            
        Returns:
            bool: 发送是否成功
        """
        if not self.connection:
            self.logger.error("未连接到人类反馈接口，无法发送反馈")
            return False
        
        try:
            # 实现发送反馈的逻辑
            feedback_type = feedback.get('feedback_type')
            
            if feedback_type == 'confirmation':
                # 发送确认信息
                message = feedback.get('message', '已收到您的反馈，谢谢！')
                self.logger.info(f"发送确认信息: {message}")
                return True
            elif feedback_type == 'follow_up':
                # 发送后续问题
                question = feedback.get('question')
                self.logger.info(f"发送后续问题: {question}")
                return True
            else:
                self.logger.warning(f"不支持的反馈类型: {feedback_type}")
                return False
        except Exception as e:
            self.logger.error(f"向人类发送反馈失败: {str(e)}")
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
        if feedback_type == 'confirmation':
            if 'message' not in feedback:
                self.logger.error("确认反馈缺少必要字段: message")
                return False
        elif feedback_type == 'follow_up':
            if 'question' not in feedback:
                self.logger.error("后续问题反馈缺少必要字段: question")
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
            'id': feedback.get('id', f"human_feedback_{id(feedback)}"),
            'source': 'human',
            'timestamp': feedback.get('timestamp', time.time()),
            'content': {
                'question': feedback.get('question', ''),
                'response': feedback.get('response', feedback.get('text', feedback.get('selected_option', ''))),
            },
            'metadata': {
                'user_type': self.user_type,
                'feedback_type': feedback.get('feedback_type', 'unknown'),
                'source_details': {
                    'interface_type': self.feedback_interface
                }
            }
        }
        
        return standard_feedback