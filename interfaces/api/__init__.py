# -*- coding: utf-8 -*-
"""
反馈系统API接口包

该包提供了反馈系统的RESTful API接口，用于与外部系统进行通信。
通过这些接口，外部系统可以获取和提交反馈数据，实现与反馈系统的集成。
"""

from .feedback_api import FeedbackAPI
from .auth import APIAuthentication

__all__ = [
    'FeedbackAPI',
    'APIAuthentication'
]