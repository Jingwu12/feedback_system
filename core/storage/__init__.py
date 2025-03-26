# -*- coding: utf-8 -*-
"""
反馈存储层模块

该模块负责存储和管理反馈信息，为系统提供持久化的反馈记忆。
"""

from .storage import FeedbackStorage, JSONFileStorage, SQLiteStorage, VersionControlStorage