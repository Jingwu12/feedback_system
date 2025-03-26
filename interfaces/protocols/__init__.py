# -*- coding: utf-8 -*-
"""
反馈系统通信协议包

该包提供了反馈系统中使用的通信协议实现，用于规范不同反馈源之间的数据交换格式和通信方式。
支持多种数据格式，包括JSON和XML等，以适应不同场景的需求。
"""

from .base_protocol import BaseProtocol
from .json_protocol import JSONProtocol
from .xml_protocol import XMLProtocol

__all__ = [
    'BaseProtocol',
    'JSONProtocol',
    'XMLProtocol'
]