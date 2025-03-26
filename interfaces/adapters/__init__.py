# -*- coding: utf-8 -*-
"""
反馈适配器包

该包提供了连接不同反馈源的适配器实现，包括知识图谱、大语言模型和人类反馈等。
适配器模式使系统能够与各种异构的反馈源进行交互，而不需要修改核心代码。
"""

from .base_adapter import BaseAdapter
from .kg_adapter import KnowledgeGraphAdapter
from .llm_adapter import LLMAdapter
from .human_adapter import HumanFeedbackAdapter

__all__ = [
    'BaseAdapter',
    'KnowledgeGraphAdapter',
    'LLMAdapter',
    'HumanFeedbackAdapter'
]