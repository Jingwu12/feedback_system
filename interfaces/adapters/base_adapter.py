# -*- coding: utf-8 -*-
"""
基础适配器接口

该模块定义了反馈系统中适配器的基础接口，用于连接不同的反馈源。
适配器模式允许系统与各种异构的反馈源进行交互，而不需要修改核心代码。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class BaseAdapter(ABC):
    """
    适配器基类，定义了所有适配器必须实现的接口方法。
    
    适配器负责将外部系统的数据格式转换为反馈系统内部的标准格式，
    并处理与外部系统的通信细节。
    """
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到外部反馈源
        
        Args:
            config: 连接配置，包含连接所需的参数
            
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        断开与外部反馈源的连接
        
        Returns:
            bool: 断开连接是否成功
        """
        pass
    
    @abstractmethod
    def get_feedback(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从外部反馈源获取反馈数据
        
        Args:
            query: 查询参数，指定要获取的反馈类型和条件
            
        Returns:
            List[Dict[str, Any]]: 反馈数据列表，每个反馈表示为一个字典
        """
        pass
    
    @abstractmethod
    def send_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        向外部反馈源发送反馈数据
        
        Args:
            feedback: 要发送的反馈数据
            
        Returns:
            bool: 发送是否成功
        """
        pass
    
    @abstractmethod
    def validate_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        验证反馈数据的格式和内容是否有效
        
        Args:
            feedback: 要验证的反馈数据
            
        Returns:
            bool: 反馈数据是否有效
        """
        pass
    
    @abstractmethod
    def transform_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        将外部反馈源的数据格式转换为系统内部标准格式
        
        Args:
            feedback: 外部格式的反馈数据
            
        Returns:
            Dict[str, Any]: 转换后的标准格式反馈数据
        """
        pass