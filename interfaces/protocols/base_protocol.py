# -*- coding: utf-8 -*-
"""
基础通信协议接口

该模块定义了反馈系统中通信协议的基础接口，用于规范不同反馈源之间的数据交换格式和通信方式。
通信协议是反馈系统中不同组件之间进行数据交换的标准，确保系统各部分能够无缝协作。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class BaseProtocol(ABC):
    """
    通信协议基类，定义了所有通信协议必须实现的接口方法。
    
    通信协议负责规范反馈数据的交换格式和通信方式，确保不同反馈源之间能够有效通信。
    """
    
    @abstractmethod
    def encode(self, data: Dict[str, Any]) -> bytes:
        """
        将数据编码为字节流
        
        Args:
            data: 要编码的数据
            
        Returns:
            bytes: 编码后的字节流
        """
        pass
    
    @abstractmethod
    def decode(self, data: bytes) -> Dict[str, Any]:
        """
        将字节流解码为数据
        
        Args:
            data: 要解码的字节流
            
        Returns:
            Dict[str, Any]: 解码后的数据
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        验证数据是否符合协议规范
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 数据是否有效
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取协议的数据模式定义
        
        Returns:
            Dict[str, Any]: 协议的数据模式定义
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        获取协议的版本号
        
        Returns:
            str: 协议的版本号
        """
        pass