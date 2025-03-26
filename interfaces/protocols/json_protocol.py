# -*- coding: utf-8 -*-
"""
JSON通信协议实现

该模块实现了基于JSON格式的通信协议，用于反馈系统中的数据交换。
JSON格式具有良好的可读性和广泛的支持，适合作为反馈系统的主要数据交换格式。
"""

import json
import jsonschema
from typing import Any, Dict, List, Optional, Union

from .base_protocol import BaseProtocol

class JSONProtocol(BaseProtocol):
    """
    JSON协议实现类，基于JSON格式进行数据交换。
    
    该类实现了将反馈数据编码为JSON格式和从JSON格式解码反馈数据的功能，
    并提供了数据验证和模式定义等功能。
    """
    
    def __init__(self, schema: Dict[str, Any] = None):
        """
        初始化JSON协议
        
        Args:
            schema: JSON Schema定义，用于验证数据格式
        """
        self.schema = schema or self._default_schema()
        self.version = "1.0.0"
    
    def encode(self, data: Dict[str, Any]) -> bytes:
        """
        将数据编码为JSON字节流
        
        Args:
            data: 要编码的数据
            
        Returns:
            bytes: 编码后的JSON字节流
        """
        try:
            # 验证数据格式
            if not self.validate(data):
                raise ValueError("数据格式不符合协议规范")
            
            # 编码为JSON字节流
            json_str = json.dumps(data, ensure_ascii=False)
            return json_str.encode('utf-8')
        except Exception as e:
            raise ValueError(f"编码数据失败: {str(e)}")
    
    def decode(self, data: bytes) -> Dict[str, Any]:
        """
        将JSON字节流解码为数据
        
        Args:
            data: 要解码的JSON字节流
            
        Returns:
            Dict[str, Any]: 解码后的数据
        """
        try:
            # 解码JSON字节流
            json_str = data.decode('utf-8')
            decoded_data = json.loads(json_str)
            
            # 验证解码后的数据格式
            if not self.validate(decoded_data):
                raise ValueError("解码后的数据格式不符合协议规范")
            
            return decoded_data
        except Exception as e:
            raise ValueError(f"解码数据失败: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        验证数据是否符合协议规范
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 数据是否有效
        """
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError:
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取协议的数据模式定义
        
        Returns:
            Dict[str, Any]: 协议的JSON Schema定义
        """
        return self.schema
    
    def get_version(self) -> str:
        """
        获取协议的版本号
        
        Returns:
            str: 协议的版本号
        """
        return self.version
    
    def _default_schema(self) -> Dict[str, Any]:
        """
        获取默认的JSON Schema定义
        
        Returns:
            Dict[str, Any]: 默认的JSON Schema定义
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "source", "timestamp", "content"],
            "properties": {
                "id": {
                    "type": "string",
                    "description": "反馈的唯一标识符"
                },
                "source": {
                    "type": "string",
                    "description": "反馈的来源，如'kg', 'llm', 'human'"
                },
                "timestamp": {
                    "type": "number",
                    "description": "反馈生成的时间戳"
                },
                "content": {
                    "type": "object",
                    "description": "反馈的具体内容"
                },
                "metadata": {
                    "type": "object",
                    "description": "反馈的元数据，包含额外信息"
                }
            }
        }